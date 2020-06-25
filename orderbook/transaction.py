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
        return f"{self.buy_id},{self.sell_id},{self.price},{self.quantity}"
