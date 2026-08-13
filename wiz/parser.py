from tokens import TokenType, token_name, describe_token
from nodes import *
from errors import WizSyntaxError
from lexer import Lexer


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
                f"Expected {token_name(token_type)}, found {describe_token(token)}",
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

        if token.type == TokenType.INTERPOLATED_STRING:
            return self.parse_interpolated_string()

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

        if token.type == TokenType.WHEN:
            return self.parse_when_expression()

        if token.type == TokenType.FUNC:
            return self.parse_function_expression()

        raise WizSyntaxError(
            f"Invalid expression starting with {describe_token(token)}",
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
                line=value.line,
                column=value.column,
                name=name,
                value=value
            )


        value = self.parse_expression()

        return Argument(
            line=value.line,
            column=value.column,
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

                base = expression

                if isinstance(base, Identifier):

                    expression = CallExpression(
                        line=base.line,
                        column=base.column,
                        name=base.name,
                        arguments=arguments
                    )

                else:

                    expression = FunctionCallExpression(
                        line=base.line,
                        column=base.column,
                        function=base,
                        arguments=arguments
                    )

                continue

            if self.current().type == TokenType.LBRACKET:
                self.advance()

                index = self.parse_expression()

                self.match(TokenType.RBRACKET)

                expression = IndexExpression(
                    line=expression.line,
                    column=expression.column,
                    object=expression,
                    index=index
                )
                continue

            if self.current().type == TokenType.DOT:

                self.advance()

                name_token = self.match(TokenType.IDENTIFIER)

                name = name_token.value


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
                            line=name_token.line,
                            column=name_token.column,
                            object=expression,
                            function=name,
                            arguments=arguments
                        )

                    else:

                        expression = MethodCallExpression(
                            line=name_token.line,
                            column=name_token.column,
                            object=expression,
                            method=name,
                            arguments=arguments
                        )


                    continue


                expression = MemberExpression(
                    line=name_token.line,
                    column=name_token.column,
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
                line=operator.line,
                column=operator.column,
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
                line=operator.line,
                column=operator.column,
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

            operator = self.current()
            self.advance()

            right = self.parse_addition()

            left = ComparisonExpression(
                line=operator.line,
                column=operator.column,
                left=left,
                operator=operator.type,
                right=right
            )

        return left

    def parse_unary(self):

        if self.current().type in (
            TokenType.NOT,
            TokenType.MINUS,
            TokenType.PLUS,
        ):

            operator = self.current()
            self.advance()

            return UnaryExpression(
                line=operator.line,
                column=operator.column,
                operator=operator.type,
                operand=self.parse_unary()
            )

        return self.parse_postfix()

    def parse_and(self):

        left = self.parse_comparison()

        while self.current().type == TokenType.AND:

            operator = self.current()
            self.advance()

            right = self.parse_comparison()

            left = LogicalExpression(
                line=operator.line,
                column=operator.column,
                left=left,
                operator=operator.type,
                right=right
            )

        return left

    def parse_or(self):

        left = self.parse_and()

        while self.current().type == TokenType.OR:

            operator = self.current()
            self.advance()

            right = self.parse_and()

            left = LogicalExpression(
                line=operator.line,
                column=operator.column,
                left=left,
                operator=operator.type,
                right=right
            )

        return left

    def parse_let(self):

        self.match(TokenType.LET)

        name = self.match(TokenType.IDENTIFIER)

        self.match(TokenType.ASSIGN)

        value = self.parse_expression()

        return LetStatement(
            line=name.line,
            column=name.column,
            name=name.value,
            value=value
        )

    def parse_var(self):

        self.match(TokenType.VAR)

        name = self.match(TokenType.IDENTIFIER)

        self.match(TokenType.ASSIGN)

        value = self.parse_expression()

        return VarStatement(
            line=name.line,
            column=name.column,
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
                line=name.line,
                column=name.column,
                object=Identifier(
                    line=name.line,
                    column=name.column,
                    name=name.value
                ),
                index=index,
                value=value
            )

        self.match(TokenType.ASSIGN)

        value = self.parse_expression()

        return AssignmentStatement(
            line=name.line,
            column=name.column,
            name=name.value,
            value=value
        )

    def parse_member_assignment(self, expression):

        self.match(TokenType.ASSIGN)

        value = self.parse_expression()

        if isinstance(expression, MemberExpression):

            return MemberAssignmentStatement(
                line=expression.line,
                column=expression.column,
                object=expression,
                value=value
            )

        raise WizSyntaxError(
            "Invalid assignment target",
            self.current().line,
            self.current().column
        )

    def parse_when(self):

        when = self.match(TokenType.WHEN)

        condition = self.parse_expression()

        self.skip_newlines()

        body = self.parse_block()

        else_body = None

        self.skip_newlines()

        if self.current().type == TokenType.ELSE:

            self.advance()

            self.skip_newlines()

            else_body = self.parse_block()

        return WhenStatement(
            line=when.line,
            column=when.column,
            condition=condition,
            body=body,
            else_body=else_body
        )

    def parse_when_expression(self):

        when = self.match(TokenType.WHEN)

        condition = self.parse_expression()

        consequent = self.parse_when_branch()

        alternate = None

        if self.current().type == TokenType.ELSE:

            self.advance()

            alternate = self.parse_when_branch()

        return WhenExpression(
            line=when.line,
            column=when.column,
            condition=condition,
            consequent=consequent,
            alternate=alternate
        )

    def parse_when_branch(self):

        if self.current().type == TokenType.LBRACE:

            self.advance()

            expression = self.parse_expression()

            self.match(TokenType.RBRACE)

            return expression

        return self.parse_expression()

    def parse_switch(self):

        switch = self.match(TokenType.SWITCH)

        expression = self.parse_expression()

        self.skip_newlines()

        self.match(TokenType.LBRACE)

        self.skip_newlines()

        cases = []
        default = None

        while self.current().type != TokenType.RBRACE:

            if self.current().type == TokenType.NEWLINE:
                self.advance()
                continue

            if self.current().type == TokenType.CASE:

                self.advance()

                value = self.parse_expression()

                self.skip_newlines()

                body = self.parse_block()

                cases.append(
                    SwitchCase(
                        line=value.line,
                        column=value.column,
                        value=value,
                        body=body
                    )
                )

                self.skip_newlines()
                continue

            if self.current().type == TokenType.DEFAULT:

                self.advance()

                self.skip_newlines()

                default = self.parse_block()

                self.skip_newlines()
                continue

            raise WizSyntaxError(
                "Expected 'case' or 'default'",
                self.current().line,
                self.current().column
            )

        self.match(TokenType.RBRACE)

        return SwitchStatement(
            line=switch.line,
            column=switch.column,
            expression=expression,
            cases=cases,
            default=default
        )

    def parse_while(self):

        while_token = self.match(TokenType.WHILE)

        condition = self.parse_expression()

        self.skip_newlines()

        body = self.parse_block()

        return WhileStatement(
            line=while_token.line,
            column=while_token.column,
            condition=condition,
            body=body
        )

    def parse_for(self):

        for_token = self.match(TokenType.FOR)

        variable = self.match(TokenType.IDENTIFIER).value

        self.match(TokenType.IN)

        start = self.parse_expression()

        # Range Mode
        if self.current().type == TokenType.RANGE:

            self.advance()

            end = self.parse_expression()

            step = None

            if self.current().type == TokenType.STEP:
                self.advance()
                step = self.parse_expression()

            self.skip_newlines()

            body = self.parse_block()

            return ForStatement(
                line=for_token.line,
                column=for_token.column,
                variable=variable,
                iterable=None,
                start=start,
                end=end,
                step=step,
                body=body
            )

        # iterable mode
        self.skip_newlines()

        body = self.parse_block()

        return ForStatement(
            line=for_token.line,
            column=for_token.column,
            variable=variable,
            iterable=start,
            start=None,
            end=None,
            step=None,
            body=body
        )

    def parse_class(self):

        self.match(TokenType.CLASS)

        name = self.match(TokenType.IDENTIFIER)

        extends = None

        if self.current().type == TokenType.EXTENDS:

            self.advance()

            parent = self.match(TokenType.IDENTIFIER)

            extends = parent.value

        self.skip_newlines()

        body = self.parse_block()

        return ClassStatement(
            line=name.line,
            column=name.column,
            name=name.value,
            body=body,
            extends=extends
        )

    def parse_function(self, decorators=None):

        if decorators is None:
            decorators = []

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

        if self.current().type == TokenType.ARROW:

            self.advance()

            expression = self.parse_expression()

            body = Block(
                line=expression.line,
                column=expression.column,
                statements=[
                    ReturnStatement(
                        line=expression.line,
                        column=expression.column,
                        value=expression
                    )
                ]
            )

        else:

            body = self.parse_block()

        return FunctionStatement(
            line=name.line,
            column=name.column,
            name=name.value,
            params=params,
            defaults=defaults,
            body=body,
            decorators=decorators
        )

    def parse_function_expression(self):

        func = self.match(TokenType.FUNC)

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

        if self.current().type == TokenType.ARROW:

            self.advance()

            expression = self.parse_expression()

            body = Block(
                line=expression.line,
                column=expression.column,
                statements=[
                    ReturnStatement(
                        line=expression.line,
                        column=expression.column,
                        value=expression
                    )
                ]
            )

        else:

            body = self.parse_block()

        return FunctionExpression(
            line=func.line,
            column=func.column,
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

        return_token = self.match(TokenType.RETURN)

        value = self.parse_expression()

        return ReturnStatement(
            line=return_token.line,
            column=return_token.column,
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

        token = self.match(TokenType.BREAK)

        return BreakStatement(line=token.line,
                        column=token.column)

    def parse_continue(self):

        token = self.match(TokenType.CONTINUE)

        return ContinueStatement(line=token.line,
                        column=token.column)

    def parse_import(self):

        self.match(TokenType.IMPORT)

        module = self.match(TokenType.IDENTIFIER)

        return ImportStatement(
            line=module.line,
            column=module.column,
            module=module.value)

    def parse_list(self):

        lbracket = self.match(TokenType.LBRACKET)
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
            line=lbracket.line,
            column=lbracket.column,
            elements=elements
        )

    def parse_interpolated_string(self):

        token = self.match(TokenType.INTERPOLATED_STRING)

        text = token.value

        parts = []

        i = 0

        while i < len(text):

            if text[i] == "{":

                depth = 1
                end = i + 1

                while end < len(text) and depth > 0:

                    if text[end] == "{":
                        depth += 1

                    elif text[end] == "}":
                        depth -= 1

                    end += 1

                if depth != 0:
                    raise WizSyntaxError(
                        "Missing '}' in interpolated string",
                        token.line,
                        token.column
                    )

                expression = text[i + 1:end - 1].strip()

                lexer = Lexer(expression)
                tokens = lexer.tokenize()

                parser = Parser(tokens)

                node = parser.parse_expression()

                parts.append(node)

                i = end

            else:

                start = i

                while i < len(text) and text[i] != "{":
                    i += 1

                value = text[start:i]

                if value:
                    parts.append(
                        String(
                            line=token.line,
                            column=token.column,
                            value=value
                        )
                    )

        return InterpolatedString(
            line=token.line,
            column=token.column,
            parts=parts
        )

    def parse_decorators(self):

        decorators = []

        while self.current().type == TokenType.HASH:

            decorators.append(self.parse_decorator())

            while self.current().type == TokenType.NEWLINE:
                self.match(TokenType.NEWLINE)

        return decorators

    def parse_decorator(self):

        self.match(TokenType.HASH)

        name_token = self.match(TokenType.IDENTIFIER)

        name = name_token.value

        arguments = []

        if self.current().type == TokenType.LPAREN:

            self.match(TokenType.LPAREN)

            if self.current().type != TokenType.RPAREN:

                while True:

                    arguments.append(self.parse_argument())

                    if self.current().type != TokenType.COMMA:
                        break

                    self.match(TokenType.COMMA)

            self.match(TokenType.RPAREN)

        return Decorator(
            line=name_token.line,
            column=name_token.column,
            name=name,
            arguments=arguments
        )

    def parse_decorator_statement(self):

        self.match(TokenType.DECORATOR)

        name_token = self.match(TokenType.IDENTIFIER)

        name = name_token.value

        self.match(TokenType.LPAREN)

        params = []
        defaults = {}

        if self.current().type != TokenType.RPAREN:

            while True:

                param_name = self.match(TokenType.IDENTIFIER).value

                params.append(param_name)

                if self.current().type == TokenType.ASSIGN:
                    self.advance()
                    defaults[param_name] = self.parse_expression()

                if self.current().type != TokenType.COMMA:
                    break

                self.advance()

        self.match(TokenType.RPAREN)

        self.match(TokenType.LBRACE)

        define = None
        before = None
        after = None
        error = None

        while self.current().type != TokenType.RBRACE:

            self.skip_newlines()

            if self.current().type == TokenType.RBRACE:
                break

            hook_token = self.match(TokenType.IDENTIFIER)

            hook = hook_token.value

            self.match(TokenType.LPAREN)

            depth = 1

            while depth:

                if self.current().type == TokenType.LPAREN:
                    depth += 1

                elif self.current().type == TokenType.RPAREN:
                    depth -= 1

                self.advance()

            block = self.parse_block()

            if hook == "define":
                define = block

            elif hook == "before":
                before = block

            elif hook == "after":
                after = block

            elif hook == "error":
                error = block

            else:
                raise WizSyntaxError(
                    f"Unknown decorator hook '{hook}'",
                    hook_token.line,
                    hook_token.column
                )

            self.skip_newlines()

        self.match(TokenType.RBRACE)

        return DecoratorStatement(
            line=name_token.line,
            column=name_token.column,
            name=name,
            params=params,
            defaults=defaults,
            define=define,
            before=before,
            after=after,
            error=error
        )

    def parse_dict(self):

        lbrace = self.match(TokenType.LBRACE)
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
            line=lbrace.line,
            column=lbrace.column,
            pairs=pairs)

    def parse_statement(self):

        decorators = []

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

            expression = self.parse_expression()

            if self.current().type == TokenType.ASSIGN:
                return self.parse_member_assignment(expression)

            return expression

        if self.current().type == TokenType.WHEN:
            return self.parse_when()

        if self.current().type == TokenType.SWITCH:
            return self.parse_switch()

        if self.current().type == TokenType.FOR:
            return self.parse_for()

        if self.current().type == TokenType.WHILE:
            return self.parse_while()

        if self.current().type == TokenType.BREAK:
            return self.parse_break()

        if self.current().type == TokenType.CONTINUE:
            return self.parse_continue()

        if self.current().type == TokenType.CLASS:
            return self.parse_class()

        if self.current().type == TokenType.IMPORT:
            return self.parse_import()

        if self.current().type == TokenType.HASH:
            decorators = self.parse_decorators()

        if self.current().type == TokenType.FUNC:
            return self.parse_function(decorators)
        
        if self.current().type == TokenType.DECORATOR:
            return self.parse_decorator_statement()

        if self.current().type == TokenType.RETURN:
            return self.parse_return()

        if self.current().type == TokenType.RBRACE:
            return None

        raise WizSyntaxError(
            f"Unexpected {describe_token(self.current())}",
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