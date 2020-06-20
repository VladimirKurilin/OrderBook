from logging import DEBUG

from orderbook.book import OrderBook
from orderbook.order import Order


def test_iceberg_vs_limit_partial_fill(caplog) -> None:
    book = OrderBook()
    caplog.set_level(DEBUG)

    def add(data):
        return book.add(Order.from_string(data))

    assert add("B,1,10,40,20") == []
    assert (
        str(book)
        in """
+-----------------------------------------------------------------+
| BUY                            | SELL                           |
| Id       | Volume      | Price | Price | Volume      | Id       |
+----------+-------------+-------+-------+-------------+----------+
|         1|           20|     10|       |             |          |
+-----------------------------------------------------------------+
"""
    )

    assert repr(add("S,2,10,20")) == "[<1,2,10,20>]"
    assert (
        str(book)
        in """
+-----------------------------------------------------------------+
| BUY                            | SELL                           |
| Id       | Volume      | Price | Price | Volume      | Id       |
+----------+-------------+-------+-------+-------------+----------+
|         1|           20|     10|       |             |          |
+-----------------------------------------------------------------+
"""
    )

    assert caplog.record_tuples == [
        (
            "root",
            20,
            "Record inserted: B,(p:10,t:1,n:0)->(visible:20,m:20,q:40)->(Id:1)",
        ),
        (
            "root",
            10,
            "S,2,10,0,None filled by visible B,(p:10,t:1,n:0)->(visible:0,m:20,q:20)->(Id:1). Volume 20",
        ),
        ("root", 10, "Peak updated: B,(p:10,t:2,n:0)->(visible:20,m:20,q:20)->(Id:1)"),
        ("root", 20, "Transaction: <1,2,10,20>"),
        ("root", 20, "S,2,10,0,None was completely executed"),
    ]
    caplog.clear()


def test_iceberg_vs_limit_hidden_partial_fill(caplog) -> None:
    book = OrderBook()
    caplog.set_level(DEBUG)

    def add(data):
        return book.add(Order.from_string(data))

    assert add("B,1,10,40,20") == []
    assert add("B,2,10,25,10") == []

    assert repr(add("S,3,9,45")) == "[<1,3,10,35>, <2,3,10,10>]"
    assert (
        str(book)
        in """
+-----------------------------------------------------------------+
| BUY                            | SELL                           |
| Id       | Volume      | Price | Price | Volume      | Id       |
+----------+-------------+-------+-------+-------------+----------+
|         1|            5|     10|       |             |          |
|         2|           10|     10|       |             |          |
+-----------------------------------------------------------------+
"""
    )
    assert caplog.record_tuples == [
        (
            "root",
            20,
            "Record inserted: B,(p:10,t:1,n:0)->(visible:20,m:20,q:40)->(Id:1)",
        ),
        (
            "root",
            20,
            "Record inserted: B,(p:10,t:2,n:0)->(visible:10,m:10,q:25)->(Id:2)",
        ),
        (
            "root",
            10,
            "S,3,9,25,None filled by visible B,(p:10,t:1,n:0)->(visible:0,m:20,q:20)->(Id:1). Volume 20",
        ),
        (
            "root",
            10,
            "S,3,9,15,None filled by visible B,(p:10,t:2,n:0)->(visible:0,m:10,q:15)->(Id:2). Volume 10",
        ),
        (
            "root",
            10,
            "S,3,9,0,None filled by hidden B,(p:10,t:3,n:0)->(visible:5,m:20,q:5)->(Id:1). Volume 15",
        ),
        ("root", 10, "Peak updated: B,(p:10,t:3,n:1)->(visible:10,m:10,q:15)->(Id:2)"),
        ("root", 20, "Transaction: <1,3,10,35>"),
        ("root", 20, "Transaction: <2,3,10,10>"),
        ("root", 20, "S,3,9,0,None was completely executed"),
    ]
    caplog.clear()


def test_limit_vs_iceberg_complete_fill(caplog) -> None:
    book = OrderBook()
    caplog.set_level(DEBUG)

    def add(data):
        return book.add(Order.from_string(data))

    assert add("S,1,10,40,20") == []

    assert str(add("B,2,11,45")) == "[<2,1,10,40>]"
    assert (
        str(book)
        in """
+-----------------------------------------------------------------+
| BUY                            | SELL                           |
| Id       | Volume      | Price | Price | Volume      | Id       |
+----------+-------------+-------+-------+-------------+----------+
|         2|            5|     11|       |             |          |
+-----------------------------------------------------------------+
"""
    )
    assert caplog.record_tuples == [
        (
            "root",
            20,
            "Record inserted: S,(p:10,t:1,n:0)->(visible:20,m:20,q:40)->(Id:1)",
        ),
        (
            "root",
            10,
            "B,2,11,25,None filled by visible S,(p:10,t:1,n:0)->(visible:0,m:20,q:20)->(Id:1). Volume 20",
        ),
        (
            "root",
            10,
            "B,2,11,5,None filled by hidden S,(p:10,t:2,n:0)->(visible:0,m:20,q:0)->(Id:1). Volume 20",
        ),
        ("root", 20, "Transaction: <2,1,10,40>"),
        ("root", 20, "Record inserted: B,(p:11,t:2,n:0)->(visible:5,m:5,q:5)->(Id:2)"),
    ]
    caplog.clear()


def test_simple_fill(caplog) -> None:
    book = OrderBook()
    caplog.set_level(DEBUG)

    def add(data):
        return book.add(Order.from_string(data))

    transactions = add("B,1,10,40,20")
    assert not transactions
    assert (
        str(book)
        in """
+-----------------------------------------------------------------+
| BUY                            | SELL                           |
| Id       | Volume      | Price | Price | Volume      | Id       |
+----------+-------------+-------+-------+-------------+----------+
|         1|           20|     10|       |             |          |
+-----------------------------------------------------------------+
"""
    )
    transactions = add("B,2,10,20")
    assert not transactions
    assert (
        str(book)
        in """
+-----------------------------------------------------------------+
| BUY                            | SELL                           |
| Id       | Volume      | Price | Price | Volume      | Id       |
+----------+-------------+-------+-------+-------------+----------+
|         1|           20|     10|       |             |          |
|         2|           20|     10|       |             |          |
+-----------------------------------------------------------------+
"""
    )

    transactions = add("S,3,10,10")
    assert repr(transactions) == "[<1,3,10,10>]"
    assert (
        str(book)
        in """
+-----------------------------------------------------------------+
| BUY                            | SELL                           |
| Id       | Volume      | Price | Price | Volume      | Id       |
+----------+-------------+-------+-------+-------------+----------+
|         1|           10|     10|       |             |          |
|         2|           20|     10|       |             |          |
+-----------------------------------------------------------------+
"""
    )

    transactions = add("S,4,10,1")
    assert repr(transactions) == "[<1,4,10,1>]"
    assert (
        str(book)
        in """
+-----------------------------------------------------------------+
| BUY                            | SELL                           |
| Id       | Volume      | Price | Price | Volume      | Id       |
+----------+-------------+-------+-------+-------------+----------+
|         1|            9|     10|       |             |          |
|         2|           20|     10|       |             |          |
+-----------------------------------------------------------------+
"""
    )

    transactions = add("S,5,11,100")
    assert not transactions
    assert (
        str(book)
        in """
+-----------------------------------------------------------------+
| BUY                            | SELL                           |
| Id       | Volume      | Price | Price | Volume      | Id       |
+----------+-------------+-------+-------+-------------+----------+
|         1|            9|     10|     11|          100|         5|
|         2|           20|     10|       |             |          |
+-----------------------------------------------------------------+
"""
    )

    assert caplog.record_tuples == [
        (
            "root",
            20,
            "Record inserted: B,(p:10,t:1,n:0)->(visible:20,m:20,q:40)->(Id:1)",
        ),
        (
            "root",
            20,
            "Record inserted: B,(p:10,t:2,n:0)->(visible:20,m:20,q:20)->(Id:2)",
        ),
        (
            "root",
            10,
            "S,3,10,0,None filled by visible B,(p:10,t:1,n:0)->(visible:10,m:20,q:30)->(Id:1). Volume 10",
        ),
        ("root", 20, "Transaction: <1,3,10,10>"),
        ("root", 20, "S,3,10,0,None was completely executed"),
        (
            "root",
            10,
            "S,4,10,0,None filled by visible B,(p:10,t:1,n:0)->(visible:9,m:20,q:29)->(Id:1). Volume 1",
        ),
        ("root", 20, "Transaction: <1,4,10,1>"),
        ("root", 20, "S,4,10,0,None was completely executed"),
        (
            "root",
            20,
            "Record inserted: S,(p:11,t:5,n:0)->(visible:100,m:100,q:100)->(Id:5)",
        ),
    ]
    caplog.clear()


def test_last_chunk_of_hidden_icebrg(caplog) -> None:
    book = OrderBook()
    caplog.set_level(DEBUG)

    def add(data):
        return book.add(Order.from_string(data))

    assert str(add("B,1,10,50,20")) == "[]"
    assert (
        str(book)
        in """
+-----------------------------------------------------------------+
| BUY                            | SELL                           |
| Id       | Volume      | Price | Price | Volume      | Id       |
+----------+-------------+-------+-------+-------------+----------+
|         1|           20|     10|       |             |          |
+-----------------------------------------------------------------+
"""
    )
    assert str(add("S,2,9,49,1")) == "[<1,2,10,49>]"
    assert (
        str(book)
        in """
+-----------------------------------------------------------------+
| BUY                            | SELL                           |
| Id       | Volume      | Price | Price | Volume      | Id       |
+----------+-------------+-------+-------+-------------+----------+
|         1|            1|     10|       |             |          |
+-----------------------------------------------------------------+
"""
    )

    assert str(add("S,2,9,1,1")) == "[<1,2,10,1>]"
    assert (
        str(book)
        in """
+-----------------------------------------------------------------+
| BUY                            | SELL                           |
| Id       | Volume      | Price | Price | Volume      | Id       |
+----------+-------------+-------+-------+-------------+----------+
+-----------------------------------------------------------------+
"""
    )

    assert caplog.record_tuples == [
        (
            "root",
            20,
            "Record inserted: B,(p:10,t:1,n:0)->(visible:20,m:20,q:50)->(Id:1)",
        ),
        (
            "root",
            10,
            "S,2,9,29,1 filled by visible B,(p:10,t:1,n:0)->(visible:0,m:20,q:30)->(Id:1). Volume 20",
        ),
        (
            "root",
            10,
            "S,2,9,0,1 filled by hidden B,(p:10,t:2,n:0)->(visible:1,m:20,q:1)->(Id:1). Volume 29",
        ),
        ("root", 20, "Transaction: <1,2,10,49>"),
        ("root", 20, "S,2,9,0,1 was completely executed"),
        (
            "root",
            10,
            "S,2,9,0,1 filled by visible B,(p:10,t:2,n:0)->(visible:0,m:20,q:0)->(Id:1). Volume 1",
        ),
        ("root", 20, "Transaction: <1,2,10,1>"),
        ("root", 20, "S,2,9,0,1 was completely executed"),
    ]

    assert str(add("S,2,9,50,1")) == "[]"
    assert str(add("B,3,9,11")) == "[<3,2,9,11>]"

    assert (
        str(book)
        in """
+-----------------------------------------------------------------+
| BUY                            | SELL                           |
| Id       | Volume      | Price | Price | Volume      | Id       |
+----------+-------------+-------+-------+-------------+----------+
|          |             |       |      9|            1|         2|
+-----------------------------------------------------------------+
"""
    )

    assert str(add("B,3,9,39")) == "[<3,2,9,39>]"
    assert (
        str(book)
        in """
+-----------------------------------------------------------------+
| BUY                            | SELL                           |
| Id       | Volume      | Price | Price | Volume      | Id       |
+----------+-------------+-------+-------+-------------+----------+
+-----------------------------------------------------------------+
"""
    )
