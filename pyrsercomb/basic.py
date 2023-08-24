from collections.abc import Sequence, Sized
from typing import TypeVar

from .core import Failure, Parser, SimpleParser, Success, Value

_U = TypeVar("_U", covariant=True)
_SizedI = TypeVar("_SizedI", contravariant=True, bound=Sized)

_Icon = TypeVar("_Icon", contravariant=True)


def eof() -> Parser[_SizedI, None]:
    @SimpleParser
    def parser(text: _SizedI, index: int) -> Value[None]:
        if index >= len(text):
            return Success(index, None)
        else:
            return Failure(index, "eof")

    return parser


def full(parser: Parser[_SizedI, _U]) -> Parser[_SizedI, _U]:
    return parser << eof()


def just(value: _Icon) -> Parser[Sequence[_Icon], _Icon]:
    @SimpleParser
    def parser(text: Sequence[_Icon], index: int) -> Value[_Icon]:
        if index < len(text) and text[index] == value:
            return Success(index + 1, value)
        else:
            return Failure(index, str(value))

    return parser
