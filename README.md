# Algotrading Infra

This is an exchange simulator where clients can connect to recieve market and matching data.

The exchange performs order matching using FIFO and its own orderbook, and disseminates the information to those connected.

It is generalizable to take in any tick level market data feed, provided it is in the correct structure, and perform simulated matching on it.

Will work out of the box with Binance feeds.

### Technicals

It is comprised of a market data listener to recieve live data, a local order book, and a matching engine.

Here are brief overviews of each part of the system:

###### Local Order Book

Upon connection to a new market data feed, the system recieves an orderbook snapshot to construct the current orderbook. Subsequent market data messages will update this book.

The orderbook itself is made of 2 halfbooks (bid and ask), where each halfbook is comprised of prices, levels, and volumes @ levels.

"Levels" uses a dict (hash map) of deques (double ended queues) to store Order objects in FIFO ordering at each price level, such that a price is a key and the deque of orders is the values.

"Prices" is simply an sorted list of available prices and "Volumes" is a dict of total order sizes @ each price.

This combination of data structures allows O(1) and O(logn) time complexities for most orderbook operations
