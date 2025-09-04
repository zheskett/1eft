from typing import Any
from lark import Token, Transformer

import lang_1eft.pipeline.ast_definitions as ast
from lang_1eft.pipeline.ast_util import *

TRUE_SYMBOL = "trve"
FALSE_SYMBOL = "fa1se"
ADD_SYMBOL = "a"
SUB_SYMBOL = "s"
MUL_SYMBOL = "t"
DIV_SYMBOL = "d"
GT_SYMBOL = "gt"
GTE_SYMBOL = "gte"
LTE_SYMBOL = "1te"
LT_SYMBOL = "1t"
EQ_SYMBOL = "eq"
REQ_SYMBOL = "req"
AND_SYMBOL = "@@"
OR_SYMBOL = "@r"


class ASTConstructor(Transformer):
    def expr(self, items: list[Any]) -> ast.Expression:
        assert len(items) == 1
        assert isinstance(items[0], ast.Expression)
        return items[0]

    def ret_stmt(self, items: list[Any]) -> ast.Return:
        assert len(items) == 3 or len(items) == 2
        assert isinstance(items[0], Token)
        if len(items) == 2:
            return ast.Return(items[0].line or 0, items[0].column or 0, None)
        assert isinstance(items[1], ast.Expression)
        return ast.Return(items[1].line, items[1].column, items[1])

    def no_op_stmt(self, items: list[Any]) -> ast.NoOp:
        assert len(items) == 2
        assert isinstance(items[0], Token)
        assert isinstance(items[1], Token)
        return ast.NoOp(items[0].line or 0, items[0].column or 0)

    def void_type(self, items: list[Any]) -> ast.VoidType:
        assert len(items) == 1
        assert isinstance(items[0], Token)
        return ast.VoidType(
            items[0].line or 0,
            items[0].column or 0,
        )

    def decimal_type(self, items: list[Any]) -> ast.DecimalType:
        assert len(items) == 1
        assert isinstance(items[0], Token)
        return ast.DecimalType(
            items[0].line or 0,
            items[0].column or 0,
        )

    def boolean_type(self, items: list[Any]) -> ast.BooleanType:
        assert len(items) == 1
        assert isinstance(items[0], Token)
        return ast.BooleanType(
            items[0].line or 0,
            items[0].column or 0,
        )

    def str_ptr_type(self, items: list[Any]) -> ast.StrPtrType:
        assert len(items) == 1
        assert isinstance(items[0], Token)
        return ast.StrPtrType(
            items[0].line or 0,
            items[0].column or 0,
        )

    def INTEGER(self, item: Token) -> ast.DecimalLiteral:
        return ast.DecimalLiteral(
            item.line if item.line else 0,
            item.column if item.column else 0,
            translate_integer(item.value),
        )

    def STRING(self, item: Token) -> ast.StringLiteral:
        assert isinstance(item.value, str)
        # Remove the backticks
        value = item.value[1:-1]
        # replace escape characters
        value = value.replace(r"\n", "\n").replace(r"\t", "\t").replace(r"\\", "\\")
        return ast.StringLiteral(item.line or 0, item.column or 0, value)

    def BOOLEAN_LITERAL(self, item: Token) -> ast.BooleanLiteral:
        assert isinstance(item.value, str)
        if item.value == TRUE_SYMBOL:
            value = True
        else:
            value = False
        return ast.BooleanLiteral(item.line or 0, item.column or 0, value)

    def IDENTIFIER(self, item: Token) -> ast.Identifier:
        return ast.Identifier(item.line or 0, item.column or 0, item.value)

    def identifier_expr(self, items: list[Any]) -> ast.IdentifierExpr:
        assert len(items) == 1
        assert isinstance(items[0], ast.Identifier)
        return ast.IdentifierExpr(items[0].line, items[0].column, items[0])

    def exec_expr(self, items: list[Any]) -> ast.Exec:
        assert len(items) >= 1
        assert isinstance(items[0], ast.Identifier)
        if len(items) == 1:
            return ast.Exec(items[0].line, items[0].column, items[0], [])

        assert all(isinstance(i, ast.Expression) for i in items[1:])
        return ast.Exec(items[0].line, items[0].column, items[0], items[1:])

    def rev_expr(self, items: list[Any]) -> ast.RevExpr:
        assert len(items) == 1
        assert isinstance(items[0], ast.Expression)
        return ast.RevExpr(items[0].line, items[0].column, items[0])

    def neg_expr(self, items: list[Any]) -> ast.SubExpr:
        assert len(items) == 1
        assert isinstance(items[0], ast.Expression)
        zero = ast.DecimalLiteral(items[0].line, items[0].column, 0)
        return ast.SubExpr(items[0].line, items[0].column, zero, items[0])

    def factor(self, items: list[Any]) -> ast.Expression:
        assert len(items) == 1
        assert isinstance(items[0], ast.Expression)
        return items[0]

    def term(self, items: list[Any]) -> ast.Expression:
        assert len(items) == 1 or len(items) >= 3
        assert isinstance(items[0], ast.Expression)
        if len(items) == 1:
            return items[0]

        # Left Associativity
        assert items[-2].value in (MUL_SYMBOL, DIV_SYMBOL)
        if items[-2].value == MUL_SYMBOL:
            return ast.MulExpr(
                items[-2].line or items[0].line,
                items[-2].column or items[0].column,
                self.term(items[:-2]),
                items[-1],
            )
        return ast.DivExpr(
            items[-2].line or items[0].line,
            items[-2].column or items[0].column,
            self.term(items[:-2]),
            items[-1],
        )

    def formula(self, items: list[Any]) -> ast.Expression:
        assert len(items) == 1 or len(items) >= 3
        assert isinstance(items[0], ast.Expression)
        if len(items) == 1:
            return items[0]

        # Left Associativity
        assert items[-2].value in (ADD_SYMBOL, SUB_SYMBOL)
        if items[-2].value == ADD_SYMBOL:
            return ast.AddExpr(
                items[-2].line or items[0].line,
                items[-2].column or items[0].column,
                self.formula(items[:-2]),
                items[-1],
            )
        return ast.SubExpr(
            items[-2].line or items[0].line,
            items[-2].column or items[0].column,
            self.formula(items[:-2]),
            items[-1],
        )

    def comparison(self, items: list[Any]) -> ast.Expression:
        assert len(items) == 1 or len(items) >= 3
        assert isinstance(items[0], ast.Expression)
        if len(items) == 1:
            return items[0]

        # Left Associativity
        assert items[-2].value in (LT_SYMBOL, LTE_SYMBOL, GT_SYMBOL, GTE_SYMBOL)
        if items[-2].value == LT_SYMBOL:
            return ast.LessThanExpr(
                items[-2].line or items[0].line,
                items[-2].column or items[0].column,
                self.comparison(items[:-2]),
                items[-1],
            )
        if items[-2].value == LTE_SYMBOL:
            return ast.LessThanEqualExpr(
                items[-2].line or items[0].line,
                items[-2].column or items[0].column,
                self.comparison(items[:-2]),
                items[-1],
            )
        if items[-2].value == GT_SYMBOL:
            return ast.GreaterThanExpr(
                items[-2].line or items[0].line,
                items[-2].column or items[0].column,
                self.comparison(items[:-2]),
                items[-1],
            )
        return ast.GreaterThanEqualExpr(
            items[-2].line or items[0].line,
            items[-2].column or items[0].column,
            self.comparison(items[:-2]),
            items[-1],
        )

    def equality(self, items: list[Any]) -> ast.Expression:
        assert len(items) == 1 or len(items) >= 3
        assert isinstance(items[0], ast.Expression)
        if len(items) == 1:
            return items[0]

        # Left Associativity
        assert items[-2].value in (EQ_SYMBOL, REQ_SYMBOL)
        if items[-2].value == EQ_SYMBOL:
            return ast.EqualsExpr(
                items[-2].line or items[0].line,
                items[-2].column or items[0].column,
                self.equality(items[:-2]),
                items[-1],
            )
        return ast.RevEqualsExpr(
            items[-2].line or items[0].line,
            items[-2].column or items[0].column,
            self.equality(items[:-2]),
            items[-1],
        )

    def and_expr(self, items: list[Any]) -> ast.Expression:
        assert len(items) == 1 or len(items) >= 3
        assert isinstance(items[0], ast.Expression)
        if len(items) == 1:
            return items[0]

        # Left Associativity
        assert items[-2].value == AND_SYMBOL
        return ast.AndExpr(
            items[-2].line or items[0].line,
            items[-2].column or items[0].column,
            self.and_expr(items[:-2]),
            items[-1],
        )

    def or_expr(self, items: list[Any]) -> ast.Expression:
        assert len(items) == 1 or len(items) >= 3
        assert isinstance(items[0], ast.Expression)
        if len(items) == 1:
            return items[0]

        # Left Associativity
        assert items[-2].value == OR_SYMBOL
        return ast.OrExpr(
            items[-2].line or items[0].line,
            items[-2].column or items[0].column,
            self.or_expr(items[:-2]),
            items[-1],
        )

    def var_decl_stmt(self, items: list[Any]) -> ast.VarDeclStatement:
        assert len(items) == 2
        assert isinstance(items[0], ast.Type)
        assert not isinstance(items[0], ast.VoidType)
        assert isinstance(items[1], ast.Identifier)
        return ast.VarDeclStatement(items[0].line, items[0].column, items[0], items[1])

    def var_ass_stmt(self, items: list[Any]) -> ast.VarAssStatement:
        assert len(items) == 2
        assert isinstance(items[0], ast.Identifier)
        assert isinstance(items[1], ast.Expression)
        return ast.VarAssStatement(items[0].line, items[0].column, items[0], items[1])

    def expr_stmt(self, items: list[Any]) -> ast.ExpressionStatement:
        assert len(items) == 1
        assert isinstance(items[0], ast.Expression)
        return ast.ExpressionStatement(items[0].line, items[0].column, items[0])

    def param(self, items: list[Any]) -> ast.Param:
        assert len(items) == 2
        assert isinstance(items[0], ast.Type) and not isinstance(items[0], ast.VoidType)
        assert isinstance(items[1], ast.Identifier)
        return ast.Param(items[0].line, items[0].column, items[0], items[1])

    def params(self, items: list[Any]) -> list[ast.Param]:
        assert all(isinstance(i, ast.Param) for i in items)
        return items

    def block(self, items: list[Any]) -> ast.Block:
        statements = items[1:-1]
        assert all(isinstance(i, ast.Statement) for i in statements)
        assert isinstance(items[0], Token)
        assert isinstance(items[-1], Token)
        return ast.Block(
            items[0].line or 0,
            items[0].column or 0,
            statements,
        )

    def function_def(self, items: list[Any]) -> ast.FunctionDef:
        assert len(items) == 5
        assert isinstance(items[0], Token)
        assert isinstance(items[1], ast.Type)
        assert isinstance(items[2], ast.Identifier)
        assert isinstance(items[3], list)
        assert all(isinstance(p, ast.Param) for p in items[3])
        assert isinstance(items[4], ast.Block)
        return ast.FunctionDef(
            items[0].line or 0,
            items[0].column or 0,
            items[1],
            items[2],
            items[3],
            items[4],
        )

    def start(self, items: list[Any]) -> ast.Program:
        assert len(items) >= 1
        assert all(isinstance(i, ast.FunctionDef) for i in items)
        return ast.Program(items[0].line, items[0].column, items)
