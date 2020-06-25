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
