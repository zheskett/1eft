from typing import Any
from lark import Token, Transformer

import lang_1eft.pipeline.ast_definitions as ast
from lang_1eft.pipeline.ast_util import *


class ASTConstructor(Transformer):
    def expr(self, items: list[Any]) -> ast.Expression:
        assert len(items) == 1
        assert isinstance(items[0], ast.Expression)
        return items[0]

    def ret_stmt(self, items: list[Any]) -> ast.Return:
        assert len(items) == 1
        assert isinstance(items[0], ast.Expression)
        return ast.Return(items[0].line, items[0].column, items[0])

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
