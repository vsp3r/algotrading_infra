#include <stdio.h>
#include <strings.h>
#include <stdlib.h>
#include "engine.h"


/* Enable/disable optimizations */
#define UNROLL_STRCPY

#define MAX_NUM_ORDERS 1010000

// #define DEBUG        (enable/disable debugging)
#ifdef DEBUG
#define ASSERT(c) do {                                                  \
  if (!(c)) { fprintf(stderr, "ASSERT failure at line %d\n", __LINE__); \
    exit(1); }} while(0)
#else
#define ASSERT(c)
#endif

#ifdef UNROLL_STRCPY
#define COPY_STRING(dst, src) do {		         \
  dst[0] = src[0]; dst[1] = src[1]; dst[2] = src[2];     \
  dst[3] = src[3]; /* dst[4] = src[4]; */		 \
} while(0)
#else
#include <string.h>
#define COPY_STRING(dst, src) strcpy(dst, src)
#endif


/* struct orderBookEntry: describes a single outstanding limit order
   (Buy or Sell). */
typedef struct orderBookEntry {
  t_size size;                     /* Order size                        */
  struct orderBookEntry *next;     /* Next entry in the pricePoint list */
  char trader[4];
} orderBookEntry_t;


/* struct pricePoint: describes a single price point in the limit order book. */
typedef struct pricePoint {
  orderBookEntry_t *listHead;
  orderBookEntry_t *listTail;
} pricePoint_t;


/** Global state ***/

/* An array of pricePoint structures representing the entire limit order book */
static pricePoint_t pricePoints[MAX_PRICE + 1];

static t_orderid curOrderID;          /* Monotonically-increasing orderID */
static unsigned int askMin;           /* Minimum Ask price    */
static unsigned int bidMax;           /* Maximum Bid price    */

/* Statically-allocated memory arena for order book entries. This data 
   structure allows us to avoid the overhead of heap-based memory allocation. */
static orderBookEntry_t arenaBookEntries[MAX_NUM_ORDERS];

static orderBookEntry_t *arenaPtr;

#define ALLOC_BOOK_ENTRY(id)

void init() {
  /* Initialize the price point array */
  bzero(pricePoints, (MAX_PRICE + 1) * sizeof(pricePoint_t));  

  /* Initialize the memory arena */
  bzero(arenaBookEntries, MAX_NUM_ORDERS * sizeof(orderBookEntry_t));
  arenaPtr = arenaBookEntries;   // Bring the arena pointer into the cache

  curOrderID = 0;
  askMin = MAX_PRICE + 1;
  bidMax = MIN_PRICE - 1;
}


void destroy() { }


/* Insert a new order book entry at the tail of the price point list */
void ppInsertOrder(pricePoint_t *ppEntry, orderBookEntry_t *entry) {
  if (ppEntry->listHead != NULL)
    ppEntry->listTail->next = entry;
  else
    ppEntry->listHead = entry;
  ppEntry->listTail = entry;
}


/* Report trade execution */
void EXECUTE_TRADE(const char *symbol, const char *buyTrader,
		   const char *sellTrader, t_price tradePrice, 
		   t_size tradeSize) {
  t_execution exec;

  if (tradeSize == 0)    /* Skip orders that have been cancelled */
    return;

  COPY_STRING(exec.symbol, symbol);

  exec.price = tradePrice;
  exec.size = tradeSize;
 
  exec.side = 0;
  COPY_STRING(exec.trader, buyTrader);
  exec.trader[4] = '\0';
  execution(exec);                  /* Report the buy-side trade */

  exec.side = 1;
  COPY_STRING(exec.trader, sellTrader);
  exec.trader[4] = '\0';
  execution(exec);                  /* Report the sell-side trade */
}


/* Process an incoming limit order */
t_orderid limit(t_order order) {
  orderBookEntry_t *bookEntry;
  orderBookEntry_t *entry;
  pricePoint_t *ppEntry;
  t_price price = order.price;
  t_size orderSize = order.size;

  if (order.side == 0) {          /* Buy order */
    /* Look for outstanding sell orders that cross with the incoming order */
    if (price >= askMin) {
      ppEntry = pricePoints + askMin;
      do {
	bookEntry = ppEntry->listHead;
	while(bookEntry != NULL) {
	  if (bookEntry->size < orderSize) {
	    EXECUTE_TRADE(order.symbol, order.trader, 
			  bookEntry->trader, price, bookEntry->size);
	    orderSize -= bookEntry->size;
	    bookEntry = bookEntry->next;
	    
	  } else {
	    EXECUTE_TRADE(order.symbol, order.trader, 
			  bookEntry->trader, price, orderSize);
	    if (bookEntry->size > orderSize)
	      bookEntry->size -= orderSize;
	    else
	      bookEntry = bookEntry->next;
	    
	    ppEntry->listHead = bookEntry;
	    return ++curOrderID;
	  }
	}
	
	/* We have exhausted all orders at the askMin price point. Move on to 
	   the next price level. */
	ppEntry->listHead = NULL;
	ppEntry++;
	askMin++;
      } while(price >= askMin);
    }

    entry =  arenaBookEntries + (++curOrderID);
    entry->size = orderSize;
    COPY_STRING(entry->trader, order.trader); 
    ppInsertOrder(&pricePoints[price], entry);
    if (bidMax < price)
      bidMax = price;
    return curOrderID;
  
  } else {                     /* Sell order */
    /* Look for outstanding Buy orders that cross with the incoming order */
    if (price <= bidMax) {
      ppEntry = pricePoints + bidMax;
      do {
	bookEntry = ppEntry->listHead;
	while(bookEntry != NULL) {
	  if (bookEntry->size < orderSize) {
	    EXECUTE_TRADE(order.symbol, bookEntry->trader, 
			  order.trader, price, bookEntry->size);
	    orderSize -= bookEntry->size;
	    bookEntry = bookEntry->next;
	    
	  } else {
	    EXECUTE_TRADE(order.symbol, bookEntry->trader, 		      
			  order.trader,price, orderSize);
	    if (bookEntry->size > orderSize)
	      bookEntry->size -= orderSize;
	    else
	      bookEntry = bookEntry->next;
	    
	    ppEntry->listHead = bookEntry;
	  return ++curOrderID;
	  }
	}

	/* We have exhausted all orders at the bidMax price point. Move on to 
	   the next price level. */
	ppEntry->listHead = NULL;
	ppEntry--;
	bidMax--;
      } while (price <= bidMax);
    }

    entry =  arenaBookEntries + (++curOrderID);
    entry->size = orderSize;       
    COPY_STRING(entry->trader, order.trader);
    ppInsertOrder(&pricePoints[price], entry);
    if (askMin > price)
      askMin = price;
    return curOrderID;
  }
}


/* Cancel an outstanding order */
void cancel(t_orderid orderid) {
  arenaBookEntries[orderid].size = 0;
}