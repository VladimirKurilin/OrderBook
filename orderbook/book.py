from copy import deepcopy
from itertools import zip_longest
from logging import Logger, getLogger
from typing import List

from sortedcontainers import SortedList

from orderbook.order import Order


class OrderBookRecord:
    is_buy: bool
    order_id: int
    max_peak_size: int
    current_peak_size: int
    price: int
    quantity: int
    timestamp: int
    order_priority: int

    def __init__(self, order: Order, timestamp: int, order_priority: int = 0):
        self.order_id = order.order_id
        self.max_peak_size = (
            order.peak_size if order.peak_size is not None else order.quantity
        )
        self.current_peak_size = self.max_peak_size
        self.price = order.price
        self.quantity = order.quantity
        self.is_buy = order.is_buy
        self.timestamp = timestamp
        self.order_priority = order_priority
        assert self.max_peak_size == self.current_peak_size
        assert self.quantity >= self.max_peak_size

    def __lt__(self, other):
        if self.is_buy != other.is_buy:
            raise ValueError("Only Orders with the same is_buy value are comparable.")

        if self.price == other.price:
            if self.timestamp == other.timestamp:
                if self.order_priority == other.order_priority:
                    raise ValueError(
                        "Orders with same price and date cannot have equal priority."
                    )
                return self.order_priority < other.order_priority
            return self.timestamp < other.timestamp

        if self.is_buy is True:
            return self.price > other.price
        return self.price < other.price

    def __repr__(self):
        return (
            f"{'B' if self.is_buy else 'S'},(p:{self.price},t:{self.timestamp},n:{self.order_priority})"
            + f"->(visible:{self.current_peak_size},m:{self.max_peak_size},q:{self.quantity})->(Id:{self.order_id})"
        )


class Transaction:
    buy_id: int
    sell_id: int
    price: int
    quantity: int

    def __init__(self, buy_id: int, sell_id: int, price: int, quantity: int):
        self.buy_id = buy_id
        self.sell_id = sell_id
        self.price = price
        self.quantity = quantity

    def __repr__(self):
        return f"<{self.buy_id},{self.sell_id},{self.price},{self.quantity}>"

    def __str__(self):
        return repr(self)


class OrderBook:
    sell: SortedList
    buy: SortedList
    timestamp: int
    __logger: Logger

    def __init__(self, logger=getLogger()):
        self.timestamp = 0
        self.buy = SortedList()
        self.sell = SortedList()
        self.__logger = logger

    def __repr__(self):
        return str([list(self.buy), list(self.sell)])

    def __str__(self):
        rows = []
        rows.append(
            "+-----------------------------------------------------------------+"
        )
        rows.append(
            "| BUY                            | SELL                           |"
        )
        rows.append(
            "| Id       | Volume      | Price | Price | Volume      | Id       |"
        )
        rows.append(
            "+----------+-------------+-------+-------+-------------+----------+"
        )

        for row in zip_longest(self.buy, self.sell):
            buy: OrderBookRecord = row[0]
            sell: OrderBookRecord = row[1]
            columns = [""]
            if buy is None:
                columns += [" " * 10, " " * 13, " " * 7]
            else:
                columns += [
                    f"{buy.order_id:10}",
                    f"{buy.current_peak_size:13,}",
                    f"{buy.price:7,}",
                ]

            if sell is None:
                columns += [" " * 7, " " * 13, " " * 10]
            else:
                columns += [
                    f"{sell.price:7,}",
                    f"{sell.current_peak_size:13,}",
                    f"{sell.order_id:10}",
                ]
            columns.append("")
            row = "|".join(columns)
            if len(row) != 67:
                self.__logger.warning(
                    "Order book line doesn't comply with pretty print constraints"
                )
            rows.append(row)

        rows.append(
            "+-----------------------------------------------------------------+"
        )
        return "\n".join(rows)

    def add(self, order: Order) -> List[Transaction]:
        self.timestamp += 1
        order = deepcopy(order)
        transactions = self.try_to_fill_an_order(order)
        if order.quantity:
            side = self.buy if order.is_buy else self.sell
            record = OrderBookRecord(order, self.timestamp)
            side.add(record)
            self.__logger.info(f"Record inserted: {record}")
        else:
            self.__logger.info(f"{order} was completely executed")
        return transactions

    def try_to_fill_an_order(self, order: Order) -> List[Transaction]:
        against = self.sell if order.is_buy else self.buy

        transactions = {}
        candidate_records: List[OrderBookRecord] = list(
            filter(lambda x: self.__is_good_price(order, x), against)
        )

        for price in self.__unique([x.price for x in candidate_records]):
            if order.quantity == 0:
                break
            records = list(filter(lambda x: x.price == price, candidate_records))

            # Trying to fill visible peak sizes
            for record in records:
                if order.quantity == 0:
                    break
                filled_quantity = min(record.current_peak_size, order.quantity)
                record.current_peak_size -= filled_quantity
                record.quantity -= filled_quantity

                order.quantity -= filled_quantity

                transactions[(record.order_id, record.price)] = filled_quantity
                self.__logger.debug(
                    f"{order} filled by visible {record}. Volume {filled_quantity}"
                )

            # Second pass to fill hidden iceberg orders
            for record in records:
                if order.quantity == 0:
                    break

                if record.quantity > order.quantity:
                    max_peak = record.max_peak_size
                    q, r = divmod(order.quantity, max_peak)
                    record.current_peak_size = min(
                        record.max_peak_size - r, record.quantity - max_peak * q
                    )
                    filled_quantity = order.quantity
                else:
                    filled_quantity = record.quantity

                record.quantity -= filled_quantity
                order.quantity -= filled_quantity

                transactions[(record.order_id, record.price)] += filled_quantity
                if filled_quantity != 0:
                    self.__logger.debug(
                        f"{order} filled by hidden {record}. Volume {filled_quantity}"
                    )

            # cleanup
            for order_priority, record in enumerate(records):
                assert record.quantity >= 0
                if record.current_peak_size == 0:
                    record.current_peak_size = min(
                        record.quantity, record.max_peak_size
                    )
                    record.timestamp = self.timestamp
                    record.order_priority = order_priority
                    if record.quantity != 0:
                        self.__logger.debug(f"Peak updated: {record}")

        against = filter(lambda x: x.quantity != 0, against)
        if order.is_buy:
            self.sell = SortedList(against)
        else:
            self.buy = SortedList(against)

        res: List[Transaction] = []
        for ((record_id, price), volume) in transactions.items():
            sell_id = order.order_id
            buy_id = record_id
            if order.is_buy:
                buy_id, sell_id = sell_id, buy_id

            res.append(Transaction(buy_id, sell_id, price, volume))
            self.__logger.info(f"Transaction: {res[-1]}")

        return res

    @staticmethod
    def __is_good_price(order: Order, record: OrderBookRecord) -> bool:
        if order.is_buy:
            return order.price >= record.price
        else:
            return order.price <= record.price

    @staticmethod
    def __unique(lst) -> list:
        res = []
        for i in lst:
            if i not in res:
                res.append(i)
        return res
