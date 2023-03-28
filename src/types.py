import enum

class Exchange(enum.IntEnum):
    HL = 0
    BINANCE = 1

class Side(enum.IntEnum):
    SELL = -1
    BUY = 1
    ASK = SELL
    BID = BUY
    A = SELL
    B = BUY
    Bid = B
    Ask = A

class Lifespan(enum.IntEnum):
    FILL_AND_KILL = 0  # Fill and kill orders trade immediately if possible, otherwise they are cancelled
    GOOD_FOR_DAY = 1  # Good for day orders remain in the market until they trade or are explicitly cancelled
    IMMEDIATE_OR_CANCEL = FILL_AND_KILL
    LIMIT_ORDER = GOOD_FOR_DAY
    FAK = FILL_AND_KILL
    GFD = GOOD_FOR_DAY
    F = FILL_AND_KILL
    G = GOOD_FOR_DAY

class OrderStatus(enum.IntEnum):
    Uninitialized = 0
    Created = 1
    Filled = 2
    PartiallyFilled = 3
    U = Uninitialized
    C = Created
    P = PartiallyFilled
    F = Filled
