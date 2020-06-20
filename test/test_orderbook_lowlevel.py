from orderbook.book import OrderBook, OrderBookRecord
from orderbook.order import Order


def test_simple_output(caplog) -> None:
    book = OrderBook()

    def add(data):
        return book.add(Order.from_string(data))

    add("B,1138,31502,7500")
    add("B,1234567890,32503,1234567890")
    add("S,6808,32505,7777")
    add("S,1234567891,32504,1234567890")
    add("S,42100,32507,3000")

    assert (
        str(book)
        in """
+-----------------------------------------------------------------+
| BUY                            | SELL                           |
| Id       | Volume      | Price | Price | Volume      | Id       |
+----------+-------------+-------+-------+-------------+----------+
|1234567890|1,234,567,890| 32,503| 32,504|1,234,567,890|1234567891|
|      1138|        7,500| 31,502| 32,505|        7,777|      6808|
|          |             |       | 32,507|        3,000|     42100|
+-----------------------------------------------------------------+
"""
    )

    book = OrderBook()
    book.add(Order.from_string("B,1,1,1"))
    book.add(Order.from_string("S,16,4,2,2"))
    book.add(Order.from_string("B,3,3,3"))
    book.add(Order.from_string("S,4,4,4"))
    assert (
        str(book)
        in """
+-----------------------------------------------------------------+
| BUY                            | SELL                           |
| Id       | Volume      | Price | Price | Volume      | Id       |
+----------+-------------+-------+-------+-------------+----------+
|         3|            3|      3|      4|            2|        16|
|         1|            1|      1|      4|            4|         4|
+-----------------------------------------------------------------+
"""
    )
    assert len(caplog.record_tuples) == 0

    book = OrderBook()
    book.add(Order(True, 1, 1, 2 ** 64))
    assert (
        str(book)
        in """
+-----------------------------------------------------------------+
| BUY                            | SELL                           |
| Id       | Volume      | Price | Price | Volume      | Id       |
+----------+-------------+-------+-------+-------------+----------+
|         1|18,446,744,073,709,551,616|      1|       |             |          |
+-----------------------------------------------------------------+
"""
    )
    assert len(caplog.record_tuples) == 1
    assert caplog.record_tuples[0] == (
        "root",
        30,
        "Order book line doesn't comply with pretty print constraints",
    )
    caplog.clear()

    assert (
        repr(book)
        in """
[[B,(p:1,t:1,n:0)->(visible:18446744073709551616,m:18446744073709551616,q:18446744073709551616)->(Id:1)], []]
"""
    )


def test_order_record_comparison() -> None:
    # buy sort by time
    left = OrderBookRecord(Order(True, 1, 1, 1), 1)
    right = OrderBookRecord(Order(True, 1, 1, 1), 2)
    assert left < right

    # sell sort by time
    left = OrderBookRecord(Order(False, 1, 1, 1), 1)
    right = OrderBookRecord(Order(False, 1, 1, 1), 2)
    assert left < right

    # buy sort by price
    left = OrderBookRecord(Order(True, 1, 2, 1), 1)
    right = OrderBookRecord(Order(True, 1, 1, 1), 2)
    assert left < right

    # buy sort by price
    left = OrderBookRecord(Order(True, 1, 1, 1), 1)
    right = OrderBookRecord(Order(True, 1, 2, 1), 2)
    assert not left < right

    # sell sort by price
    left = OrderBookRecord(Order(False, 1, 505, 1), 1)
    right = OrderBookRecord(Order(False, 1, 504, 1), 2)
    assert not left < right

    # sell sort by price
    left = OrderBookRecord(Order(False, 1, 1, 1), 1, 2)
    right = OrderBookRecord(Order(False, 1, 1, 1), 1, 1)
    assert right < left

    try:
        left = OrderBookRecord(Order(True, 1, 1, 1), 1)
        right = OrderBookRecord(Order(False, 2, 2, 2), 2)
        assert not (left < right) and not (right < left)

    except ValueError as e:
        assert e.args[0] == "Only Orders with the same is_buy value are comparable."

    try:
        left = OrderBookRecord(Order(False, 1, 1, 1), 1, 2)
        right = OrderBookRecord(Order(False, 1, 1, 1), 1, 2)
        assert not (left < right) and not (right < left)
    except ValueError as e:
        assert (
            e.args[0] == "Orders with same price and date cannot have equal priority."
        )


def test_id_uniqueness(caplog) -> None:
    book = OrderBook()

    def add(data):
        return book.add(Order.from_string(data))

    assert add("B,1138,31502,7500") == []
    assert len(book.buy) == 1 and len(book.sell) == 0

    assert add("B,1138,31502,7500") == []
    assert len(book.buy) == 1 and len(book.sell) == 0
    assert caplog.record_tuples == [
        ("root", 40, "Updating orders is prohibited: B,1138,31502,7500,None")
    ]
