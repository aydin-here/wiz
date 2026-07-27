from dataclasses import dataclass
from tokens import TokenType


class Node:
    pass


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
class String(Node):
    value: str


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
class LogicalExpression:
    left: any
    operator: TokenType
    right: any

@dataclass
class UnaryExpression:
    operator: TokenType
    operand: any

@dataclass
class IndexExpression:
    object: any
    index: any

@dataclass
class MethodCallExpression:
    object: any
    method: str
    arguments: list

@dataclass
class CallExpression(Node):
    name: str
    arguments: list

@dataclass
class MemberCallExpression(Node):
    object: object
    function: str
    arguments: list

@dataclass
class FunctionCallExpression:
    function: object
    arguments: list

@dataclass
class MemberExpression:
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
class FunctionStatement(Node):
    name: str
    params: list
    body: Block

@dataclass
class ReturnStatement(Node):
    value: Node

@dataclass
class BreakStatement:
    pass

@dataclass
class ContinueStatement:
    pass

@dataclass
class IndexAssignmentStatement:
    object: any
    index: any
    value: any

@dataclass
class ImportStatement(Node):
    module: str

# Literals

@dataclass
class ListLiteral:
    elements: list["Node"]

@dataclass
class DictLiteral:
    pairs: list

@dataclass
class DictPair:
    key: any
    value: any
