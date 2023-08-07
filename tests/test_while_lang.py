from dataclasses import dataclass
from enum import Enum, auto
from typing import Literal, cast

from pyrsercomb import Parser, chars, const, fix, lift2, lift3, regex, string, token

Skip = Literal["skip"]


@dataclass(eq=True, frozen=True)
class Variable:
    name: str

    def __str__(self) -> str:
        return self.name


@dataclass(eq=True, frozen=True)
class Number:
    value: int

    def __str__(self) -> str:
        return str(self.value)


class BinaryArithOp(Enum):
    ADD = auto()
    SUB = auto()
    MUL = auto()
    DIV = auto()


@dataclass(eq=True, frozen=True)
class BinaryArithExpr:
    left: "ArithExpr"
    operator: BinaryArithOp
    right: "ArithExpr"


ArithExpr = BinaryArithExpr | Variable | Number


@dataclass(eq=True, frozen=True)
class Assignment:
    variable: Variable
    value: ArithExpr


class ComparisonOp(Enum):
    GT = auto()
    GEQ = auto()
    EQ = auto()
    LEQ = auto()
    LT = auto()


@dataclass(eq=True, frozen=True)
class Comparison:
    left: ArithExpr
    comparator: ComparisonOp
    right: ArithExpr


class BinaryBoolOp(Enum):
    AND = auto()
    OR = auto()


@dataclass(eq=True, frozen=True)
class BinaryBoolExpr:
    left: "BoolExpr"
    operator: BinaryBoolOp
    right: "BoolExpr"


BoolExpr = BinaryBoolExpr | Comparison | bool


@dataclass(eq=True, frozen=True)
class If:
    condition: BoolExpr
    if_true: "Statement"
    if_false: "Statement"


@dataclass(eq=True, frozen=True)
class While:
    condition: BoolExpr
    invariant: BoolExpr
    body: "Statement"


@dataclass(eq=True, frozen=True)
class Sequence:
    first: "Statement"
    second: "Statement"


Statement = Skip | Assignment | If | While | Sequence


variable = token(regex(r"[A-Za-z_]+"))[Variable]
number = token(regex(r"-?[0-9]+"))[int][Number]
add, sub, mul, div = chars("+-*/")
add_op = add[const(BinaryArithOp.ADD)]
sub_op = sub[const(BinaryArithOp.SUB)]
mul_op = mul[const(BinaryArithOp.MUL)]
div_op = div[const(BinaryArithOp.DIV)]
binary_arith_op = add_op | sub_op | mul_op | div_op

lpar, rpar = chars("()")


def def_arith_expr(parser: Parser[str, ArithExpr]) -> Parser[str, ArithExpr]:
    expr_with_parens = token(lpar) >> parser << token(rpar)
    expr = expr_with_parens ^ number ^ variable
    binary = (expr & token(binary_arith_op) & expr)[lift3(BinaryArithExpr)]
    return binary ^ expr


arith_expr = fix(def_arith_expr)

assignment = (variable << token(string(":=")) & arith_expr)[lift2(Assignment)]

gt_op = token(string(">"))[const(ComparisonOp.GT)]
geq_op = token(string(">="))[const(ComparisonOp.GEQ)]
eq_op = token(string("="))[const(ComparisonOp.EQ)]
leq_op = token(string("<="))[const(ComparisonOp.LEQ)]
lt_op = token(string("<"))[const(ComparisonOp.LT)]

comparator = gt_op ^ geq_op ^ eq_op ^ leq_op ^ lt_op
comparison = (arith_expr & comparator & arith_expr)[lift3(Comparison)]

false = token(string("false"))[const(False)]
true = token(string("true"))[const(True)]

and_op = token(string("&&"))[const(BinaryBoolOp.AND)]
or_op = token(string("||"))[const(BinaryBoolOp.OR)]

binary_bool_op = and_op | or_op


def def_bool_expr(parser: Parser[str, BoolExpr]) -> Parser[str, BoolExpr]:
    expr_with_parens = token(lpar) >> parser << token(rpar)
    expr = expr_with_parens ^ comparison ^ true ^ false
    binary = (expr & token(binary_bool_op) & expr)[lift3(BinaryBoolExpr)]
    return binary ^ expr


bool_expr = fix(def_bool_expr)

skip = token(string("skip"))[lambda x: cast(Literal["skip"], x)]

lbrace, rbrace = chars("{}")
lbracket, rbracket = chars("[]")


def def_statement(parser: Parser[str, Statement]) -> Parser[str, Statement]:
    if_statement = (
        token(string("if")) >> bool_expr << token(string("then"))
        & parser << token(string("else"))
        & parser
    )[lift3(If)]
    while_statement = (
        token(string("while")) >> bool_expr << token(string("do"))
        & token(lbracket >> bool_expr << rbracket)
        & parser
    )[lift3(While)]
    sequence_statement = (
        token(lbrace) >> parser << token(string(";")) & parser << token(rbrace)
    )[lift2(Sequence)]
    return if_statement ^ while_statement ^ sequence_statement ^ assignment ^ skip


statement = fix(def_statement)


def test_basics() -> None:
    assert variable.parse_or_raise("x") == Variable("x")
    assert variable.parse_or_raise("a_long_VARiable") == Variable("a_long_VARiable")
    assert number.parse_or_raise("123") == Number(123)
    assert number.parse_or_raise("-71") == Number(-71)


def test_arith_expr() -> None:
    assert arith_expr.parse_or_raise("123") == Number(123)
    assert arith_expr.parse_or_raise("a_VAR") == Variable("a_VAR")
    assert arith_expr.parse_or_raise("17 * -20") == BinaryArithExpr(
        Number(17), BinaryArithOp.MUL, Number(-20)
    )
    assert arith_expr.parse_or_raise("17 / x") == BinaryArithExpr(
        Number(17), BinaryArithOp.DIV, Variable("x")
    )
    assert arith_expr.parse_or_raise("17 / (1 + x)") == BinaryArithExpr(
        Number(17),
        BinaryArithOp.DIV,
        BinaryArithExpr(Number(1), BinaryArithOp.ADD, Variable("x")),
    )


def test_assignment() -> None:
    assert assignment.parse_or_raise("x := 12 / y") == Assignment(
        Variable("x"), BinaryArithExpr(Number(12), BinaryArithOp.DIV, Variable("y"))
    )


def test_comparisons() -> None:
    assert comparison.parse_or_raise("23 > x * 3") == Comparison(
        Number(23),
        ComparisonOp.GT,
        BinaryArithExpr(Variable("x"), BinaryArithOp.MUL, Number(3)),
    )


def test_bool_expr() -> None:
    assert bool_expr.parse_or_raise("false") is False
    assert bool_expr.parse_or_raise("true") is True
    assert bool_expr.parse_or_raise(
        "x > 33 && (y = -1 * z || false)"
    ) == BinaryBoolExpr(
        Comparison(Variable("x"), ComparisonOp.GT, Number(33)),
        BinaryBoolOp.AND,
        BinaryBoolExpr(
            Comparison(
                Variable("y"),
                ComparisonOp.EQ,
                BinaryArithExpr(Number(-1), BinaryArithOp.MUL, Variable("z")),
            ),
            BinaryBoolOp.OR,
            False,
        ),
    )


def test_statement() -> None:
    assert statement.parse_or_raise("skip") == "skip"
    assert statement.parse_or_raise("x := 2 * y") == assignment.parse_or_raise(
        "x := 2 * y"
    )
    assert statement.parse_or_raise("if x > y then skip else x := y + 1") == If(
        bool_expr.parse_or_raise("x > y"),
        "skip",
        assignment.parse_or_raise("x := y + 1"),
    )
    assert statement.parse_or_raise("while x <= y do [true] x := x + 1") == While(
        bool_expr.parse_or_raise("x <= y"),
        True,
        assignment.parse_or_raise("x := x + 1"),
    )
    assert (
        statement.parse_or_raise(
            """
            {
                x := 0;
                while x < y do [true] {
                    y := y - 1;
                    x := x + 1
                }
            }
            """
        )
        == Sequence(
            assignment.parse_or_raise("x := 0"),
            While(
                bool_expr.parse_or_raise("x < y"),
                True,
                Sequence(
                    assignment.parse_or_raise("y := y - 1"),
                    assignment.parse_or_raise("x := x + 1"),
                ),
            ),
        )
    )
