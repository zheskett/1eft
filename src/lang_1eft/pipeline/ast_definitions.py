from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class ASTNode(ABC):
    line: int
    column: int


@dataclass(frozen=True)
class Expression(ASTNode, ABC):
    pass


@dataclass(frozen=True)
class Statement(ASTNode, ABC):
    pass


@dataclass(frozen=True)
class Return(Statement):
    """Return represents a return statement."""

    value: Expression | None


@dataclass(frozen=True)
class ExpressionStatement(Statement):
    """ExpressionStatement represents a statement consisting of a single expression."""

    expression: Expression


@dataclass(frozen=True)
class NoOp(Statement):
    """NoOp represents a no-operation statement."""

    pass


@dataclass(frozen=True)
class Type(ASTNode, ABC):
    pass


@dataclass(frozen=True)
class VoidType(Type):
    pass


@dataclass(frozen=True)
class DecimalType(Type):
    pass


@dataclass(frozen=True)
class BooleanType(Type):
    pass


@dataclass(frozen=True)
class StrPtrType(Type):
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
class BooleanLiteral(Expression):
    """BooleanLiteral represents a boolean literal value."""

    value: bool


@dataclass(frozen=True)
class Identifier(ASTNode):
    """Identifier represents a variable or function name."""

    name: str


@dataclass(frozen=True)
class OperatorExpr(Expression, ABC):
    """Operator represents an expression with some operator"""

    lhs: Expression
    rhs: Expression


@dataclass(frozen=True)
class OrExpr(OperatorExpr):
    """OrExpr represents a logical OR expression."""

    pass


@dataclass(frozen=True)
class AndExpr(OperatorExpr):
    """AndExpr represents a logical AND expression."""

    pass


@dataclass(frozen=True)
class CmpExpression(OperatorExpr, ABC):
    """CmpExpression represents a comparison expression."""

    @property
    @abstractmethod
    def ir_icmp(self) -> str:
        pass


@dataclass(frozen=True)
class EqualsExpr(CmpExpression):
    """EqualsExpr represents an equals expression."""

    @property
    def ir_icmp(self) -> str:
        return "=="


@dataclass(frozen=True)
class RevEqualsExpr(CmpExpression):
    """RevEqualsExpr represents a not equals expression."""

    @property
    def ir_icmp(self) -> str:
        return "!="


@dataclass(frozen=True)
class LessThanExpr(CmpExpression):
    """LessThanExpr represents a less than expression."""

    @property
    def ir_icmp(self) -> str:
        return "<"


@dataclass(frozen=True)
class LessThanEqualExpr(CmpExpression):
    """LessThanEqualExpr represents a less than or equal to expression."""

    @property
    def ir_icmp(self) -> str:
        return "<="


@dataclass(frozen=True)
class GreaterThanExpr(CmpExpression):
    """GreaterThanExpr represents a greater than expression."""

    @property
    def ir_icmp(self) -> str:
        return ">"


@dataclass(frozen=True)
class GreaterThanEqualExpr(CmpExpression):
    """GreaterThanEqualExpr represents a greater than or equal to expression."""

    @property
    def ir_icmp(self) -> str:
        return ">="


@dataclass(frozen=True)
class AddExpr(OperatorExpr):
    """AddExpr represents an addition expression."""

    pass


@dataclass(frozen=True)
class SubExpr(OperatorExpr):
    """SubExpr represents a subtraction expression."""

    pass


@dataclass(frozen=True)
class MulExpr(OperatorExpr):
    """MulExpr represents a multiplication expression."""

    pass


@dataclass(frozen=True)
class DivExpr(OperatorExpr):
    """DivExpr represents a division expression."""

    pass


@dataclass(frozen=True)
class RevExpr(Expression):
    """RevExpr represents a logical NOT expression."""

    value: Expression


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
class ElseIf(ASTNode):
    """ElseIf represents an else-if statement."""

    condition: Expression
    body: Block


@dataclass(frozen=True)
class IfStatement(Statement):
    """IfStatement represents an if statement."""

    condition: Expression
    body: Block
    else_ifs: list[ElseIf]
    else_body: Block | None


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
