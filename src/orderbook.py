import collections
from bisect import bisect, insort_left
from typing import Any, Callable, Deque, Dict, List, Optional, Tuple, Union
import random

from .types import Exchange, Lifespan, Side, OrderStatus

# Side, 0 = sell, 1 = buy
class Order:
    """An order object"""
    __slots__ = ['order_id', 'side', 'size', 'price', 'exchange',
                  'lifespan', 'status', 'remaining', 'total_fees']
    def __init__(self, order_id: int, size: int, exchange: Exchange, price: int,
                 lifespan: Lifespan, status: OrderStatus, side: Side):
        self.order_id: int = order_id
        self.side: Side = side
        self.size: int = size
        self.price: int = price

        self.exchange: Exchange = exchange
        self.lifespan: Lifespan = lifespan
        self.status: OrderStatus = status
        self.total_fees: int = 0

        self.remaining: int = size

class Halfbook:
    """Half an orderbook"""
    def __init__(self, side: Side) -> None:
        self.side = side

        self.levels: Dict[int, Deque[Order]] = {} 
        self.total_volumes: Dict[int, int] = {}
        self.prices: List[int] = []
        # could also add traded vol @ price levels if it makes diffchecking easier later


class Orderbook:
    """Full orderbook"""
    def __init__(self, exchange: Exchange, maker_fee: float, taker_fee: float):
        self.exchange: Exchange = exchange
        self.maker_fee: float = maker_fee
        self.taker_fee: float = taker_fee
        # HL: 2.5bps taker fee
        # 0.2bps maker fee

        self.ask_book = Halfbook(Side.SELL)
        self.bid_book = Halfbook(Side.BUY)
        self.order_loc: Dict[int, Order] = {} # {order_id: order obj}

        self.best_bid = 0
        self.best_ask = 0
    # add - O(log M) for first order, O(1) for all else
    # cancel - O(1)
    # execute/match - O(1)
    # getvolume at limit - O(1)
    # get bbo - O(1)
    def insert_order(self, order: Order) -> str: 
        price = order.price
        size = order.size
        side = order.side

        book = self.bid_book if order.side == Side.B else self.ask_book

        # wonder if we can collapse this part
        # check if it crosses the spread / can match with opposing order
        #   if so, then match order
        if side == Side.SELL and self.bid_book.prices and price <= self.bid_book.prices[0]:
            # incoming order: sell at $12, qty 10
            # bids: [14, 13, 12, 11]
            # asks: [15, 16, 17, 18]
            self.match_at_bid(order)
        # array access time complexity is O(1)...
        elif side == Side.BUY and self.ask_book.prices and price >= self.ask_book.prices[0]:
            self.trade_bid(order)
        # check if price level exits, and make if needed    
        if price not in book.levels: # TODO: this search might be slow
        # append to end of deque @ pricelevel
            book.levels[price] = collections.deque()
            book.total_volumes[price] = 0
            # O(log n) search dominated by O(n) insertion
            insort_left(book.prices, price, key=lambda x: (-side) * x) #reverses list when its descending(bids)
            # NOTE: could also remove the lambda, and use bid_book.prices[-1]
        # update total vol
        book.levels[price].append(order)
        book.total_volumes[price] += size
        self.order_loc[order.order_id] = order
        
    def match_at_bid(self, order):
        best_price = order.price
        size = order.remaining
        side = order.side
        book = self.bid_book
        if book.side != side:
            print(f'{order.order_id} trying to match bid {book.prices[0]} w/ ${best_price} and {size}')
        # incoming order: sell at $12, qty 10
        # bids: [14:3, 13:4, 12:12, 11]
        # asks: [15, 16, 17, 18]
        
        # while order has size left, and best_price is less or eq to best bid
        #   get size of order at top of book
        #   calculate tradeable amt: either all of available resting, or all of remaining
        #   match those:
        #       resting order gets maker fees = notional traded * makers bps
        #       incoming order gets -taker fees = notional traded * takers bps
        #       (decrease vol at level):
        #           decrease size of both orders = to tradeable
        #           if 
        #       


        while order.remaining > 0 and book.prices and best_price <= book.prices[0]:
            px = book.prices[0]
            next_order = book.levels[px].popleft()
            # subtract from remaining: remaining or all of order size
            tradeable = order.remaining if next_order.remaining >= order.remaining else next_order.remaining
            self.match_orders(order, next_order)

    def match_at_ask(self, order):
        best_price = order.price
        size = order.remaining
        side = order.side
        book = self.bid_book
        if book.side != side:
            print(f'{order.order_id} trying to match bid {book.prices[0]} w/ ${best_price} and {size}')
        # incoming order: sell at $12, qty 10
        # bids: [14:3, 13:4, 12:12, 11]
        # asks: [15, 16, 17, 18]

        
        while order.remaining > 0 and book.prices and best_price <= book.prices[0]:
            px = book.prices[0]
            next_order = book.levels[px].popleft()
            # subtract from remaining: remaining or all of order size
            tradeable = order.remaining if next_order.remaining >= order.remaining else next_order.remaining
            self.match_orders(order, next_order)

    def remove_vol(self, volume: int, price: int, side: Side):
            book = self.bid_book if side == Side.B else self.ask_book

            book.total_volumes[price] -= volume

            if book.total_volumes[price] == 0:
                del book.levels[price]
                del book.total_volumes[price]
                book.prices.remove(price)


    def cancel_order(self, order: Order):
        self.remove_vol(order.remaining, order.price, order.side)

        del self.order_loc[order.order_id]

    
    def match_at_price(self, order):
        best_price = order.price
        size = order.size

        # {$100: 10, $110: 5, $112: 8}
        # bid at 111 for 17

        book = self.bid_book if order.side == Side.A else self.ask_book # opposite book

        # while order.remaining > 0 and book.prices and best_price >= book.prices[0]:
        

    # def match_orders(self, taker: Order, maker: Order):
        # # bids: ($101, $100, $98)
        # # maker: ($101, 7)
        # # taker: ($100, 9)
        # while taker.remaining > 0 and maker.remaining > 0:
        #     # subtract tradeable volume from both's remaining
        #     # add to their fees accordingly
        #     # remove volume accordingly

        # # whichever order dies, remove it from the book
            


    # def trade_ask(self, order: Order):
    #     price = order.price
    #     size = order.size
    #     side = order.side

    #     book = self.bid_book if order.side == Side.A else self.ask_book # opposite book of order

    #     best_bid = book.prices[0]
    #     # while order has vol and its best price 
    #     while order.remaining > 0:
    #         book.levels[]
          



    # def amend(self, order: Order, volume: int):

