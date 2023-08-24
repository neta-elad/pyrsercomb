import pytest

from pyrsercomb import (
    Failure,
    PyrsercombError,
    Success,
    chars,
    full,
    lift2,
    regex,
    string,
    strings,
    token,
)


def test_string() -> None:
    plus = string("+")

    assert plus.parse("+") == Success(1, "+")
    assert plus.parse("+-") == Success(1, "+")
    assert plus.parse("-") == Failure(0, "+")

    longer = string("longer")

    assert longer.parse("longer") == Success(6, "longer")

    with pytest.raises(PyrsercombError):
        longer.parse_or_raise("short")


def test_strings() -> None:
    me, you = strings(["me", "you"])
    assert me.parse("me") == Success(2, "me")
    assert me.parse("you") == Failure(0, "me")
    assert you.parse("me") == Failure(0, "you")
    assert you.parse("you") == Success(3, "you")


def test_chars() -> None:
    lpar, rpar = chars("()")
    assert lpar.parse("(") == Success(1, "(")
    assert lpar.parse(")") == Failure(0, "(")
    assert rpar.parse("(") == Failure(0, ")")
    assert rpar.parse(")") == Success(1, ")")


def test_regex() -> None:
    number = regex(r"[1-9][0-9]*")

    assert number.parse("123") == Success(3, "123")
    assert number.parse("103") == Success(3, "103")
    assert number.parse("03") == Failure(0, r"[1-9][0-9]*")


def test_compose() -> None:
    def add(x: int, y: int) -> int:
        return x + y

    number = regex(r"[1-9][0-9]*")[int]
    plus = token(string("+"))
    addition = (number << plus & number)[lift2(add)]

    assert addition.parse("123+456") == Success(7, 579)
    assert addition.parse("123 + 456") == Success(9, 579)


def test_many() -> None:
    number = token(regex(r"[1-9][0-9]*"))[int]
    numbers = ~number

    assert numbers.parse("123 456 789") == Success(11, [123, 456, 789])


def test_parse_all() -> None:
    number = token(regex(r"[1-9][0-9]*"))[int]

    assert number.parse("123 foo") == Success(4, 123)

    number_all = full(number)

    assert number_all.parse("123") == Success(3, 123)
    assert number_all.parse("123 foo") == Failure(4, "eof")


def test_sep_by() -> None:
    number = token(regex(r"[1-9][0-9]+"))[int]
    comma = token(string(","))
    numbers = full(number @ comma)

    assert numbers.parse("") == Failure(0, r"[1-9][0-9]+")
    assert numbers.parse("123") == Success(3, [123])
    assert numbers.parse("123 , 456") == Success(9, [123, 456])
    assert numbers.parse("123,") == Failure(4, r"[1-9][0-9]+")
