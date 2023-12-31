import re
from typing import TypeVar

from .core import Failure, Parser, SimpleParser, Success, Value

_U = TypeVar("_U", covariant=True)


def string(expected: str) -> Parser[str, str]:
    length = len(expected)

    @SimpleParser
    def parser(text: str, index: int) -> Value[str]:
        if len(text) >= index + length and text[index : index + length] == expected:
            return Success(index + length, expected)
        else:
            return Failure(index, expected)

    return parser


def strings(expected: list[str]) -> list[Parser[str, str]]:
    return list(map(string, expected))


def chars(expected: str) -> list[Parser[str, str]]:
    return list(map(string, expected))


def regex(expression: str | re.Pattern[str]) -> Parser[str, str]:
    if isinstance(expression, str):
        compiled = re.compile(expression)
    else:
        compiled = expression

    @SimpleParser
    def parser(text: str, index: int) -> Value[str]:
        if match := compiled.match(text, index):
            entire_match = match[0]
            return Success(index + len(entire_match), entire_match)
        else:
            return Failure(index, str(expression))

    return parser


def whitespace() -> Parser[str, str]:
    return regex(r"\s*")


def eol() -> Parser[str, str]:
    return string("\n")


def token(parser: Parser[str, _U]) -> Parser[str, _U]:
    return whitespace() >> parser << whitespace()
