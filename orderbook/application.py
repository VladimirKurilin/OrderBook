import sys

from orderbook.book import OrderBook
from orderbook.inputparser import InputLexer


def start():
    lexer = InputLexer(sys.stdin)
    book = OrderBook()

    while True:
        order = lexer.get()
        if order is None:
            break

        for transaction in book.add(order):
            sys.stdout.write(str(transaction) + "\n")

        sys.stdout.write(str(book) + "\n")
