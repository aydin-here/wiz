from tokens import TokenType
from nodes import *
from errors import WizSyntaxError


class Parser:

    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0

    def current(self):
        return self.tokens[self.position]

    def peek(self):
        if self.position + 1 >= len(self.tokens):
            return None

        return self.tokens[self.position + 1]

    def advance(self):
        self.position += 1

    def match(self, token_type):
        token = self.current()

        if token.type != token_type:
            raise WizSyntaxError(
                f"Expected {token_type}, got {token.type}",
                token.line,
                token.column
            )

        self.advance()

        return token

    def parse_primary(self):

        token = self.current()

        if token.type == TokenType.STRING:
            self.advance()
            return String(line=token.line, column=token.column, value=token.value)

        if token.type == TokenType.NUMBER:
            self.advance()
            return Number(line=token.line, column=token.column, value=token.value)

        if token.type == TokenType.BOOLEAN:
            self.advance()
            return Boolean(line=token.line, column=token.column, value=token.value)

        if token.type == TokenType.LBRACKET:
            return self.parse_list()

        if token.type == TokenType.LBRACE:
            return self.parse_dict()

        if token.type == TokenType.IDENTIFIER:
            self.advance()
            return Identifier(line=token.line, column=token.column, name=token.value)
        

        if token.type == TokenType.LPAREN:
            self.advance()

            expression = self.parse_expression()

            self.match(TokenType.RPAREN)

            return expression

        raise WizSyntaxError(
            f"Invalid expression.",
            token.line,
            token.column
        )

    def parse_argument(self):

        if (
            self.current().type == TokenType.IDENTIFIER
            and self.peek().type == TokenType.ASSIGN
        ):
            name = self.current().value

            self.advance()
            self.advance()

            value = self.parse_expression()

            return Argument(
                line=self.current().line,
                column=self.current().column,
                name=name,
                value=value
            )


        value = self.parse_expression()

        return Argument(
            line=self.current().line,
            column=self.current().column,
            name=None,
            value=value
        )

    def parse_postfix(self):

        expression = self.parse_primary()

        while True:

            if self.current().type == TokenType.LPAREN:

                self.advance()

                self.skip_newlines()

                arguments = []

                if self.current().type != TokenType.RPAREN:

                    while True:

                        self.skip_newlines()

                        arguments.append(
                            self.parse_argument()
                        )

                        self.skip_newlines()

                        if self.current().type != TokenType.COMMA:
                            break

                        self.advance()

                self.skip_newlines()
                self.match(TokenType.RPAREN)

                if isinstance(expression, Identifier):

                    expression = CallExpression(
                        line=self.current().line,
                        column=self.current().column,
                        name=expression.name,
                        arguments=arguments
                    )

                else:

                    expression = FunctionCallExpression(
                        line=self.current().line,
                        column=self.current().column,
                        function=expression,
                        arguments=arguments
                    )

                continue

            if self.current().type == TokenType.LBRACKET:
                self.advance()

                index = self.parse_expression()

                self.match(TokenType.RBRACKET)

                expression = IndexExpression(
                    line=self.current().line,
                    column=self.current().column,
                    object=expression,
                    index=index
                )
                continue

            if self.current().type == TokenType.DOT:

                self.advance()

                name = self.match(TokenType.IDENTIFIER).value


                if self.current().type == TokenType.LPAREN:

                    self.advance()

                    self.skip_newlines()

                    arguments = []

                    if self.current().type != TokenType.RPAREN:

                        while True:

                            arguments.append(
                                self.parse_argument()
                            )

                            self.skip_newlines()

                            if self.current().type != TokenType.COMMA:
                                break

                            self.advance()
                            self.skip_newlines()

                    self.match(TokenType.RPAREN)


                    if isinstance(expression, MemberExpression):

                        expression = MemberCallExpression(
                            line=self.current().line,
                            column=self.current().column,
                            object=expression,
                            function=name,
                            arguments=arguments
                        )

                    else:

                        expression = MethodCallExpression(
                            line=self.current().line,
                            column=self.current().column,
                            object=expression,
                            method=name,
                            arguments=arguments
                        )


                    continue


                expression = MemberExpression(
                    line=self.current().line,
                    column=self.current().column,
                    object=expression,
                    property=name
                )

                continue

            break

        return expression

    def parse_term(self):

        left = self.parse_unary()

        while self.current().type in (
            TokenType.STAR,
            TokenType.SLASH,
            TokenType.MODULO,
        ):

            operator = self.current()
            self.advance()

            right = self.parse_unary()

            left = BinaryExpression(
                line=self.current().line,
                column=self.current().column,
                left=left,
                operator=operator.type,
                right=right
            )

        return left

    def parse_addition(self):

        left = self.parse_term()

        while self.current().type in (
            TokenType.PLUS,
            TokenType.MINUS,
        ):

            operator = self.current()
            self.advance()

            right = self.parse_term()

            left = BinaryExpression(
                line=self.current().line,
                column=self.current().column,
                left=left,
                operator=operator.type,
                right=right
            )

        return left

    def parse_expression(self):
        return self.parse_or()

    def parse_comparison(self):

        left = self.parse_addition()

        while self.current().type in (
            TokenType.GREATER,
            TokenType.LESS,
            TokenType.GREATER_EQUAL,
            TokenType.LESS_EQUAL,
            TokenType.EQUAL,
            TokenType.NOT_EQUAL,
        ):

            operator = self.current().type
            self.advance()

            right = self.parse_addition()

            left = ComparisonExpression(
                line=self.current().line,
                column=self.current().column,
                left=left,
                operator=operator,
                right=right
            )

        return left

    def parse_unary(self):

        if self.current().type == TokenType.NOT:

            operator = self.current().type
            self.advance()

            return UnaryExpression(
                line=self.current().line,
                column=self.current().column,
                operator=operator,
                operand=self.parse_unary()
            )

        return self.parse_postfix()

    def parse_and(self):

        left = self.parse_comparison()

        while self.current().type == TokenType.AND:

            operator = self.current().type
            self.advance()

            right = self.parse_comparison()

            left = LogicalExpression(
                line=self.current().line,
                column=self.current().column,
                left=left,
                operator=operator,
                right=right
            )

        return left

    def parse_or(self):

        left = self.parse_and()

        while self.current().type == TokenType.OR:

            operator = self.current().type
            self.advance()

            right = self.parse_and()

            left = LogicalExpression(
                line=self.current().line,
                column=self.current().column,
                left=left,
                operator=operator,
                right=right
            )

        return left

    def parse_let(self):

        self.match(TokenType.LET)

        name = self.match(TokenType.IDENTIFIER)

        self.match(TokenType.ASSIGN)

        value = self.parse_expression()

        return LetStatement(
            line=self.current().line,
            column=self.current().column,
            name=name.value,
            value=value
        )

    def parse_var(self):

        self.match(TokenType.VAR)

        name = self.match(TokenType.IDENTIFIER)

        self.match(TokenType.ASSIGN)

        value = self.parse_expression()

        return VarStatement(
            line=self.current().line,
            column=self.current().column,
            name=name.value,
            value=value
        )

    def parse_assignment(self):

        name = self.match(TokenType.IDENTIFIER)

        if self.current().type == TokenType.LBRACKET:

            self.advance()

            index = self.parse_expression()

            self.match(TokenType.RBRACKET)

            self.match(TokenType.ASSIGN)

            value = self.parse_expression()

            return IndexAssignmentStatement(
                line=self.current().line,
                column=self.current().column,
                object=Identifier(name.value),
                index=index,
                value=value
            )

        self.match(TokenType.ASSIGN)

        value = self.parse_expression()

        return AssignmentStatement(
            line=self.current().line,
            column=self.current().column,
            name=name.value,
            value=value
        )

    def parse_when(self):

        self.match(TokenType.WHEN)

        condition = self.parse_expression()

        self.skip_newlines()

        body = self.parse_block()

        else_body = None

        self.skip_newlines()

        if self.current().type == TokenType.ELSE:

            self.advance()

            else_body = self.parse_block()

        return WhenStatement(
            line=self.current().line,
            column=self.current().column,
            condition=condition,
            body=body,
            else_body=else_body
        )

    def parse_while(self):

        self.match(TokenType.WHILE)

        condition = self.parse_expression()

        body = self.parse_block()

        return WhileStatement(
            line=self.current().line,
            column=self.current().column,
            condition=condition,
            body=body
        )

    def parse_function(self):

        self.match(TokenType.FUNC)

        name = self.match(TokenType.IDENTIFIER)

        self.match(TokenType.LPAREN)

        params = []
        defaults = {}

        if self.current().type != TokenType.RPAREN:

            while True:

                param = self.match(TokenType.IDENTIFIER)

                params.append(param.value)

                if self.current().type == TokenType.ASSIGN:
                    self.advance()
                    defaults[param.value] = self.parse_expression()

                if self.current().type != TokenType.COMMA:
                    break

                self.advance()

        self.match(TokenType.RPAREN)

        self.skip_newlines()

        body = self.parse_block()

        return FunctionStatement(
            line=self.current().line,
            column=self.current().column,
            name=name.value,
            params=params,
            defaults=defaults,
            body=body
        )

    # def parse_call(self):

    #     name = self.match(TokenType.IDENTIFIER)

    #     self.match(TokenType.LPAREN)

    #     arguments = []

    #     if self.current().type != TokenType.RPAREN:

    #         while True:

    #             arguments.append(
    #                 self.parse_expression()
    #             )

    #             if self.current().type != TokenType.COMMA:
    #                 break

    #             self.advance()

    #     self.match(TokenType.RPAREN)

    #     return CallExpression(
    #         name=name.value,
    #         arguments=arguments
    #     )

    def parse_return(self):

        self.match(TokenType.RETURN)

        value = self.parse_expression()

        return ReturnStatement(
            line=self.current().line,
            column=self.current().column,
            value=value
        )

    def parse_block(self):

        self.match(TokenType.LBRACE)

        statements = []

        while self.current().type != TokenType.RBRACE:

            if self.current().type == TokenType.NEWLINE:
                self.advance()
                continue

            statement = self.parse_statement()

            if statement:
                statements.append(statement)

        self.match(TokenType.RBRACE)

        return Block(line=self.current().line,
                        column=self.current().column,
                        statements=statements)

    def parse_break(self):

        self.match(TokenType.BREAK)

        return BreakStatement(line=self.current().line,
                        column=self.current().column)

    def parse_continue(self):

        self.match(TokenType.CONTINUE)

        return ContinueStatement(line=self.current().line,
                        column=self.current().column)

    def parse_import(self):

        self.match(TokenType.IMPORT)

        module = self.match(TokenType.IDENTIFIER)

        return ImportStatement(
            line=self.current().line,
            column=self.current().column,
            module=module.value)

    def parse_list(self):

        self.match(TokenType.LBRACKET)
        self.skip_newlines()

        elements = []

        if self.current().type != TokenType.RBRACKET:

            while True:

                elements.append(
                    self.parse_expression()
                )

                self.skip_newlines()

                if self.current().type != TokenType.COMMA:
                    break

                self.match(TokenType.COMMA)
                self.skip_newlines()

        self.skip_newlines()
        self.match(TokenType.RBRACKET)

        return ListLiteral(
            line=self.current().line,
            column=self.current().column,
            elements=elements
        )

    def parse_dict(self):

        self.match(TokenType.LBRACE)
        self.skip_newlines()

        pairs = []

        if self.current().type != TokenType.RBRACE:

            while True:

                key = self.parse_expression()

                self.match(TokenType.COLON)

                value = self.parse_expression()

                pairs.append(DictPair(key.line, key.column, key, value))

                self.skip_newlines()

                if self.current().type != TokenType.COMMA:
                    break

                self.advance()
                self.skip_newlines()

        self.skip_newlines()
        self.match(TokenType.RBRACE)

        return DictLiteral(
            line=self.current().line,
            column=self.current().column,
            pairs=pairs)

    def parse_statement(self):

        if self.current().type == TokenType.NEWLINE:
            self.advance()
            return self.parse_statement()

        if self.current().type == TokenType.LET:
            return self.parse_let()

        if self.current().type == TokenType.VAR:
            return self.parse_var()

        if self.current().type == TokenType.IDENTIFIER:

            if self.peek().type in (
                TokenType.ASSIGN,
                TokenType.LBRACKET,
            ):
                return self.parse_assignment()

            return self.parse_expression()

        if self.current().type == TokenType.WHEN:
            return self.parse_when()

        if self.current().type == TokenType.WHILE:
            return self.parse_while()

        if self.current().type == TokenType.BREAK:
            return self.parse_break()

        if self.current().type == TokenType.CONTINUE:
            return self.parse_continue()

        if self.current().type == TokenType.IMPORT:
            return self.parse_import()

        if self.current().type == TokenType.FUNC:
            return self.parse_function()

        if self.current().type == TokenType.RETURN:
            return self.parse_return()

        if self.current().type == TokenType.RBRACE:
            return None

        raise WizSyntaxError(
            f"Unexpected token {self.current().type}",
            self.current().line,
            self.current().column
        )

    def skip_newlines(self):
        while self.current().type == TokenType.NEWLINE:
            self.advance()

    def parse(self):

        body = []

        while self.current().type != TokenType.EOF:

            if self.current().type == TokenType.NEWLINE:
                self.advance()
                continue

            body.append(self.parse_statement())

        return Program(1, 1, body)