import io
import logging

from orderbook.inputparser import InputLexer


def test_lexter_get(caplog) -> None:
    for buffer_size in (1, 2, 4, 16, 64):
        caplog.set_level(logging.INFO)
        stream = io.StringIO(
            "B,1,11,111\nS,2,22,222,2222\n            \n   #kkdkd\n B,3,33,333\nB,4,44,444   \nBB,4,44,444   \n"
        )
        lexer = InputLexer(stream, buffer_size)
        assert repr(lexer.get()) == "B,1,11,111,None"
        assert caplog.record_tuples[0] == ("root", 20, "Line 1: B,1,11,111,None")
        assert repr(lexer.get()) == "S,2,22,222,2222"
        assert caplog.record_tuples[1] == ("root", 20, "Line 2: S,2,22,222,2222")
        assert repr(lexer.get()) == "B,4,44,444,None"
        assert caplog.record_tuples[2] == ("root", 20, "Line 3: Whitespace string.")
        assert caplog.record_tuples[3] == ("root", 20, "Line 4: Comment string.")
        assert caplog.record_tuples[4] == (
            "root",
            40,
            "Line 5: Starts with whitespaces but is not a comment or empty.",
        )
        assert caplog.record_tuples[5] == ("root", 20, "Line 6: B,4,44,444,None")
        assert lexer.get() is None
        assert caplog.record_tuples[6] == ("root", 40, "Unexpected buy direction: BB")
        assert caplog.record_tuples[7] == (
            "root",
            40,
            "Line 7: Failed to parse order BB,4,44,444   \n",
        )
        assert lexer.get() is None
        assert lexer.get() is None
        assert len(caplog.record_tuples) == 8
        caplog.clear()


def test_rest_of_the_line() -> None:
    stream = io.StringIO("  initial text data\n\nkek")
    lexer = InputLexer(stream, 4)
    assert lexer._InputLexer__skip_whitespaces() == ("in", True)  # type: ignore
    assert (
        lexer._InputLexer__build_whole_line("in")  # type: ignore
        == "initial text data\n"
    )
    assert lexer._InputLexer__skip_whitespaces() == ("", True)  # type: ignore
    assert lexer._InputLexer__build_whole_line("") == ""  # type: ignore
    assert lexer._InputLexer__skip_whitespaces() == ("kek", False)  # type: ignore
    assert lexer._InputLexer__build_whole_line("kek") == "kek"  # type: ignore


def test_skip_spaces_and_rest_line() -> None:
    stream = io.StringIO(
        """
         # kkkkkkk
        1

        2
            #
            3
           455555
        """
    )
    lexer = InputLexer(stream, 2)

    assert lexer._InputLexer__skip_whitespaces() == ("", True)  # type: ignore
    assert lexer._InputLexer__skip_whitespaces() == ("#", True)  # type: ignore
    lexer._InputLexer__skip_rest_of_the_line()  # type: ignore
    assert lexer._InputLexer__skip_whitespaces() == ("1\n", True)  # type: ignore
    assert lexer._InputLexer__skip_whitespaces() == ("", True)  # type: ignore
    assert lexer._InputLexer__skip_whitespaces() == ("2\n", True)  # type: ignore
    assert lexer._InputLexer__skip_whitespaces() == ("#\n", True)  # type: ignore
    assert lexer._InputLexer__skip_whitespaces() == ("3\n", True)  # type: ignore
    assert lexer._InputLexer__skip_whitespaces() == ("4", True)  # type: ignore
    lexer._InputLexer__skip_rest_of_the_line()  # type: ignore
    assert lexer._InputLexer__skip_whitespaces() == ("", True)  # type: ignore
    assert lexer._InputLexer__skip_whitespaces() == ("", False)  # type: ignore
    assert lexer._InputLexer__skip_whitespaces() == ("", False)  # type: ignore


def test_skip_spaces_modelled() -> None:
    msg = """
    initial

    text data
    """
    stream = io.StringIO(msg)
    lexer = InputLexer(stream, 4)
    assert lexer._InputLexer__skip_whitespaces() == ("", True)  # type: ignore
    assert lexer._InputLexer__skip_whitespaces() == ("init", True)  # type: ignore
    assert lexer._InputLexer__skip_whitespaces() == ("ial\n", False)  # type: ignore
    assert lexer._InputLexer__skip_whitespaces() == ("", True)  # type: ignore
    assert lexer._InputLexer__skip_whitespaces() == ("text", True)  # type: ignore
    assert lexer._InputLexer__skip_whitespaces() == ("dat", True)  # type: ignore
    assert lexer._InputLexer__skip_whitespaces() == ("a\n", False)  # type: ignore
    assert lexer._InputLexer__skip_whitespaces() == ("", True)  # type: ignore
    assert lexer._InputLexer__skip_whitespaces() == ("", False)  # type: ignore
    assert lexer._InputLexer__skip_whitespaces() == ("", False)  # type: ignore


def test_skip_rest_of_the_line_modelled() -> None:
    stream = io.StringIO("12341234\n\n")
    lexer = InputLexer(stream, 1)

    lexer._InputLexer__skip_rest_of_the_line()  # type: ignore
    assert stream.read() == "\n"
    assert stream.read() == ""

    stream = io.StringIO("1\n")
    lexer = InputLexer(stream, 1)

    lexer._InputLexer__skip_rest_of_the_line()  # type: ignore
    assert stream.read() == ""
