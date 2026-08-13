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
    EXTENDS = auto()
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
    ARROW = auto()       # =>

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


TOKEN_LABELS = {
    TokenType.LET: "'let'",
    TokenType.VAR: "'var'",
    TokenType.FUNC: "'func'",
    TokenType.WHEN: "'when'",
    TokenType.ELSE: "'else'",
    TokenType.SWITCH: "'switch'",
    TokenType.CASE: "'case'",
    TokenType.DEFAULT: "'default'",
    TokenType.RETURN: "'return'",
    TokenType.WHILE: "'while'",
    TokenType.FOR: "'for'",
    TokenType.IN: "'in'",
    TokenType.STEP: "'step'",
    TokenType.RANGE: "'..'",
    TokenType.BREAK: "'break'",
    TokenType.CONTINUE: "'continue'",
    TokenType.CLASS: "'class'",
    TokenType.EXTENDS: "'extends'",
    TokenType.IMPORT: "'import'",
    TokenType.DECORATOR: "'decorator'",
    TokenType.BEFORE: "'before'",
    TokenType.AFTER: "'after'",
    TokenType.ERROR: "'error'",
    TokenType.IDENTIFIER: "a name",
    TokenType.NUMBER: "a number",
    TokenType.STRING: "a string",
    TokenType.INTERPOLATED_STRING: "an interpolated string",
    TokenType.BOOLEAN: "a boolean",
    TokenType.ASSIGN: "'='",
    TokenType.PLUS: "'+'",
    TokenType.MINUS: "'-'",
    TokenType.STAR: "'*'",
    TokenType.SLASH: "'/'",
    TokenType.MODULO: "'%'",
    TokenType.HASH: "'#'",
    TokenType.EQUAL: "'=='",
    TokenType.NOT_EQUAL: "'!='",
    TokenType.ARROW: "'=>'",
    TokenType.GREATER: "'>'",
    TokenType.LESS: "'<'",
    TokenType.GREATER_EQUAL: "'>='",
    TokenType.LESS_EQUAL: "'<='",
    TokenType.AND: "'and'",
    TokenType.OR: "'or'",
    TokenType.NOT: "'not'",
    TokenType.LPAREN: "'('",
    TokenType.RPAREN: "')'",
    TokenType.LBRACE: "'{'",
    TokenType.RBRACE: "'}'",
    TokenType.LBRACKET: "'['",
    TokenType.RBRACKET: "']'",
    TokenType.COMMA: "','",
    TokenType.COLON: "':'",
    TokenType.DOT: "'.'",
    TokenType.NEWLINE: "end of line",
    TokenType.EOF: "end of file",
}


def token_name(token_type):
    return TOKEN_LABELS.get(token_type, token_type.name)


def describe_token(token):
    if token.type == TokenType.IDENTIFIER:
        return f"name '{token.value}'"

    if token.type in (TokenType.STRING, TokenType.INTERPOLATED_STRING):
        return f"string {token.value!r}"

    if token.type == TokenType.NUMBER:
        return f"number {token.value}"

    if token.type == TokenType.BOOLEAN:
        return "boolean 'true'" if token.value else "boolean 'false'"

    return token_name(token.type)