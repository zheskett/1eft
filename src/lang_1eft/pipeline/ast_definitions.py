from dataclasses import dataclass


@dataclass(frozen=True)
class ASTNode:
    line: int
    column: int


@dataclass(frozen=True)
class Expression(ASTNode):
    pass


@dataclass(frozen=True)
class Statement(ASTNode):
    pass


@dataclass(frozen=True)
class Return(Statement):
    """Return represents a return statement."""

    value: Expression


@dataclass(frozen=True)
class ExpressionStatement(Statement):
    """ExpressionStatement represents a statement consisting of a single expression."""

    expression: Expression


@dataclass(frozen=True)
class Type(ASTNode):
    pass


@dataclass(frozen=True)
class VoidType(Type):
    pass


@dataclass(frozen=True)
class DecimalType(Type):
    pass


@dataclass(frozen=True)
class StringLiteral(Expression):
    """StringLiteral represents a string literal value."""

    value: str


@dataclass(frozen=True)
class DecimalLiteral(Expression):
    """Decimal literal represents a integer literal value."""

    value: int


@dataclass(frozen=True)
class Identifier(ASTNode):
    """Identifier represents a variable or function name."""

    name: str


@dataclass(frozen=True)
class IdentifierExpr(Expression):
    """IdentifierExpr represents an identifier expression."""

    identifier: Identifier


@dataclass(frozen=True)
class Exec(Expression):
    """Exec represents an exec expression."""

    identifier: Identifier
    arguments: list[Expression]


@dataclass(frozen=True)
class VarDeclStatement(Statement):
    """VarDeclStatement represents a variable declaration statement."""

    type: Type
    identifier: Identifier


@dataclass(frozen=True)
class VarAssStatement(Statement):
    """VarAssStatement represents a variable assignment statement."""

    identifier: Identifier
    value: Expression


@dataclass(frozen=True)
class Param(ASTNode):
    """Param represents a function parameter."""

    type: Type
    identifier: Identifier


@dataclass(frozen=True)
class Block(ASTNode):
    """Block represents a block of statements."""

    statements: list[Statement]


@dataclass(frozen=True)
class FunctionDef(ASTNode):
    """FunctionDef represents a function definition."""

    type: Type
    identifier: Identifier
    parameters: list[Param]
    body: Block


@dataclass(frozen=True)
class Program(ASTNode):
    """Program is the root AST node."""

    functions: list[FunctionDef]
