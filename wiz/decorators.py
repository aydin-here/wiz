import time
from errors import *

class DecoratorRuntime:

    def define(self, ctx):
        pass

    def before(self, ctx, state):
        pass

    def after(self, ctx, state):
        pass

    def error(self, ctx):
        pass

class DecoratorState:
    pass

class DecoratorInfo:

    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments

class UserDecorator(DecoratorRuntime):

    def __init__(self, statement):
        self.statement = statement

    def build_scope(self, ctx, state):

        info = ctx.function._decorator

        scope = {
            "ctx": {
                "value": ctx,
                "mutable": False
            }
        }

        if state is not None:
            scope["state"] = {
                "value": state,
                "mutable": False
            }

        used = set()
        positional_index = 0

        for argument in info.arguments:

            value = ctx.interpreter.visit(argument.value)

            # ---------- Named argument ----------
            if argument.name is not None:

                if argument.name not in self.statement.params:
                    raise WizRuntimeError(
                        f"Unknown parameter '{argument.name}' for decorator '{self.statement.name}'",
                        argument.line,
                        argument.column
                    )

                if argument.name in used:
                    raise WizRuntimeError(
                        f"Parameter '{argument.name}' already assigned",
                        argument.line,
                        argument.column
                    )

                scope[argument.name] = {
                    "value": value,
                    "mutable": False
                }

                used.add(argument.name)

            # ---------- Positional argument ----------
            else:

                while (
                    positional_index < len(self.statement.params)
                    and self.statement.params[positional_index] in used
                ):
                    positional_index += 1

                if positional_index >= len(self.statement.params):
                    raise WizRuntimeError(
                        f"Too many arguments for decorator '{self.statement.name}'",
                        argument.line,
                        argument.column
                    )

                param = self.statement.params[positional_index]

                scope[param] = {
                    "value": value,
                    "mutable": False
                }

                used.add(param)
                positional_index += 1

        # ---------- Missing parameters ----------

        for param in self.statement.params:

            if param in scope:
                continue

            if param in self.statement.defaults:

                scope[param] = {
                    "value": ctx.interpreter.visit(
                        self.statement.defaults[param]
                    ),
                    "mutable": False
                }

            else:

                raise WizRuntimeError(
                    f"Missing required parameter '{param}' for decorator '{self.statement.name}'",
                    self.statement.line,
                    self.statement.column
                )

        return scope

    def define(self, ctx):

        if self.statement.define is None:
            return

        ctx.interpreter.visit_Block(
            self.statement.define,
            self.build_scope(ctx, None)
        )

    def before(self, ctx, state):

        if self.statement.before is None:
            return

        self.statement.closure = ctx.interpreter.scopes.copy()

        ctx.interpreter.visit_Block(
            self.statement.before,
            self.build_scope(ctx, state)
        )

    def after(self, ctx, state):

        if self.statement.after is None:
            return

        ctx.interpreter.visit_Block(
            self.statement.after,
            self.build_scope(ctx, state)
        )

    def error(self, ctx):

        if self.statement.error is None:
            return

        ctx.interpreter.visit_Block(
            self.statement.error,
            self.build_scope(ctx, None)
        )

class DecoratorContext:

    def __init__(self, interpreter, function):
        self.interpreter = interpreter
        self.function = function
        self.result = None

    def call(self):

        scope = {}

        return self.interpreter.visit_Block(
            self.function.body,
            scope
        )

class TimerDecorator(DecoratorRuntime):

    def before(self, ctx, state):
        state.start = time.time()

    def after(self, ctx, state):
        print(time.time() - state.start)

class DeprecatedDecorator(DecoratorRuntime):

    def before(self, ctx, state):
        print(f"Warning: {ctx.function.name} is deprecated")

    def after(self, ctx, state):
        return super().after(ctx, state)