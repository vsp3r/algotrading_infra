import pytest

from src.types import Exchange, Lifespan, Side, OrderStatus
from src.orderbook import Orderbook, Halfbook, Order

@pytest.fixture
def orderbook():
    # Create an Orderbook object with your desired setup for testing
    exchange = Exchange.HL
    maker_fee = 0.001
    taker_fee = 0.002
    return Orderbook(exchange, maker_fee, taker_fee)

def test_simple_inserts(orderbook):
    # Create multiple orders to insert
    msg = {"time":"2023-06-01T00:00:03.299718723","ver_num":1,"raw":{"channel":"l2Book","data":{"coin":"ETH","time":1685577602705,"levels":[[{"px":"1872.7","sz":"1.2498","n":3},{"px":"1872.4","sz":"23.592","n":2},{"px":"1872.1","sz":"22.4793","n":2},{"px":"1871.5","sz":"0.66","n":1},{"px":"1871.4","sz":"21.6611","n":2},{"px":"1870.8","sz":"1.08","n":1},{"px":"1869.4","sz":"17.8855","n":2},{"px":"1868.8","sz":"0.2","n":1},{"px":"1866.9","sz":"12.8558","n":1},{"px":"1862.4","sz":"18.0419","n":2},{"px":"1861.2","sz":"0.045","n":1},{"px":"1860.7","sz":"16.35","n":2},{"px":"1860.1","sz":"0.134","n":1},{"px":"1859.7","sz":"0.255","n":1},{"px":"1858.4","sz":"7.8361","n":1},{"px":"1857.5","sz":"8.7444","n":1},{"px":"1857.4","sz":"2.04","n":8},{"px":"1855.2","sz":"0.255","n":1},{"px":"1855.0","sz":"0.8003","n":1},{"px":"1852.0","sz":"10.0","n":1}],[{"px":"1873.3","sz":"0.5195","n":2},{"px":"1874.1","sz":"11.2992","n":2},{"px":"1875.9","sz":"6.261","n":1},{"px":"1876.2","sz":"6.2376","n":1},{"px":"1878.7","sz":"6.4375","n":1},{"px":"1879.0","sz":"6.0727","n":1},{"px":"1879.3","sz":"0.2","n":1},{"px":"1883.9","sz":"8.0363","n":1},{"px":"1884.5","sz":"9.0587","n":1},{"px":"1885.2","sz":"7.7413","n":1},{"px":"1887.3","sz":"7.7936","n":1},{"px":"1887.6","sz":"8.2943","n":1},{"px":"1888.0","sz":"8.6784","n":1},{"px":"1889.5","sz":"8.7885","n":1},{"px":"1889.7","sz":"7.7731","n":1},{"px":"1903.5","sz":"9.0125","n":1},{"px":"1905.3","sz":"9.2903","n":1},{"px":"1912.2","sz":"8.2795","n":1},{"px":"1917.7","sz":"9.0086","n":1},{"px":"1919.0","sz":"0.0727","n":1}]]}}}
    # for order in msg["raw"]['data']
    # orders = [
    #     Order(1, 100, orderbook.exchange, 5000, "GTC", "OPEN", Side.BUY),
    #     Order(2, 150, orderbook.exchange, 4800, "GTC", "OPEN", Side.BUY),
    #     Order(3, 50, orderbook.exchange, 5000, "GTC", "OPEN", Side.BUY),
    #     Order(4, 200, orderbook.exchange, 5300, "GTC", "OPEN", Side.SELL),
    #     Order(5, 75, orderbook.exchange, 5400, "GTC", "OPEN", Side.SELL),
    #     Order(6, 120, orderbook.exchange, 5100, "GTC", "OPEN", Side.SELL),
    # ]
    orders = initialize_book(msg)
    bid_list, bid_vols, bids = price_list(msg, 0)
    ask_list, ask_vols, asks = price_list(msg, 1)

    # Insert orders on both sides of the book
    for order in orders:
        orderbook.insert_order(order)

    # Check if the bid_book was updated correctly
    for price in orderbook.bid_book.levels:
        assert len(orderbook.bid_book.levels[price]) == bids[price]
        assert orderbook.bid_book.total_volumes[price] == bid_vols[price]
    assert orderbook.bid_book.prices == bid_list
    # # print(orderbook.bid_book.levels)
    # print(bids)
    # print(orderbook.bid_book.total_volumes)
    # print(bid_vols)
    # print(orderbook.bid_book.prices)
    # print(bid_list)
    
    for price in orderbook.ask_book.levels:
        assert len(orderbook.ask_book.levels[price]) == asks[price]
        assert orderbook.ask_book.total_volumes[price] == ask_vols[price]
    assert orderbook.ask_book.prices == ask_list


def price_list(msg, side):
    prices = []
    vols = {}
    num = {}
    for level in msg['raw']['data']['levels'][side]:
        px = round(float(level['px']) * 10) # should swap for some sig fig thing according to hl docs
        sz = round(float(level['sz']) * 10000) 
        n = int(level['n'])

        prices.append(px)
        vols[px] = sz
        num[px] = n

    return prices, vols, num

def initialize_book(msg):
    order_id = 0
    orders = []
    for level in msg['raw']['data']['levels'][0]:
        px = round(float(level['px']) * 10) # should swap for some sig fig thing according to hl docs
        sz = round(float(level['sz']) * 10000) 
        n = int(level['n'])

        order_id +=1 
        orders.append(Order(order_id, sz//n + sz%n, Exchange.HL, px, Lifespan.G, OrderStatus.Created, Side.B))
        sz = sz//n
        n -= 1

        for i in range(n):
            order_id +=1
            orders.append(Order(order_id, sz, Exchange.HL, px, Lifespan.G, OrderStatus.Created, Side.B))

    for level in msg['raw']['data']['levels'][1]:
        px = round(float(level['px']) * 10) # should swap for some sig fig thing according to hl docs
        sz = round(float(level['sz']) * 10000) 
        n = int(level['n'])

        order_id +=1 
        orders.append(Order(order_id, sz//n + sz%n, Exchange.HL, px, Lifespan.G, OrderStatus.Created, Side.A))
        sz = sz//n
        n -= 1

        for i in range(n):
            order_id +=1
            orders.append(Order(order_id, sz, Exchange.HL, px, Lifespan.G, OrderStatus.Created, Side.A))

    return orders


def test_cancel_order(orderbook):
    # Your cancel_order test cases here
    pass

def test_amend_order(orderbook):
    # Your amend_order test cases here
    pass