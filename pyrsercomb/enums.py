from enum import Enum, StrEnum
from functools import reduce
from operator import xor
from typing import TypeVar

from .core import Parser
from .functions import const
from .strings import string

TEnum = TypeVar("TEnum", bound=Enum)
TStrEnum = TypeVar("TStrEnum", bound=StrEnum)


def member(member: TEnum) -> Parser[str, TEnum]:
    return string(member.name)[const(member)]


def value(member: TStrEnum) -> Parser[str, TStrEnum]:
    return string(member.value)[const(member)]


def members(enum: type[TEnum]) -> Parser[str, TEnum]:
    return reduce(xor, map(member, enum))


def values(enum: type[TStrEnum]) -> Parser[str, TStrEnum]:
    return reduce(xor, map(value, enum))
