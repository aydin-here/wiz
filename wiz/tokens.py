from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    # Keywords
    LET = auto()
    VAR = auto()
    FUNC = auto()
    WHEN = auto()
    ELSE = auto()
    SWITCH = auto()
    CASE = auto()
    DEFAULT = auto()
    RETURN = auto()
    WHILE = auto()
    FOR = auto()
    IN = auto()
    STEP = auto()
    RANGE = auto()
    BREAK = auto()
    CONTINUE = auto()
    CLASS = auto()
    IMPORT = auto()
    DECORATOR = auto()
    BEFORE = auto()
    AFTER = auto()
    ERROR = auto()

    # Literals
    IDENTIFIER = auto()
    NUMBER = auto()
    STRING = auto()
    INTERPOLATED_STRING = auto()
    BOOLEAN = auto()

    # Operators
    ASSIGN = auto()      # =
    PLUS = auto()        # +
    MINUS = auto()       # -
    STAR = auto()        # *
    SLASH = auto()       # /
    MODULO = auto()      # %
    HASH = auto()        # #

    EQUAL = auto()       # ==
    NOT_EQUAL = auto()   # !=

    GREATER = auto()     # >
    LESS = auto()        # <

    GREATER_EQUAL = auto()   # >=
    LESS_EQUAL = auto()      # <=

    AND = auto()
    OR = auto()
    NOT = auto()

    # Symbols
    LPAREN = auto()      # (
    RPAREN = auto()      # )

    LBRACE = auto()      # {
    RBRACE = auto()      # }

    LBRACKET = auto()    # [
    RBRACKET = auto()    # ]

    COMMA = auto()
    COLON = auto()
    DOT = auto()

    NEWLINE = auto()
    EOF = auto()


@dataclass(slots=True)
class Token:
    type: TokenType
    value: object = None
    line: int = 1
    column: int = 1