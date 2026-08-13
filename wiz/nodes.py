from dataclasses import dataclass
from tokens import TokenType


@dataclass
class Node:
    line: int
    column: int


@dataclass
class Program(Node):
    body: list


# Types

@dataclass
class Identifier(Node):
    name: str

@dataclass
class Block(Node):
    statements: list

@dataclass
class SwitchCase(Node):
    value: Node | None
    body: Block

@dataclass
class Argument(Node):
    name: str | None
    value: object

@dataclass
class Parameter(Node):
    name: str
    default: Node | None = None

@dataclass
class Decorator(Node):
    name: str
    arguments: list[Argument]

@dataclass
class String(Node):
    value: str

@dataclass
class InterpolatedString(Node):
    parts: list

@dataclass
class Number(Node):
    value: int

@dataclass
class Boolean(Node):
    value: bool

# Expressions

@dataclass
class BinaryExpression(Node):
    left: Node
    operator: str
    right: Node

@dataclass
class ComparisonExpression(Node):
    left: Node
    operator: TokenType
    right: Node

@dataclass
class LogicalExpression(Node):
    left: any
    operator: TokenType
    right: any

@dataclass
class UnaryExpression(Node):
    operator: TokenType
    operand: any

@dataclass
class IndexExpression(Node):
    object: any
    index: any

@dataclass
class MethodCallExpression(Node):
    object: any
    method: str
    arguments: list

@dataclass
class CallExpression(Node):
    name: str
    arguments: list[Argument]

@dataclass
class MemberCallExpression(Node):
    object: object
    function: str
    arguments: list[Argument]

@dataclass
class FunctionCallExpression(Node):
    function: object
    arguments: list[Argument]

@dataclass
class MemberExpression(Node):
    object: object
    property: str

# Statements

@dataclass
class WhenStatement(Node):
    condition: Node
    body: list
    else_body: list | None

@dataclass
class LetStatement(Node):
    name: str
    value: Node

@dataclass
class VarStatement(Node):
    name: str
    value: Node

@dataclass
class AssignmentStatement(Node):
    name: str
    value: Node

@dataclass
class WhileStatement(Node):
    condition: Node
    body: Block

@dataclass
class ForStatement(Node):
    variable: str

    iterable: Node | None

    start: Node | None
    end: Node | None
    step: Node | None

    body: Block

@dataclass
class FunctionStatement(Node):
    name: str
    params: list
    defaults: dict
    body: Block
    decorators: list[Decorator]

@dataclass
class ClassStatement(Node):
    name: str
    body: Block

@dataclass
class DecoratorStatement(Node):
    name: str
    params: list[str]
    defaults: dict[str, Node]
    define: Block | None = None
    before: Block | None = None
    after: Block | None = None
    error: Block | None = None

@dataclass
class ReturnStatement(Node):
    value: Node

@dataclass
class BreakStatement(Node):
    pass

@dataclass
class ContinueStatement(Node):
    pass

@dataclass
class IndexAssignmentStatement(Node):
    object: any
    index: any
    value: any

@dataclass
class MemberAssignmentStatement(Node):
    object: any
    value: any

@dataclass
class ImportStatement(Node):
    module: str

@dataclass
class SwitchStatement(Node):
    expression: Node
    cases: list[SwitchCase]
    default: Block | None

# Literals

@dataclass
class ListLiteral(Node):
    elements: list["Node"]

@dataclass
class DictLiteral(Node):
    pairs: list

@dataclass
class DictPair(Node):
    key: any
    value: any
