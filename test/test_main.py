import mock


def test_init():
    from orderbook import __main__ as module

    with mock.patch.object(module, "__name__", "__main__"):
        module.init()
