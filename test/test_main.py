from io import StringIO

import mock


def test_init():
    input_data = (
        "\nB,1,99,50000\n # ;sadkf;asf\nS,2,105,20000\n\n\n\n\nS,3,100,10000\n\n\nB,4,98,25500\nS,5,103,"
        "10000\n                       # ke;akef;\nS,6,100,10000\nB,7,103,30000\nS,5,98,75500,10000 "
    )

    with mock.patch("sys.stdin", new=StringIO(input_data)):
        with mock.patch("sys.stdout", new=StringIO()) as output_data:
            from orderbook import __main__ as module

            with mock.patch.object(module, "__name__", "__main__"):
                assert module
                module.run()

                assert (
                    output_data.getvalue()
                    in """
+-----------------------------------------------------------------+
| BUY                            | SELL                           |
| Id       | Volume      | Price | Price | Volume      | Id       |
+----------+-------------+-------+-------+-------------+----------+
|         1|       50,000|     99|       |             |          |
+-----------------------------------------------------------------+
+-----------------------------------------------------------------+
| BUY                            | SELL                           |
| Id       | Volume      | Price | Price | Volume      | Id       |
+----------+-------------+-------+-------+-------------+----------+
|         1|       50,000|     99|    105|       20,000|         2|
+-----------------------------------------------------------------+
+-----------------------------------------------------------------+
| BUY                            | SELL                           |
| Id       | Volume      | Price | Price | Volume      | Id       |
+----------+-------------+-------+-------+-------------+----------+
|         1|       50,000|     99|    100|       10,000|         3|
|          |             |       |    105|       20,000|         2|
+-----------------------------------------------------------------+
+-----------------------------------------------------------------+
| BUY                            | SELL                           |
| Id       | Volume      | Price | Price | Volume      | Id       |
+----------+-------------+-------+-------+-------------+----------+
|         1|       50,000|     99|    100|       10,000|         3|
|         4|       25,500|     98|    105|       20,000|         2|
+-----------------------------------------------------------------+
+-----------------------------------------------------------------+
| BUY                            | SELL                           |
| Id       | Volume      | Price | Price | Volume      | Id       |
+----------+-------------+-------+-------+-------------+----------+
|         1|       50,000|     99|    100|       10,000|         3|
|         4|       25,500|     98|    103|       10,000|         5|
|          |             |       |    105|       20,000|         2|
+-----------------------------------------------------------------+
+-----------------------------------------------------------------+
| BUY                            | SELL                           |
| Id       | Volume      | Price | Price | Volume      | Id       |
+----------+-------------+-------+-------+-------------+----------+
|         1|       50,000|     99|    100|       10,000|         3|
|         4|       25,500|     98|    100|       10,000|         6|
|          |             |       |    103|       10,000|         5|
|          |             |       |    105|       20,000|         2|
+-----------------------------------------------------------------+
7,3,100,10000
7,6,100,10000
7,5,103,10000
+-----------------------------------------------------------------+
| BUY                            | SELL                           |
| Id       | Volume      | Price | Price | Volume      | Id       |
+----------+-------------+-------+-------+-------------+----------+
|         1|       50,000|     99|    105|       20,000|         2|
|         4|       25,500|     98|       |             |          |
+-----------------------------------------------------------------+
1,5,99,50000
4,5,98,25500
+-----------------------------------------------------------------+
| BUY                            | SELL                           |
| Id       | Volume      | Price | Price | Volume      | Id       |
+----------+-------------+-------+-------+-------------+----------+
|          |             |       |    105|       20,000|         2|
+-----------------------------------------------------------------+
"""
                )


def test_two_icebergs_buy() -> None:
    input_lines = ["B,1,10,20,1", "B,2,9,20,3", "S,3,9,22"]
    with mock.patch("sys.stdin", new=StringIO("\n".join(input_lines))):
        with mock.patch("sys.stdout", new=StringIO()) as output_data:
            from orderbook import __main__ as module

            with mock.patch.object(module, "__name__", "__main__"):
                assert module
                module.run()

                assert (
                    output_data.getvalue()
                    in """
+-----------------------------------------------------------------+
| BUY                            | SELL                           |
| Id       | Volume      | Price | Price | Volume      | Id       |
+----------+-------------+-------+-------+-------------+----------+
|         1|            1|     10|       |             |          |
+-----------------------------------------------------------------+
+-----------------------------------------------------------------+
| BUY                            | SELL                           |
| Id       | Volume      | Price | Price | Volume      | Id       |
+----------+-------------+-------+-------+-------------+----------+
|         1|            1|     10|       |             |          |
|         2|            3|      9|       |             |          |
+-----------------------------------------------------------------+
1,3,10,20
2,3,9,2
+-----------------------------------------------------------------+
| BUY                            | SELL                           |
| Id       | Volume      | Price | Price | Volume      | Id       |
+----------+-------------+-------+-------+-------------+----------+
|         2|            1|      9|       |             |          |
+-----------------------------------------------------------------+

"""
                )


def test_two_icebergs_sell() -> None:
    input_lines = ["S,1,10,20,1", "S,2,10,21,10", "B,3,10,39"]

    with mock.patch("sys.stdin", new=StringIO("\n".join(input_lines))):
        with mock.patch("sys.stdout", new=StringIO()) as output_data:
            from orderbook import __main__ as module

            with mock.patch.object(module, "__name__", "__main__"):
                assert module
                module.run()

                assert (
                    output_data.getvalue()
                    in """
+-----------------------------------------------------------------+
| BUY                            | SELL                           |
| Id       | Volume      | Price | Price | Volume      | Id       |
+----------+-------------+-------+-------+-------------+----------+
|          |             |       |     10|            1|         1|
+-----------------------------------------------------------------+
+-----------------------------------------------------------------+
| BUY                            | SELL                           |
| Id       | Volume      | Price | Price | Volume      | Id       |
+----------+-------------+-------+-------+-------------+----------+
|          |             |       |     10|            1|         1|
|          |             |       |     10|           10|         2|
+-----------------------------------------------------------------+
3,1,10,20
3,2,10,19
+-----------------------------------------------------------------+
| BUY                            | SELL                           |
| Id       | Volume      | Price | Price | Volume      | Id       |
+----------+-------------+-------+-------+-------------+----------+
|          |             |       |     10|            1|         2|
+-----------------------------------------------------------------+

"""
                )
