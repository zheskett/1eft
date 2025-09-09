from typing import Any
from lark import Token, Transformer

from lang_1eft.pipeline.ast_definitions import *
from lang_1eft.pipeline.ast_util import *

ADDRESS_OF_SYMBOL = "addr"
POINTER_SYMBOL = "#"
TRUE_SYMBOL = "trve"
FALSE_SYMBOL = "fa1se"
ADD_SYMBOL = "a"
SUB_SYMBOL = "s"
MUL_SYMBOL = "t"
DIV_SYMBOL = "d"
MOD_SYMBOL = f"%%"
GT_SYMBOL = "gt"
GTE_SYMBOL = "gte"
LTE_SYMBOL = "1te"
LT_SYMBOL = "1t"
EQ_SYMBOL = "eq"
REQ_SYMBOL = "req"
AND_SYMBOL = "@@"
OR_SYMBOL = "@r"


class ASTConstructor(Transformer):
    def expr(self, items: list[Any]) -> Expression:
        assert len(items) == 1
        assert isinstance(items[0], Expression)
        return items[0]

    def ret_stmt(self, items: list[Any]) -> Return:
        assert len(items) == 3 or len(items) == 2
        assert isinstance(items[0], Token)
        if len(items) == 2:
            return Return(items[0].line or 0, items[0].column or 0, None)
        assert isinstance(items[1], Expression)
        return Return(items[1].line, items[1].column, items[1])

    def no_op_stmt(self, items: list[Any]) -> NoOp:
        assert len(items) == 2
        assert isinstance(items[0], Token)
        assert isinstance(items[1], Token)
        return NoOp(items[0].line or 0, items[0].column or 0)

    def void_type(self, items: list[Any]) -> VoidType:
        assert len(items) == 1
        assert isinstance(items[0], Token)
        return VoidType(
            items[0].line or 0,
            items[0].column or 0,
        )

    def decimal_type(self, items: list[Any]) -> DecimalType:
        assert len(items) == 1
        assert isinstance(items[0], Token)
        return DecimalType(
            items[0].line or 0,
            items[0].column or 0,
        )

    def boolean_type(self, items: list[Any]) -> BooleanType:
        assert len(items) == 1
        assert isinstance(items[0], Token)
        return BooleanType(
            items[0].line or 0,
            items[0].column or 0,
        )

    def char_type(self, items: list[Any]) -> CharType:
        assert len(items) == 1
        assert isinstance(items[0], Token)
        return CharType(
            items[0].line or 0,
            items[0].column or 0,
        )

    def type(self, items: list[Any]) -> Type:
        assert len(items) >= 1
        assert isinstance(items[0], Type)
        ret = items[0]
        for i in items[1:]:
            assert isinstance(i, Token) and i.value == POINTER_SYMBOL
            ret = PointerOf(i.line or 0, i.column or 0, ret)
        return ret

    def INTEGER(self, item: Token) -> DecimalLiteral:
        return DecimalLiteral(
            item.line if item.line else 0,
            item.column if item.column else 0,
            translate_integer(item.value),
        )

    def STRING(self, item: Token) -> StringLiteral:
        assert isinstance(item.value, str)
        # Remove the backticks
        value = item.value[1:-1]
        # replace escape characters
        value = value.replace(r"\n", "\n").replace(r"\t", "\t").replace(r"\\", "\\")
        return StringLiteral(item.line or 0, item.column or 0, value)

    def BOOLEAN_LITERAL(self, item: Token) -> BooleanLiteral:
        assert isinstance(item.value, str)
        if item.value == TRUE_SYMBOL:
            value = True
        else:
            value = False
        return BooleanLiteral(item.line or 0, item.column or 0, value)

    def IDENTIFIER(self, item: Token) -> Identifier:
        return Identifier(item.line or 0, item.column or 0, item.value)

    def identifier_expr(self, items: list[Any]) -> IdentifierExpr | AddressOfExpr:
        assert len(items) == 1 or len(items) == 2
        if len(items) == 2:
            assert isinstance(items[0], Token)
            assert items[0].value == ADDRESS_OF_SYMBOL
            assert isinstance(items[1], Identifier)
            return AddressOfExpr(items[0].line or 0, items[0].column or 0, items[1])
        assert isinstance(items[0], Identifier)
        return IdentifierExpr(items[0].line, items[0].column, items[0])

    def deref_expr(self, items: list[Any]) -> DerefExpr:
        assert len(items) == 2
        assert isinstance(items[0], Token)
        assert items[0].value == POINTER_SYMBOL
        assert isinstance(items[1], Expression)
        return DerefExpr(items[0].line or 0, items[0].column or 0, items[1])

    def exec_expr(self, items: list[Any]) -> ExecExpr:
        assert len(items) >= 1
        assert isinstance(items[0], Identifier)
        if len(items) == 1:
            return ExecExpr(items[0].line, items[0].column, items[0], [])

        assert all(isinstance(i, Expression) for i in items[1:])
        return ExecExpr(items[0].line, items[0].column, items[0], items[1:])

    def rev_expr(self, items: list[Any]) -> RevExpr:
        assert len(items) == 1
        assert isinstance(items[0], Expression)
        return RevExpr(items[0].line, items[0].column, items[0])

    def neg_expr(self, items: list[Any]) -> SubExpr:
        assert len(items) == 1
        assert isinstance(items[0], Expression)
        zero = DecimalLiteral(items[0].line, items[0].column, 0)
        return SubExpr(items[0].line, items[0].column, zero, items[0])

    def factor(self, items: list[Any]) -> Expression:
        assert len(items) == 1
        assert isinstance(items[0], Expression)
        return items[0]

    def term(self, items: list[Any]) -> Expression:
        assert len(items) == 1 or len(items) >= 3
        assert isinstance(items[0], Expression)
        if len(items) == 1:
            return items[0]

        # Left Associativity
        assert items[-2].value in (MUL_SYMBOL, DIV_SYMBOL, MOD_SYMBOL)
        if items[-2].value == MUL_SYMBOL:
            return MulExpr(
                items[-2].line or items[0].line,
                items[-2].column or items[0].column,
                self.term(items[:-2]),
                items[-1],
            )
        if items[-2].value == DIV_SYMBOL:
            return DivExpr(
                items[-2].line or items[0].line,
                items[-2].column or items[0].column,
                self.term(items[:-2]),
                items[-1],
            )
        return ModExpr(
            items[-2].line or items[0].line,
            items[-2].column or items[0].column,
            self.term(items[:-2]),
            items[-1],
        )

    def formula(self, items: list[Any]) -> Expression:
        assert len(items) == 1 or len(items) >= 3
        assert isinstance(items[0], Expression)
        if len(items) == 1:
            return items[0]

        # Left Associativity
        assert items[-2].value in (ADD_SYMBOL, SUB_SYMBOL)
        if items[-2].value == ADD_SYMBOL:
            return AddExpr(
                items[-2].line or items[0].line,
                items[-2].column or items[0].column,
                self.formula(items[:-2]),
                items[-1],
            )
        return SubExpr(
            items[-2].line or items[0].line,
            items[-2].column or items[0].column,
            self.formula(items[:-2]),
            items[-1],
        )

    def comparison(self, items: list[Any]) -> Expression:
        assert len(items) == 1 or len(items) >= 3
        assert isinstance(items[0], Expression)
        if len(items) == 1:
            return items[0]

        # Left Associativity
        assert items[-2].value in (LT_SYMBOL, LTE_SYMBOL, GT_SYMBOL, GTE_SYMBOL)
        if items[-2].value == LT_SYMBOL:
            return LessThanExpr(
                items[-2].line or items[0].line,
                items[-2].column or items[0].column,
                self.comparison(items[:-2]),
                items[-1],
            )
        if items[-2].value == LTE_SYMBOL:
            return LessThanEqualExpr(
                items[-2].line or items[0].line,
                items[-2].column or items[0].column,
                self.comparison(items[:-2]),
                items[-1],
            )
        if items[-2].value == GT_SYMBOL:
            return GreaterThanExpr(
                items[-2].line or items[0].line,
                items[-2].column or items[0].column,
                self.comparison(items[:-2]),
                items[-1],
            )
        return GreaterThanEqualExpr(
            items[-2].line or items[0].line,
            items[-2].column or items[0].column,
            self.comparison(items[:-2]),
            items[-1],
        )

    def equality(self, items: list[Any]) -> Expression:
        assert len(items) == 1 or len(items) >= 3
        assert isinstance(items[0], Expression)
        if len(items) == 1:
            return items[0]

        # Left Associativity
        assert items[-2].value in (EQ_SYMBOL, REQ_SYMBOL)
        if items[-2].value == EQ_SYMBOL:
            return EqualsExpr(
                items[-2].line or items[0].line,
                items[-2].column or items[0].column,
                self.equality(items[:-2]),
                items[-1],
            )
        return RevEqualsExpr(
            items[-2].line or items[0].line,
            items[-2].column or items[0].column,
            self.equality(items[:-2]),
            items[-1],
        )

    def and_expr(self, items: list[Any]) -> Expression:
        assert len(items) == 1 or len(items) >= 3
        assert isinstance(items[0], Expression)
        if len(items) == 1:
            return items[0]

        # Left Associativity
        assert items[-2].value == AND_SYMBOL
        return AndExpr(
            items[-2].line or items[0].line,
            items[-2].column or items[0].column,
            self.and_expr(items[:-2]),
            items[-1],
        )

    def or_expr(self, items: list[Any]) -> Expression:
        assert len(items) == 1 or len(items) >= 3
        assert isinstance(items[0], Expression)
        if len(items) == 1:
            return items[0]

        # Left Associativity
        assert items[-2].value == OR_SYMBOL
        return OrExpr(
            items[-2].line or items[0].line,
            items[-2].column or items[0].column,
            self.or_expr(items[:-2]),
            items[-1],
        )

    def var_decl_stmt(self, items: list[Any]) -> VarDeclStatement:
        assert len(items) == 2
        assert isinstance(items[0], Type)
        assert not isinstance(items[0], VoidType)
        assert isinstance(items[1], Identifier)
        return VarDeclStatement(items[0].line, items[0].column, items[0], items[1])

    def var_ass_stmt(self, items: list[Any]) -> VarAssStatement:
        assert len(items) == 2
        assert isinstance(items[0], Identifier | DerefExpr)
        assert isinstance(items[1], Expression)
        return VarAssStatement(items[0].line, items[0].column, items[0], items[1])

    def expr_stmt(self, items: list[Any]) -> ExpressionStatement:
        assert len(items) == 1
        assert isinstance(items[0], Expression)
        return ExpressionStatement(items[0].line, items[0].column, items[0])

    def param(self, items: list[Any]) -> Param:
        assert len(items) == 2
        assert isinstance(items[0], Type) and not isinstance(items[0], VoidType)
        assert isinstance(items[1], Identifier)
        return Param(items[0].line, items[0].column, items[0], items[1])

    def params(self, items: list[Any]) -> list[Param]:
        assert all(isinstance(i, Param) for i in items)
        return items

    def block(self, items: list[Any]) -> Block:
        statements = items[1:-1]
        assert all(isinstance(i, Statement) for i in statements)
        assert isinstance(items[0], Token)
        assert isinstance(items[-1], Token)
        return Block(
            items[0].line or 0,
            items[0].column or 0,
            statements,
        )

    def else_stmt(self, items: list[Any]) -> Block:
        assert len(items) == 1
        assert isinstance(items[0], Block)
        return items[0]

    def else_if_stmt(self, items: list[Any]) -> ElseIf:
        assert len(items) == 2
        assert isinstance(items[0], Expression)
        assert isinstance(items[1], Block)
        return ElseIf(items[0].line, items[0].column, items[0], items[1])

    def if_stmt(self, items: list[Any]) -> IfStatement:
        assert len(items) >= 2
        assert isinstance(items[0], Expression)
        assert isinstance(items[1], Block)
        if len(items) == 2:
            return IfStatement(
                items[0].line, items[0].column, items[0], items[1], [], None
            )

        assert all(isinstance(i, ElseIf) for i in items[2:-1])
        if isinstance(items[-1], ElseIf):
            return IfStatement(
                items[0].line,
                items[0].column,
                items[0],
                items[1],
                items[2:],
                None,
            )
        assert isinstance(items[-1], Block)
        return IfStatement(
            items[0].line,
            items[0].column,
            items[0],
            items[1],
            items[2:-1],
            items[-1],
        )

    def as_stmt(self, items: list[Any]) -> AsStatement:
        assert len(items) == 2
        assert isinstance(items[0], Expression)
        assert isinstance(items[1], Block)
        return AsStatement(items[0].line, items[0].column, items[0], items[1])

    def function_def(self, items: list[Any]) -> FunctionDef:
        assert len(items) == 5
        assert isinstance(items[0], Token)
        assert isinstance(items[1], Type)
        assert isinstance(items[2], Identifier)
        assert isinstance(items[3], list)
        assert all(isinstance(p, Param) for p in items[3])
        assert isinstance(items[4], Block)
        return FunctionDef(
            items[0].line or 0,
            items[0].column or 0,
            items[1],
            items[2],
            items[3],
            items[4],
        )

    def start(self, items: list[Any]) -> Program:
        assert len(items) >= 1
        assert all(isinstance(i, FunctionDef) for i in items)
        return Program(items[0].line, items[0].column, items)
