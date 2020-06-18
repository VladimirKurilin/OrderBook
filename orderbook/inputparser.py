import logging
from typing import Optional, Tuple

from orderbook.order import Order


class InputLexer:
    def __init__(self, input_stream, buffer_limit: int = 20, logger_name: str = None):
        self.input_stream = input_stream
        self.buffer_limit = buffer_limit
        self.__logger = logging.getLogger(logger_name)
        self.__line_count = 0

    def get(self) -> Optional[Order]:
        while True:
            self.__line_count += 1
            buffer, whitespace_started = self.__skip_whitespaces()
            if not buffer and whitespace_started is False:
                return None

            if not buffer:
                self.__logger.info(f"Line {self.__line_count}: Whitespace string.")
                continue

            if whitespace_started and buffer[0] == "#":
                if buffer[-1] != "\n":
                    self.__skip_rest_of_the_line()
                self.__logger.info(f"Line {self.__line_count}: Comment string.")
                continue

            if whitespace_started:
                if buffer[-1] != "\n":
                    self.__skip_rest_of_the_line()
                self.__logger.error(
                    f"Line {self.__line_count}: "
                    f"Starts with whitespaces but is not a comment or empty."
                )
                continue

            buffer = self.__build_whole_line(buffer)
            order = Order.from_string(buffer)

            if order is None:
                self.__logger.error(
                    f"Line {self.__line_count}: Failed to parse order {buffer}"
                )
                continue

            self.__logger.info(f"Line {self.__line_count}: {order}")
            return order

    def __skip_whitespaces(self) -> Tuple[str, bool]:
        """
        Skip starting whitespaces from input stream.

        :rtype: (string, bool)
        :return:
            First non-whitespace buffer fragment and bool flag whether
            there were any whitespaces at the beginning of the line.

            If there's only whitespace characters, the '\n' is returned
        """
        buffer: str = self.input_stream.readline(self.buffer_limit)
        if not buffer:
            return "", False

        is_whitespace_started = buffer[0].isspace()

        while True:
            stripped = buffer.lstrip()
            if stripped or not buffer or buffer[-1] == "\n":
                break
            buffer = self.input_stream.readline(self.buffer_limit)

        return stripped, is_whitespace_started

    def __skip_rest_of_the_line(self) -> None:
        buffer = self.input_stream.readline(self.buffer_limit)
        while buffer and buffer[-1] != "\n":
            buffer = self.input_stream.readline(self.buffer_limit)

    def __build_whole_line(self, buffer: str) -> str:
        res = buffer
        while buffer and buffer[-1] != "\n":
            buffer = self.input_stream.readline(self.buffer_limit)
            res += buffer
        return res
