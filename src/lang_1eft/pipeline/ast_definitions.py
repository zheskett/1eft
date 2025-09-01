from abc import ABC


class ASTNode(ABC):
    def __init__(self, line: int, column: int) -> None:
        self.line = line
        self.column = column


class Expression(ASTNode):
    def __init__(self, line: int, column: int) -> None:
        super().__init__(line, column)


class Statement(ASTNode):
    def __init__(self, line: int, column: int) -> None:
        super().__init__(line, column)


class Return(Statement):
    """Return represents a return statement.

    Parameters
    ----------
        line : `int`
        column : `int`
        value : `Expression`
    """

    def __init__(self, line: int, column: int, value: Expression) -> None:
        super().__init__(line, column)
        self.value = value


class Type(ASTNode):
    def __init__(self, line: int, column: int) -> None:
        super().__init__(line, column)


class VoidType(Type):
    def __init__(self, line: int, column: int) -> None:
        super().__init__(line, column)


class DecimalType(Type):
    def __init__(self, line: int, column: int) -> None:
        super().__init__(line, column)


class Literal(Expression):
    """Literal represents an integer literal.

    Parameters
    ----------
        line : `int`
        column : `int`
        value : `int`
    """

    def __init__(self, line: int, column: int, value: int) -> None:
        super().__init__(line, column)
        self.value = value


class Identifier(ASTNode):
    """Identifier represents a variable or function name.

    Parameters
    ----------
        line : `int`
        column : `int`
        name : `str`
    """

    def __init__(self, line: int, column: int, name: str) -> None:
        super().__init__(line, column)
        self.name = name


class Block(ASTNode):
    """Block represents a block of statements.

    Parameters
    ----------
        line : `int`
        column : `int`
        statements : `list[Statement]`
    """

    def __init__(self, line: int, column: int, statements: list[Statement]) -> None:
        super().__init__(line, column)
        assert all(isinstance(s, Statement) for s in statements)
        self.statements = statements


class FunctionDef(ASTNode):
    """FunctionDef represents a function definition.

    Parameters
    ----------
        line : `int`
        column : `int`
        type : `Type`
        identifier : `Identifier`
        body : `Block`
    """

    def __init__(
        self, line: int, column: int, type: Type, identifier: Identifier, body: Block
    ) -> None:
        super().__init__(line, column)
        assert isinstance(type, Type)
        self.type = type
        assert isinstance(identifier, Identifier)
        self.identifier = identifier
        assert isinstance(body, Block)
        self.body = body


class Program(ASTNode):
    """Program is the root AST node.

    Parameters
    ----------
        line : `int`
        column : `int`
        functions : `list[FunctionDef]`
    """

    def __init__(self, line: int, column: int, functions: list[FunctionDef]) -> None:
        super().__init__(line, column)
        assert all(isinstance(f, FunctionDef) for f in functions)
        self.functions = functions
