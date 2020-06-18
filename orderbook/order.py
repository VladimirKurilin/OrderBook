import logging
from typing import Optional


class Order:
    is_buy: bool
    order_id: int
    price: int
    quantity: int
    peak_size: Optional[int]
    __logger: logging.Logger

    def __init__(
        self,
        is_buy: bool,
        order_id: int,
        price: int,
        quantity: int,
        peak_size: Optional[int] = None,
        logger: logging.Logger = logging.getLogger(),
    ):
        self.is_buy = is_buy
        self.order_id = order_id
        self.price = price
        self.quantity = quantity
        self.peak_size = peak_size
        self.__logger = logger

    def __repr__(self):
        return ",".join(
            map(
                str,
                (
                    "B" if self.is_buy else "S",
                    self.order_id,
                    self.price,
                    self.quantity,
                    self.peak_size,
                ),
            )
        )

    def __str__(self):
        return repr(self)

    @classmethod
    def create(
        cls,
        is_buy: bool = None,
        order_id: int = None,
        price: int = None,
        quantity: int = None,
        peak_size: int = None,
        logger_name=None,
    ):

        logger = logging.getLogger(logger_name)
        ok = True

        if is_buy and not isinstance(is_buy, bool):
            logger.error(f"Unexpected is_buy: {is_buy}")
            ok = False

        def check_int(value, name, min, max):
            if value is None:
                return None, True
            if not isinstance(value, int):
                logger.error(f"Unexpected type {name}: {value}")
                return None, False
            if value and (value <= min or value > max):
                logger.error(f"Unexpected {name}: {value}")
                return None, False
            return value, True

        order_id, tmp_ok = check_int(order_id, "order_id", 0, 2 ** 31 - 1)
        ok = ok and tmp_ok

        price, tmp_ok = check_int(price, "price", 0, 2 ** 15 - 1)
        ok = ok and tmp_ok

        quantity, tmp_ok = check_int(quantity, "quantity", 0, 2 ** 31 - 1)
        ok = ok and tmp_ok

        peak_size, tmp_ok = check_int(peak_size, "peak_size", 0, 2 ** 31 - 1)
        ok = ok and tmp_ok

        if (
            not ok
            or is_buy is None
            or order_id is None
            or price is None
            or quantity is None
        ):
            return None

        return cls(is_buy, order_id, price, quantity, peak_size, logger)

    @classmethod
    def from_string(cls, data: str, logger_name=None):
        logger = logging.getLogger(logger_name)
        if not isinstance(data, str):
            logger.error(f"Expected str, got {data}")
            return None

        if len(data) > 40:
            logger.error(f"Input string is too long: {len(data)}")
            return None

        tokens = data.split(",")
        if len(tokens) < 4 or len(tokens) > 5:
            logger.error(f"Expected from 4 to 5 comma-separated values: {len(tokens)}")
            return None

        direction, order_id_str, price_str, quantity_str, *peak_size_list = tokens

        if direction not in ["B", "S"]:
            logger.error(f"Unexpected buy direction: {direction}")
            return None

        is_buy = direction == "B"

        try:
            order_id, price, quantity = map(
                int, (order_id_str, price_str, quantity_str)
            )
            if len(peak_size_list) == 1:
                peak_size: Optional[int] = int(peak_size_list[0])
            else:
                peak_size = None
        except ValueError as e:
            logger.error(e)
            return None

        return Order.create(is_buy, order_id, price, quantity, peak_size, logger_name)
