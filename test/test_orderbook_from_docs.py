from logging import DEBUG

from orderbook.book import OrderBook
from orderbook.order import Order


def test_order_tranching(caplog) -> None:
    book = OrderBook()
    caplog.set_level(DEBUG)

    def add(data):
        return book.add(Order.from_string(data))

    assert add("B,1,99,50000") == []
    assert add("S,2,105,20000") == []
    assert add("S,3,100,10000") == []
    assert add("B,4,98,25500") == []
    assert add("S,5,103,10000") == []
    assert add("S,6,100,10000") == []

    assert (
        str(book)
        in """
+-----------------------------------------------------------------+
| BUY                            | SELL                           |
| Id       | Volume      | Price | Price | Volume      | Id       |
+----------+-------------+-------+-------+-------------+----------+
|         1|       50,000|     99|    100|       10,000|         3|
|         4|       25,500|     98|    100|       10,000|         6|
|          |             |       |    103|       10,000|         5|
|          |             |       |    105|       20,000|         2|
+-----------------------------------------------------------------+
"""
    )

    assert (
        str(add("B,7,103,30000"))
        == "[<7,3,100,10000>, <7,6,100,10000>, <7,5,103,10000>]"
    )
    assert (
        str(book)
        in """
+-----------------------------------------------------------------+
| BUY                            | SELL                           |
| Id       | Volume      | Price | Price | Volume      | Id       |
+----------+-------------+-------+-------+-------------+----------+
|         1|       50,000|     99|    105|       20,000|         2|
|         4|       25,500|     98|       |             |          |
+-----------------------------------------------------------------+
"""
    )

    assert str(add("S,8,100,10000")) == "[]"
    assert (
        str(book)
        in """
+-----------------------------------------------------------------+
| BUY                            | SELL                           |
| Id       | Volume      | Price | Price | Volume      | Id       |
+----------+-------------+-------+-------+-------------+----------+
|         1|       50,000|     99|    100|       10,000|         8|
|         4|       25,500|     98|    105|       20,000|         2|
+-----------------------------------------------------------------+
"""
    )

    assert caplog.record_tuples == [
        (
            "root",
            20,
            "Record inserted: B,(p:99,t:1,n:0)->(visible:50000,m:50000,q:50000)->(Id:1)",
        ),
        (
            "root",
            20,
            "Record inserted: S,(p:105,t:2,n:0)->(visible:20000,m:20000,q:20000)->(Id:2)",
        ),
        (
            "root",
            20,
            "Record inserted: S,(p:100,t:3,n:0)->(visible:10000,m:10000,q:10000)->(Id:3)",
        ),
        (
            "root",
            20,
            "Record inserted: B,(p:98,t:4,n:0)->(visible:25500,m:25500,q:25500)->(Id:4)",
        ),
        (
            "root",
            20,
            "Record inserted: S,(p:103,t:5,n:0)->(visible:10000,m:10000,q:10000)->(Id:5)",
        ),
        (
            "root",
            20,
            "Record inserted: S,(p:100,t:6,n:0)->(visible:10000,m:10000,q:10000)->(Id:6)",
        ),
        (
            "root",
            10,
            "B,7,103,20000,None filled by visible S,(p:100,t:3,n:0)->(visible:0,m:10000,q:0)->(Id:3). Volume 10000",
        ),
        (
            "root",
            10,
            "B,7,103,10000,None filled by visible S,(p:100,t:6,n:0)->(visible:0,m:10000,q:0)->(Id:6). Volume 10000",
        ),
        (
            "root",
            10,
            "B,7,103,0,None filled by visible S,(p:103,t:5,n:0)->(visible:0,m:10000,q:0)->(Id:5). Volume 10000",
        ),
        ("root", 20, "Transaction: <7,3,100,10000>"),
        ("root", 20, "Transaction: <7,6,100,10000>"),
        ("root", 20, "Transaction: <7,5,103,10000>"),
        ("root", 20, "B,7,103,0,None was completely executed"),
        (
            "root",
            20,
            "Record inserted: S,(p:100,t:8,n:0)->(visible:10000,m:10000,q:10000)->(Id:8)",
        ),
    ]


def test_iceberg_order(caplog) -> None:
    book = OrderBook()
    caplog.set_level(DEBUG)

    def add(data):
        return book.add(Order.from_string(data))

    assert add("B,1,99,50000") == []
    assert add("S,2,105,20000") == []
    assert add("S,3,100,10000") == []
    assert add("B,4,98,25500") == []
    assert add("S,5,103,10000") == []
    assert add("S,6,100,50000,10000") == []

    assert (
        str(book)
        in """
+-----------------------------------------------------------------+
| BUY                            | SELL                           |
| Id       | Volume      | Price | Price | Volume      | Id       |
+----------+-------------+-------+-------+-------------+----------+
|         1|       50,000|     99|    100|       10,000|         3|
|         4|       25,500|     98|    100|       10,000|         6|
|          |             |       |    103|       10,000|         5|
|          |             |       |    105|       20,000|         2|
+-----------------------------------------------------------------+
"""
    )

    assert str(add("B,7,103,30000")) == "[<7,3,100,10000>, <7,6,100,20000>]"
    assert (
        str(book)
        in """
+-----------------------------------------------------------------+
| BUY                            | SELL                           |
| Id       | Volume      | Price | Price | Volume      | Id       |
+----------+-------------+-------+-------+-------------+----------+
|         1|       50,000|     99|    100|       10,000|         6|
|         4|       25,500|     98|    103|       10,000|         5|
|          |             |       |    105|       20,000|         2|
+-----------------------------------------------------------------+
"""
    )

    assert caplog.record_tuples == [
        (
            "root",
            20,
            "Record inserted: B,(p:99,t:1,n:0)->(visible:50000,m:50000,q:50000)->(Id:1)",
        ),
        (
            "root",
            20,
            "Record inserted: S,(p:105,t:2,n:0)->(visible:20000,m:20000,q:20000)->(Id:2)",
        ),
        (
            "root",
            20,
            "Record inserted: S,(p:100,t:3,n:0)->(visible:10000,m:10000,q:10000)->(Id:3)",
        ),
        (
            "root",
            20,
            "Record inserted: B,(p:98,t:4,n:0)->(visible:25500,m:25500,q:25500)->(Id:4)",
        ),
        (
            "root",
            20,
            "Record inserted: S,(p:103,t:5,n:0)->(visible:10000,m:10000,q:10000)->(Id:5)",
        ),
        (
            "root",
            20,
            "Record inserted: S,(p:100,t:6,n:0)->(visible:10000,m:10000,q:50000)->(Id:6)",
        ),
        (
            "root",
            10,
            "B,7,103,20000,None filled by visible S,(p:100,t:3,n:0)->(visible:0,m:10000,q:0)->(Id:3). Volume 10000",
        ),
        (
            "root",
            10,
            "B,7,103,10000,None filled by visible S,(p:100,t:6,n:0)->(visible:0,m:10000,q:40000)->(Id:6). Volume 10000",
        ),
        (
            "root",
            10,
            "B,7,103,0,None filled by hidden S,(p:100,t:7,n:0)->(visible:10000,m:10000,q:30000)->(Id:6). Volume 10000",
        ),
        ("root", 20, "Transaction: <7,3,100,10000>"),
        ("root", 20, "Transaction: <7,6,100,20000>"),
        ("root", 20, "B,7,103,0,None was completely executed"),
    ]


def test_iceberg_order_partial_execution(caplog) -> None:
    book = OrderBook()
    caplog.set_level(DEBUG)

    def add(data):
        return book.add(Order.from_string(data))

    assert add("B,1,99,50000") == []
    assert add("S,2,101,20000") == []
    assert add("B,3,100,30000,10000") == []
    assert add("B,4,98,25500") == []

    assert (
        str(book)
        in """
+-----------------------------------------------------------------+
| BUY                            | SELL                           |
| Id       | Volume      | Price | Price | Volume      | Id       |
+----------+-------------+-------+-------+-------------+----------+
|         3|       10,000|    100|    101|       20,000|         2|
|         1|       50,000|     99|       |             |          |
|         4|       25,500|     98|       |             |          |
+-----------------------------------------------------------------+
"""
    )

    assert str(add("S,5,15,11500")) == "[<3,5,100,11500>]"

    assert (
        str(book)
        in """
+-----------------------------------------------------------------+
| BUY                            | SELL                           |
| Id       | Volume      | Price | Price | Volume      | Id       |
+----------+-------------+-------+-------+-------------+----------+
|         3|        8,500|    100|    101|       20,000|         2|
|         1|       50,000|     99|       |             |          |
|         4|       25,500|     98|       |             |          |
+-----------------------------------------------------------------+
"""
    )


def test_aggressive_iceberg_order_entry(caplog) -> None:
    book = OrderBook()
    caplog.set_level(DEBUG)

    def add(data):
        return book.add(Order.from_string(data))

    assert add("S,1,101,20000") == []
    assert add("B,2,99,50000") == []
    assert add("S,3,100,10000") == []
    assert add("S,4,100,7500") == []
    assert add("B,5,98,25500") == []

    assert (
        str(book)
        in """
+-----------------------------------------------------------------+
| BUY                            | SELL                           |
| Id       | Volume      | Price | Price | Volume      | Id       |
+----------+-------------+-------+-------+-------------+----------+
|         2|       50,000|     99|    100|       10,000|         3|
|         5|       25,500|     98|    100|        7,500|         4|
|          |             |       |    101|       20,000|         1|
+-----------------------------------------------------------------+
"""
    )

    assert str(add("B,6,100,100000,10000")) == "[<6,3,100,10000>, <6,4,100,7500>]"
    assert (
        str(book)
        in """
+-----------------------------------------------------------------+
| BUY                            | SELL                           |
| Id       | Volume      | Price | Price | Volume      | Id       |
+----------+-------------+-------+-------+-------------+----------+
|         6|       10,000|    100|    101|       20,000|         1|
|         2|       50,000|     99|       |             |          |
|         5|       25,500|     98|       |             |          |
+-----------------------------------------------------------------+
"""
    )

    assert str(add("S,7,90,10000")) == "[<6,7,100,10000>]"
    assert (
        str(book)
        in """
+-----------------------------------------------------------------+
| BUY                            | SELL                           |
| Id       | Volume      | Price | Price | Volume      | Id       |
+----------+-------------+-------+-------+-------------+----------+
|         6|       10,000|    100|    101|       20,000|         1|
|         2|       50,000|     99|       |             |          |
|         5|       25,500|     98|       |             |          |
+-----------------------------------------------------------------+
"""
    )

    assert str(add("S,8,90,11000")) == "[<6,8,100,11000>]"
    assert (
        str(book)
        in """
+-----------------------------------------------------------------+
| BUY                            | SELL                           |
| Id       | Volume      | Price | Price | Volume      | Id       |
+----------+-------------+-------+-------+-------------+----------+
|         6|        9,000|    100|    101|       20,000|         1|
|         2|       50,000|     99|       |             |          |
|         5|       25,500|     98|       |             |          |
+-----------------------------------------------------------------+
"""
    )

    assert str(add("B,9,100,50000,20000")) == "[]"
    assert (
        str(book)
        in """
+-----------------------------------------------------------------+
| BUY                            | SELL                           |
| Id       | Volume      | Price | Price | Volume      | Id       |
+----------+-------------+-------+-------+-------------+----------+
|         6|        9,000|    100|    101|       20,000|         1|
|         9|       20,000|    100|       |             |          |
|         2|       50,000|     99|       |             |          |
|         5|       25,500|     98|       |             |          |
+-----------------------------------------------------------------+
"""
    )

    assert str(add("S,10,90,35000")) == "[<6,10,100,15000>, <9,10,100,20000>]"
    assert (
        str(book)
        in """
+-----------------------------------------------------------------+
| BUY                            | SELL                           |
| Id       | Volume      | Price | Price | Volume      | Id       |
+----------+-------------+-------+-------+-------------+----------+
|         6|        4,000|    100|    101|       20,000|         1|
|         9|       20,000|    100|       |             |          |
|         2|       50,000|     99|       |             |          |
|         5|       25,500|     98|       |             |          |
+-----------------------------------------------------------------+
"""
    )
    assert caplog.record_tuples == [
        (
            "root",
            20,
            "Record inserted: S,(p:101,t:1,n:0)->(visible:20000,m:20000,q:20000)->(Id:1)",
        ),
        (
            "root",
            20,
            "Record inserted: B,(p:99,t:2,n:0)->(visible:50000,m:50000,q:50000)->(Id:2)",
        ),
        (
            "root",
            20,
            "Record inserted: S,(p:100,t:3,n:0)->(visible:10000,m:10000,q:10000)->(Id:3)",
        ),
        (
            "root",
            20,
            "Record inserted: S,(p:100,t:4,n:0)->(visible:7500,m:7500,q:7500)->(Id:4)",
        ),
        (
            "root",
            20,
            "Record inserted: B,(p:98,t:5,n:0)->(visible:25500,m:25500,q:25500)->(Id:5)",
        ),
        (
            "root",
            10,
            "B,6,100,90000,10000 filled by visible S,(p:100,t:3,n:0)->(visible:0,m:10000,q:0)->(Id:3). Volume 10000",
        ),
        (
            "root",
            10,
            "B,6,100,82500,10000 filled by visible S,(p:100,t:4,n:0)->(visible:0,m:7500,q:0)->(Id:4). Volume 7500",
        ),
        ("root", 20, "Transaction: <6,3,100,10000>"),
        ("root", 20, "Transaction: <6,4,100,7500>"),
        (
            "root",
            20,
            "Record inserted: B,(p:100,t:6,n:0)->(visible:10000,m:10000,q:82500)->(Id:6)",
        ),
        (
            "root",
            10,
            "S,7,90,0,None filled by visible B,(p:100,t:6,n:0)->(visible:0,m:10000,q:72500)->(Id:6). Volume 10000",
        ),
        (
            "root",
            10,
            "Peak updated: B,(p:100,t:7,n:0)->(visible:10000,m:10000,q:72500)->(Id:6)",
        ),
        ("root", 20, "Transaction: <6,7,100,10000>"),
        ("root", 20, "S,7,90,0,None was completely executed"),
        (
            "root",
            10,
            "S,8,90,1000,None filled by visible B,(p:100,t:7,n:0)->(visible:0,m:10000,q:62500)->(Id:6). Volume 10000",
        ),
        (
            "root",
            10,
            "S,8,90,0,None filled by hidden B,(p:100,t:8,n:0)->(visible:9000,m:10000,q:61500)->(Id:6). Volume 1000",
        ),
        ("root", 20, "Transaction: <6,8,100,11000>"),
        ("root", 20, "S,8,90,0,None was completely executed"),
        (
            "root",
            20,
            "Record inserted: B,(p:100,t:9,n:0)->(visible:20000,m:20000,q:50000)->(Id:9)",
        ),
        (
            "root",
            10,
            "S,10,90,26000,None filled by visible B,(p:100,t:8,n:0)->(visible:0,m:10000,q:52500)->(Id:6). Volume 9000",
        ),
        (
            "root",
            10,
            "S,10,90,6000,None filled by visible B,(p:100,t:9,n:0)->(visible:0,m:20000,q:30000)->(Id:9). Volume 20000",
        ),
        (
            "root",
            10,
            "S,10,90,0,None filled by hidden B,(p:100,t:10,n:0)->(visible:4000,m:10000,q:46500)->(Id:6). Volume 6000",
        ),
        (
            "root",
            10,
            "Peak updated: B,(p:100,t:10,n:1)->(visible:20000,m:20000,q:30000)->(Id:9)",
        ),
        ("root", 20, "Transaction: <6,10,100,15000>"),
        ("root", 20, "Transaction: <9,10,100,20000>"),
        ("root", 20, "S,10,90,0,None was completely executed"),
    ]
