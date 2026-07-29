from tokens import Token, TokenType


KEYWORDS = {
    "let": TokenType.LET,
    "var": TokenType.VAR,
    "func": TokenType.FUNC,
    "when": TokenType.WHEN,
    "else": TokenType.ELSE,
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
    "import": TokenType.IMPORT
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

    def make_token(self, token_type, value=None):
        return Token(
            token_type,
            value,
            self.line,
            self.column,
        )

    def identifier(self):
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
                text == "true"
            )

        if token_type is not None:
            return self.make_token(token_type)

        return self.make_token(
            TokenType.IDENTIFIER,
            text
        )

    def number(self):
        start = self.position

        while self.current() is not None and self.current().isdigit():
            self.advance()

        value = self.source[start:self.position]

        return self.make_token(TokenType.NUMBER, int(value))

    def string(self):
        self.advance()  # رد شدن از "

        start = self.position

        while self.current() is not None and self.current() != '"':
            self.advance()

        value = self.source[start:self.position]

        self.advance()  # رد شدن از "

        return self.make_token(TokenType.STRING, value)

    def tokenize(self):
        tokens = []

        while self.current() is not None:
            char = self.current()

            # فاصله
            if char in " \t":
                self.advance()
                continue

            # خط جدید
            if char == "\n":
                tokens.append(self.make_token(TokenType.NEWLINE))
                self.advance()
                continue

            # شناسه یا Keyword
            if char.isalpha() or char == "_":
                tokens.append(self.identifier())
                continue

            # عدد
            if char.isdigit():
                tokens.append(self.number())
                continue

            # رشته
            if char == '"':
                tokens.append(self.string())
                continue

            # ==
            if char == "=" and self.peek() == "=":
                tokens.append(
                    self.make_token(TokenType.EQUAL)
                )
                self.advance()
                self.advance()
                continue


            # !=
            if char == "!" and self.peek() == "=":
                tokens.append(
                    self.make_token(TokenType.NOT_EQUAL)
                )
                self.advance()
                self.advance()
                continue


            # >=
            if char == ">" and self.peek() == "=":
                tokens.append(
                    self.make_token(TokenType.GREATER_EQUAL)
                )
                self.advance()
                self.advance()
                continue


            # <=
            if char == "<" and self.peek() == "=":
                tokens.append(
                    self.make_token(TokenType.LESS_EQUAL)
                )
                self.advance()
                self.advance()
                continue

            # >
            if char == ">":
                tokens.append(
                    self.make_token(TokenType.GREATER)
                )
                self.advance()
                continue


            # <
            if char == "<":
                tokens.append(
                    self.make_token(TokenType.LESS)
                )
                self.advance()
                continue

            # =
            if char == "=":
                tokens.append(self.make_token(TokenType.ASSIGN))
                self.advance()
                continue

            # (
            if char == "(":
                tokens.append(self.make_token(TokenType.LPAREN))
                self.advance()
                continue

            # )
            if char == ")":
                tokens.append(self.make_token(TokenType.RPAREN))
                self.advance()
                continue

            if char == ",":
                tokens.append(self.make_token(TokenType.COMMA))
                self.advance()
                continue

            if char == ".":
                if self.peek() == ".":
                    tokens.append(self.make_token(TokenType.RANGE))
                    self.advance()
                    self.advance()
                    continue
                tokens.append(self.make_token(TokenType.DOT))
                self.advance()
                continue

            if char == ":":
                tokens.append(self.make_token(TokenType.COLON))
                self.advance()
                continue

            if char == "{":
                tokens.append(self.make_token(TokenType.LBRACE))
                self.advance()
                continue

            if char == "}":
                tokens.append(self.make_token(TokenType.RBRACE))
                self.advance()
                continue

            if char == "[":
                tokens.append(self.make_token(TokenType.LBRACKET))
                self.advance()
                continue

            if char == "]":
                tokens.append(self.make_token(TokenType.RBRACKET))
                self.advance()
                continue

            if char == "+":
                tokens.append(self.make_token(TokenType.PLUS))
                self.advance()
                continue

            if char == "-":
                tokens.append(self.make_token(TokenType.MINUS))
                self.advance()
                continue

            if char == "*":
                tokens.append(self.make_token(TokenType.STAR))
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
                tokens.append(self.make_token(TokenType.SLASH))
                self.advance()
                continue

            if char == "%":
                tokens.append(self.make_token(TokenType.MODULO))
                self.advance()
                continue

            raise Exception(
                f"Unexpected character '{char}' at line {self.line}"
            )

        tokens.append(self.make_token(TokenType.EOF))

        return tokens