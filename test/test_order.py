from orderbook.order import Order


def test_from_string() -> None:
    order = Order.from_string("S,100345,5103,100000,1000")
    assert order.is_buy is False
    assert order.order_id == 100345
    assert order.price == 5103
    assert order.quantity == 100000
    assert order.peak_size == 1000

    order = Order.from_string("B,1,2,3")
    assert order.is_buy is True
    assert order.order_id == 1
    assert order.price == 2
    assert order.quantity == 3
    assert order.peak_size is None


def test_fail_from_string(caplog) -> None:
    # noinspection PyTypeChecker
    order = Order.from_string(11)  # type: ignore
    assert order is None
    assert "Expected str, got 11" in caplog.text
    caplog.clear()

    order = Order.from_string("1" * 41)
    assert order is None
    assert "Input string is too long: 41" in caplog.text
    caplog.clear()

    order = Order.from_string("1,2,3,4,5,6")
    assert order is None
    assert "Expected from 4 to 5 comma-separated values: 6" in caplog.text
    caplog.clear()

    order = Order.from_string("1,2,3")
    assert order is None
    assert "Expected from 4 to 5 comma-separated values: 3" in caplog.text
    caplog.clear()

    order = Order.from_string("SS,1,2,3")
    assert order is None
    assert "Unexpected buy direction: SS" in caplog.text
    caplog.clear()

    order = Order.from_string("S,1,2.0,3")
    assert order is None
    assert "invalid literal for int() with base 10: '2.0'\n" in caplog.text
    caplog.clear()

    order = Order.from_string("B,1,2,3,")
    assert order is None
    assert "invalid literal for int() with base 10: ''\n" in caplog.text
    caplog.clear()


def test_fail_create(caplog) -> None:
    # noinspection PyTypeChecker
    order = Order.create(  # type: ignore
        is_buy="S",  # type: ignore
        order_id=-1,
        price=12345678,
        quantity="a",  # type: ignore
        peak_size=4.5,  # type: ignore
    )
    assert order is None
    assert "Unexpected is_buy: S" in caplog.text
    assert "Unexpected order_id: -1" in caplog.text
    assert "Unexpected price: 12345678" in caplog.text
    assert "Unexpected type quantity: a" in caplog.text
    assert "Unexpected type peak_size: 4.5" in caplog.text
    caplog.clear()


def test_create() -> None:
    order = Order.create(is_buy=True, order_id=1, price=2, quantity=3)
    assert order.is_buy is True
    assert order.order_id == 1
    assert order.price == 2
    assert order.quantity == 3
    assert order.peak_size is None
