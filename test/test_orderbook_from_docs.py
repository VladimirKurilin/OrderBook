from logging import DEBUG

from orderbook.book import Order, OrderBook


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
            "B,7,103,0,None filled by hidden S,(p:100,t:6,n:0)->(visible:0,m:10000,q:30000)->(Id:6). Volume 10000",
        ),
        (
            "root",
            10,
            "Peak updated: S,(p:100,t:7,n:1)->(visible:10000,m:10000,q:30000)->(Id:6)",
        ),
        ("root", 20, "Transaction: <7,3,100,10000>"),
        ("root", 20, "Transaction: <7,6,100,20000>"),
        ("root", 20, "B,7,103,0,None was completely executed"),
    ]


# def test_iceberg_order_partial_execution(caplog) -> None:
#     book = OrderBook()
#     caplog.set_level(DEBUG)
#
#     def add(data):
#         return book.add(Order.from_string(data))
#
#     assert add("B,1,99,50000") == []
#     assert add("S,2,101,20000") == []
#     assert add("B,3,100,30000,10000") == []
#     assert add("B,4,98,25500") == []
#
#     assert (
#         str(book)
#         in """
# +-----------------------------------------------------------------+
# | BUY                            | SELL                           |
# | Id       | Volume      | Price | Price | Volume      | Id       |
# +----------+-------------+-------+-------+-------------+----------+
# |         3|       10,000|    100|    101|       20,000|         2|
# |         1|       50,000|     99|       |             |          |
# |         4|       25,500|     98|       |             |          |
# +-----------------------------------------------------------------+
# """
#     )
#
#     assert str(add("S,5,15,11500")) == '[<3,5,100,11500>]'
#
#     assert (
#         str(book)
#         in """
# +-----------------------------------------------------------------+
# | BUY                            | SELL                           |
# | Id       | Volume      | Price | Price | Volume      | Id       |
# +----------+-------------+-------+-------+-------------+----------+
# |         3|        8,500|    100|    101|       20,000|         2|
# |         1|       50,000|     99|       |             |          |
# |         4|       25,500|     98|       |             |          |
# +-----------------------------------------------------------------+
# """
#     )
