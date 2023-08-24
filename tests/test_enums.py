from enum import Enum, StrEnum, auto

from pyrsercomb import Failure, Success, member, members, value, values


class SimpleEnum(Enum):
    FIRST = auto()
    SECOND = auto()


class StringEnum(StrEnum):
    FIRST = "first"
    SECOND = "second"


def test_member() -> None:
    parser = member(SimpleEnum.FIRST)

    assert parser.parse("FIRST") == Success(5, SimpleEnum.FIRST)
    assert parser.parse("first") == Failure(0, "FIRST")


def test_value() -> None:
    parser = value(StringEnum.FIRST)

    assert parser.parse("first") == Success(5, StringEnum.FIRST)
    assert parser.parse("FIRST") == Failure(0, "first")


def test_members() -> None:
    parser = members(SimpleEnum)

    assert parser.parse("FIRST") == Success(5, SimpleEnum.FIRST)
    assert parser.parse("SECOND") == Success(6, SimpleEnum.SECOND)
    assert parser.parse("first") == Failure(0, "SECOND")


def test_values() -> None:
    parser = values(StringEnum)

    assert parser.parse("first") == Success(5, StringEnum.FIRST)
    assert parser.parse("second") == Success(6, StringEnum.SECOND)
    assert parser.parse("FIRST") == Failure(0, "second")
