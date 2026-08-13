from tokens import Token, TokenType
from errors import WizSyntaxError


KEYWORDS = {
    "let": TokenType.LET,
    "var": TokenType.VAR,
    "func": TokenType.FUNC,
    "when": TokenType.WHEN,
    "else": TokenType.ELSE,
    "switch": TokenType.SWITCH,
    "case": TokenType.CASE,
    "default": TokenType.DEFAULT,
    "return": TokenType.RETURN,
    "true": TokenType.BOOLEAN,
    "false": TokenType.BOOLEAN,
    "while": TokenType.WHILE,
    "for": TokenType.FOR,
    "in": TokenType.IN,
    "step": TokenType.STEP,
    "and": TokenType.AND,
    "or": TokenType.OR,
    "not": TokenType.NOT,
    "break": TokenType.BREAK,
    "continue": TokenType.CONTINUE,
    "class": TokenType.CLASS,
    "extends": TokenType.EXTENDS,
    "import": TokenType.IMPORT,
    "decorator": TokenType.DECORATOR
}


class Lexer:

    def __init__(self, source: str):
        self.source = source
        self.position = 0
        self.line = 1
        self.column = 1

    def current(self):
        if self.position >= len(self.source):
            return None
        return self.source[self.position]

    def peek(self):
        if self.position + 1 >= len(self.source):
            return None
        return self.source[self.position + 1]

    def advance(self):
        char = self.current()

        self.position += 1

        if char == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1

        return char

    def make_token(self, token_type, value=None, line=None, column=None):
        return Token(
            token_type,
            value,
            self.line if line is None else line,
            self.column if column is None else column,
        )

    def identifier(self, line, column):
        start = self.position

        while self.current() is not None and (
            self.current().isalnum() or self.current() == "_"
        ):
            self.advance()

        text = self.source[start:self.position]

        token_type = KEYWORDS.get(text)

        if token_type == TokenType.BOOLEAN:
            return self.make_token(
                TokenType.BOOLEAN,
                text == "true",
                line,
                column
            )

        if token_type is not None:
            return self.make_token(token_type, line=line, column=column)

        return self.make_token(
            TokenType.IDENTIFIER,
            text,
            line,
            column
        )

    def number(self, line, column):
        start = self.position

        while self.current() is not None and self.current().isdigit():
            self.advance()

        value = self.source[start:self.position]

        return self.make_token(TokenType.NUMBER, int(value), line, column)

    def string(self, line, column):
        self.advance()  # Skipping "

        start = self.position

        while self.current() is not None and self.current() != '"':
            self.advance()

        value = self.source[start:self.position]

        self.advance()  # Skipping "

        return self.make_token(TokenType.STRING, value, line, column)

    def interpolated_string(self, line, column):
        self.advance()  # Skipping $
        self.advance()  # Skipping "

        start = self.position

        depth = 0

        while self.current() is not None:

            char = self.current()

            if char == "{":
                depth += 1

            elif char == "}":
                depth -= 1

            elif char == '"' and depth == 0:
                break

            self.advance()

        value = self.source[start:self.position]

        self.advance()  # Skipping "

        return self.make_token(TokenType.INTERPOLATED_STRING, value, line, column)

    def tokenize(self):
        tokens = []

        while self.current() is not None:
            char = self.current()

            token_line, token_column = self.line, self.column

            # Space
            if char in " \t":
                self.advance()
                continue

            # New Line
            if char == "\n":
                tokens.append(
                    self.make_token(
                        TokenType.NEWLINE,
                        line=token_line,
                        column=token_column
                    )
                )
                self.advance()
                continue

            # Variable or Keyword
            if char.isalpha() or char == "_":
                tokens.append(self.identifier(token_line, token_column))
                continue

            # Number
            if char.isdigit():
                tokens.append(self.number(token_line, token_column))
                continue

            # Interpolated String
            if char == "$" and self.peek() == '"':
                tokens.append(
                    self.interpolated_string(token_line, token_column)
                )
                continue

            # String
            if char == '"':
                tokens.append(self.string(token_line, token_column))
                continue

            # ==
            if char == "=" and self.peek() == "=":
                tokens.append(
                    self.make_token(
                        TokenType.EQUAL,
                        line=token_line,
                        column=token_column
                    )
                )
                self.advance()
                self.advance()
                continue

            # =>
            if char == "=" and self.peek() == ">":
                tokens.append(
                    self.make_token(
                        TokenType.ARROW,
                        line=token_line,
                        column=token_column
                    )
                )
                self.advance()
                self.advance()
                continue


            # !=
            if char == "!" and self.peek() == "=":
                tokens.append(
                    self.make_token(
                        TokenType.NOT_EQUAL,
                        line=token_line,
                        column=token_column
                    )
                )
                self.advance()
                self.advance()
                continue


            # >=
            if char == ">" and self.peek() == "=":
                tokens.append(
                    self.make_token(
                        TokenType.GREATER_EQUAL,
                        line=token_line,
                        column=token_column
                    )
                )
                self.advance()
                self.advance()
                continue


            # <=
            if char == "<" and self.peek() == "=":
                tokens.append(
                    self.make_token(
                        TokenType.LESS_EQUAL,
                        line=token_line,
                        column=token_column
                    )
                )
                self.advance()
                self.advance()
                continue

            # >
            if char == ">":
                tokens.append(
                    self.make_token(
                        TokenType.GREATER,
                        line=token_line,
                        column=token_column
                    )
                )
                self.advance()
                continue


            # <
            if char == "<":
                tokens.append(
                    self.make_token(
                        TokenType.LESS,
                        line=token_line,
                        column=token_column
                    )
                )
                self.advance()
                continue

            # =
            if char == "=":
                tokens.append(
                    self.make_token(
                        TokenType.ASSIGN,
                        line=token_line,
                        column=token_column
                    )
                )
                self.advance()
                continue

            # (
            if char == "(":
                tokens.append(
                    self.make_token(
                        TokenType.LPAREN,
                        line=token_line,
                        column=token_column
                    )
                )
                self.advance()
                continue

            # )
            if char == ")":
                tokens.append(
                    self.make_token(
                        TokenType.RPAREN,
                        line=token_line,
                        column=token_column
                    )
                )
                self.advance()
                continue

            if char == "#":
                tokens.append(
                    self.make_token(
                        TokenType.HASH,
                        line=token_line,
                        column=token_column
                    )
                )
                self.advance()
                continue

            if char == ",":
                tokens.append(
                    self.make_token(
                        TokenType.COMMA,
                        line=token_line,
                        column=token_column
                    )
                )
                self.advance()
                continue

            if char == ".":
                if self.peek() == ".":
                    tokens.append(
                        self.make_token(
                            TokenType.RANGE,
                            line=token_line,
                            column=token_column
                        )
                    )
                    self.advance()
                    self.advance()
                    continue
                tokens.append(
                    self.make_token(
                        TokenType.DOT,
                        line=token_line,
                        column=token_column
                    )
                )
                self.advance()
                continue

            if char == ":":
                tokens.append(
                    self.make_token(
                        TokenType.COLON,
                        line=token_line,
                        column=token_column
                    )
                )
                self.advance()
                continue

            if char == "{":
                tokens.append(
                    self.make_token(
                        TokenType.LBRACE,
                        line=token_line,
                        column=token_column
                    )
                )
                self.advance()
                continue

            if char == "}":
                tokens.append(
                    self.make_token(
                        TokenType.RBRACE,
                        line=token_line,
                        column=token_column
                    )
                )
                self.advance()
                continue

            if char == "[":
                tokens.append(
                    self.make_token(
                        TokenType.LBRACKET,
                        line=token_line,
                        column=token_column
                    )
                )
                self.advance()
                continue

            if char == "]":
                tokens.append(
                    self.make_token(
                        TokenType.RBRACKET,
                        line=token_line,
                        column=token_column
                    )
                )
                self.advance()
                continue

            if char == "+":
                tokens.append(
                    self.make_token(
                        TokenType.PLUS,
                        line=token_line,
                        column=token_column
                    )
                )
                self.advance()
                continue

            if char == "-":
                tokens.append(
                    self.make_token(
                        TokenType.MINUS,
                        line=token_line,
                        column=token_column
                    )
                )
                self.advance()
                continue

            if char == "*":
                tokens.append(
                    self.make_token(
                        TokenType.STAR,
                        line=token_line,
                        column=token_column
                    )
                )
                self.advance()
                continue

            if char == "/" and self.peek() == "/":

                while (
                    self.current() is not None
                    and self.current() != "\n"
                ):
                    self.advance()

                continue

            if char == "/" and self.peek() == "*":

                while (
                    self.current() is not None
                    and not (
                        self.current() == "*"
                        and self.peek() == "/"
                    )
                ):
                    self.advance()

                self.advance()
                self.advance()
                continue

            if char == "/":
                tokens.append(
                    self.make_token(
                        TokenType.SLASH,
                        line=token_line,
                        column=token_column
                    )
                )
                self.advance()
                continue

            if char == "%":
                tokens.append(
                    self.make_token(
                        TokenType.MODULO,
                        line=token_line,
                        column=token_column
                    )
                )
                self.advance()
                continue

            raise WizSyntaxError(
                f"Unexpected character '{char}'",
                token_line,
                token_column
            )

        tokens.append(
            self.make_token(
                TokenType.EOF,
                line=self.line,
                column=self.column
            )
        )

        return tokens