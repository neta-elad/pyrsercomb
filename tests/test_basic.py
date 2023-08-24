from pyrsercomb import Failure
from pyrsercomb.basic import eof, just


def test_generic() -> None:
    one = just(1)
    one_or_two = one | just(2)
    ones_and_twos = ~one_or_two
    full = ones_and_twos << eof()

    assert full.parse_or_raise([1, 2, 1, 1]) == [1, 2, 1, 1]
    assert full.parse([1, 2, 3]) == Failure(2, "eof")


def test_generic_str() -> None:
    one = just("1")
    one_or_two = one | just("2")
    ones_and_twos = ~one_or_two
    full = ones_and_twos << eof()

    assert full.parse_or_raise("1211") == ["1", "2", "1", "1"]
    assert full.parse("123") == Failure(2, "eof")


def test_bool() -> None:
    ones = ~just("1") << eof()
    assert ones.parse("111")
    assert not ones.parse("123")
