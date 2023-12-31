import collections
from bisect import bisect, insort_left
from typing import Any, Callable, Deque, Dict, List, Optional, Tuple, Union
import random

from .types import Exchange, Lifespan, Side, OrderStatus

# Side, -1 = sell, 1 = buy
class Order:
    """An order object"""
    __slots__ = ['order_id', 'side', 'size', 'price', 'exchange',
                  'lifespan', 'status', 'remaining', 'total_fees']
    def __init__(self, order_id: int, side: Side, size: int, price: int,
                 exchange: Exchange, lifespan: Lifespan, status: OrderStatus):
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
        # NOTE: deleting obj from here still requires deleting other references
        # doesn't automatically remove from levels
        self.order_loc: Dict[int, Order] = {} # {order_id: order obj}

        self.best_bid = 0
        self.best_ask = 0
    # add - O(log M) for first order, O(1) for all else
    # cancel - O(1)
    # execute/match - O(1)
    # getvolume at limit - O(1)
    # get bbo - O(1)
    def insert_order(self, order: Order) -> str: 
        """First call to insert order into book"""
        # wonder if we can collapse this part
        # check if it crosses the spread / can match with opposing order
        #   if so, then match order
        if order.side == Side.SELL and self.bid_book.prices and order.price <= self.bid_book.prices[0]:
            # incoming order: sell at $12, qty 10
            # bids: [14, 13, 12, 11]
            # asks: [15, 16, 17, 18]
            self.match_at_bid(order)
        # array access time complexity is O(1)...
        elif order.side == Side.BUY and self.ask_book.prices and order.price >= self.ask_book.prices[0]:
            self.match_at_ask(order)
        # check if price level exits, and make if needed    

        # if we fully matched the order
        if order.remaining > 0:
            self.add_order(order)
       
        
    def add_order(self, order):
        """Adds order (or what remains of it) to book. Only called when 
        order.remaining > 0"""
        book = self.bid_book if order.side == Side.B else self.ask_book
        if order.price not in book.levels: # TODO: this search might be slow
        # append to end of deque @ pricelevel
            book.levels[order.price] = collections.deque()
            book.total_volumes[order.price] = 0
            # O(log n) search dominated by O(n) insertion
            insort_left(book.prices, order.price, key=lambda x: (-order.side) * x) #reverses list when its descending(bids)
            # NOTE: could also remove the lambda, and use bid_book.prices[-1]
        # update total vol
        book.levels[order.price].append(order)
        book.total_volumes[order.price] += order.remaining
        self.order_loc[order.order_id] = order

    def match_at_bid(self, order):
        """Matches size of order until we run out of resting bids that are >= to 
        order.price OR until order.remaining = 0"""
        best_price = order.price
        side = order.side
        book = self.bid_book
        if book.side == side:
            print(f"""ID:{order.order_id} type: {order.side} of ${best_price} and {order.remaining}, 
                  trying to match resting bid ${book.prices[0]}""")
        # incoming order: sell at $12, qty 10
        # bids: [14:3, 13:4, 12:12, 11]
        # asks: [15, 16, 17, 18]
        
        best_bid = book.prices[0]
        while order.remaining > 0 and best_price <= best_bid and book.total_volumes[best_bid] > 0:
            self.trade_at_level(order, best_bid)
            if not book.prices:
                break
            # NOTE: if slow, can take out remove_at_level in trade_at_level
            # and replace it here with prices.pop instead of prices.remove
            best_bid = book.prices[0]

    def match_at_ask(self, order):
        # in ask case: match until order.price < best_ask or order.remaining == 0
        # incoming order: buy at $16, qty 10
        # bids: [14:3, 13:4, 12:12, 11]
        # asks: [15:3, 16:12, 17:91, 18]
        best_price = order.price
        side = order.side
        book = self.ask_book
        if book.side != side:
            print(f'{order.order_id} trying to match ask {book.prices[0]} w/ ${best_price} and {order.remaining}')
        best_ask = book.prices[0]
        while order.remaining > 0 and best_price >= best_ask and book.total_volumes[best_ask] > 0:
            self.trade_at_level(order, best_ask)
            if not book.prices:
                break
            best_ask = book.prices[0]


    def trade_at_level(self, order, price_level):
        """Matches orders at a level"""
        book = self.bid_book if order.side == Side.A else self.ask_book
        # print(f'price: {price_level}, vol: {book.total_volumes[price_level]}')
        # print(f'id:{order.order_id}, price:{order.price}, size: {order.remaining}')
        order_queue = book.levels[price_level]
        while order.remaining > 0 and book.total_volumes[price_level] > 0:
            next_order = order_queue[0]
            tradeable = min(order.remaining, next_order.remaining)
            # assign fees to each
            # remove volume from both
            order.total_fees -= self.taker_fee * (tradeable * order.price)
            next_order.total_fees += self.maker_fee * (tradeable * order.price)
            order.remaining -= tradeable
            next_order.remaining -= tradeable

            if next_order.remaining == 0:
                order_queue.popleft()
            # TODO: needs more elegant solution
            if self.remove_vol(tradeable, price_level, book.side) == 0:
                break
            

    def remove_vol(self, volume: int, price: int, side: Side):
            book = self.bid_book if side == Side.B else self.ask_book

            book.total_volumes[price] -= volume

            if book.total_volumes[price] == 0:
                del book.levels[price]
                del book.total_volumes[price]
                book.prices.remove(price)
                return 0
            return 1

    def cancel_order(self, order: Order):
        if order.remaining > 0:
            self.remove_vol(order.remaining, order.price, order.side)
            
        del self.order_loc[order.order_id]
    

    # def amend(self, order: Order, volume: int):

