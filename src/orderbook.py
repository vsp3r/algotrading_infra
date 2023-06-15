import collections
from typing import Dict, Deque

class Order(object):
    def __init__(self, order_id: int, side: bool, price: int, size: int):
        self.order_id = order_id
        self.side = side
        self.price = price
        self.size = size
    

class OrderBook(object):
    def __init__(self):
        self.ask_book: Dict[int, Deque[Order]] = {}
        self.bid_book: Dict[int, Deque[Order]] = {}
    
    def add_order(self, order: Order) -> None:
        # need to check if when you send an order, is there an order it can execute against? 
        # bid logic
        if order.side: #buy = true, sell = false
            if order.price not in self.bid_book:
                self.bid_book[order.price].append(Order)
        # ask logic
        else:
            if order.price not in self.ask_book:
                self.ask_book[order.price].append(Order)
    