from nodes import *
from errors import *
from tokens import TokenType
from lexer import Lexer
from parser import Parser
from runtime import Module
from stdlib import STDLIB
import os


class ReturnException(Exception):

    def __init__(self, value):
        self.value = value

class BreakException(Exception):
    pass


class ContinueException(Exception):
    pass

class Interpreter:

    def __init__(self, base_path="."):
        self.scopes = [
            {}
        ]
        self.functions = {}
        self.stdlib = STDLIB
        self.modules = {}
        self.base_path = base_path
        self.builtins = {
            "str": str,
            "num": int,
            "bool": bool,
            "len": len,
            "echo": print,
            "get": input,
        }
        self.methods = {
            list: {
                "append": lambda obj, *args: obj.append(*args),
                "pop": lambda obj, *args: obj.pop(*args),
                "sort": lambda obj: obj.sort(),
                "reverse": lambda obj: obj.reverse(),
                "remove": lambda obj, *args: obj.remove(*args),
                "insert": lambda obj, *args: obj.insert(*args),
                "copy": lambda obj: obj.copy(),
                "clear": lambda obj: obj.clear(),
                "extend": lambda obj, *args: obj.extend(*args),
                "count": lambda obj, *args: obj.count(*args),
                "index": lambda obj, *args: obj.index(*args),
            },

            dict: {
                "get": lambda obj, *args: obj.get(*args),
                "keys": lambda obj: list(obj.keys()),
                "values": lambda obj: list(obj.values()),
                "items": lambda obj: list(obj.items()),
                "pop": lambda obj, *args: obj.pop(*args),
                "clear": lambda obj: obj.clear(),
                "update": lambda obj, *args: obj.update(*args),
                "copy": lambda obj: obj.copy(),
            },

            str: {
                "upper": lambda obj: obj.upper(),
                "lower": lambda obj: obj.lower(),
                "replace": lambda obj, a, b: obj.replace(a, b),
                "split": lambda obj, sep=None: obj.split(sep),
                "strip": lambda obj, *args: obj.strip(*args),
            },
        }

    def visit(self, node):

        method_name = f"visit_{type(node).__name__}"

        method = getattr(self, method_name, None)

        if method is None:
            raise Exception(f"No visit method for {type(node).__name__}")

        return method(node)

    # Program

    def visit_Program(self, node):

        for statement in node.body:
            self.visit(statement)

    # Statements

    def visit_LetStatement(self, node):

        scope = self.scopes[-1]

        if node.name in scope:
            raise WizVariableDeclared(
                f"Variable '{node.name}' already declared",
                node.line,
                node.column
            )

        value = self.visit(node.value)

        scope[node.name] = {
            "value": value,
            "mutable": False
        }

    def visit_VarStatement(self, node):

        scope = self.scopes[-1]

        if node.name in scope:
            raise WizVariableDeclared(
                f"Variable '{node.name}' already declared",
                node.line,
                node.column
            )

        value = self.visit(node.value)

        scope[node.name] = {
            "value": value,
            "mutable": True
        }

    def visit_AssignmentStatement(self, node):

        variable = self.find_variable(node.name)

        if variable is None:
            raise WizNameError(
                f"Undefined variable '{node.name}'",
                node.line,
                node.column
            )

        if not variable["mutable"]:
            raise WizVariableNotImmutable(
                f"Cannot modify immutable variable '{node.name}'",
                node.line,
                node.column
            )

        value = self.visit(node.value)

        variable["value"] = value

    def visit_EchoStatement(self, node):

        value = self.visit(node.value)

        print(value)

    def visit_WhenStatement(self, node):
    
            condition = self.visit(node.condition)
    
            if condition:
                self.visit(node.body)
    
            elif node.else_body:
                self.visit(node.else_body)

    def visit_WhileStatement(self, node):

        while self.visit(node.condition):

            try:
                self.visit(node.body)

            except BreakException:
                break

            except ContinueException:
                continue

    def visit_ForStatement(self, node):

        # ---------------- Iterable for ----------------

        if node.iterable is not None:

            iterable = self.visit(node.iterable)

            for value in iterable:

                scope = {
                    node.variable: {
                        "value": value,
                        "mutable": True
                    }
                }

                try:
                    self.visit_Block(node.body, scope)

                except BreakException:
                    break

                except ContinueException:
                    continue

            return


        # ---------------- Numeric for ----------------

        start = self.visit(node.start)
        end = self.visit(node.end)

        step = 1 if node.step is None else self.visit(node.step)

        if step == 0:
            raise WizRuntimeError(
                "Step cannot be zero.",
                node.line,
                node.column
            )

        if start <= end:

            current = start

            while current < end:

                scope = {
                    node.variable: {
                        "value": current,
                        "mutable": True
                    }
                }

                try:
                    self.visit_Block(node.body, scope)

                except BreakException:
                    break

                except ContinueException:
                    current += abs(step)
                    continue

                current += abs(step)

        else:

            current = start

            while current > end:

                scope = {
                    node.variable: {
                        "value": current,
                        "mutable": True
                    }
                }

                try:
                    self.visit_Block(node.body, scope)

                except BreakException:
                    break

                except ContinueException:
                    current -= abs(step)
                    continue

                current -= abs(step)

    def visit_FunctionStatement(self, node):

        node.closure = self.scopes.copy()

        self.functions[node.name] = node


    def visit_ReturnStatement(self, node):

        value = self.visit(node.value)

        raise ReturnException(value)

    def visit_BreakStatement(self, node):
        raise BreakException()

    def visit_ContinueStatement(self, node):
        raise ContinueException()

    def visit_IndexAssignmentStatement(self, node):

        obj = self.visit(node.object)

        index = self.visit(node.index)

        value = self.visit(node.value)

        obj[index] = value

    def visit_ImportStatement(self, node):

        if node.module in self.stdlib:

            if node.module not in self.modules:
                self.modules[node.module] = self.stdlib[node.module]()

            self.scopes[0][node.module] = {
                "value": self.modules[node.module],
                "mutable": False
            }

            return
        
        filename = os.path.join(
            self.base_path,
            node.module + ".wiz"
        )


        with open(filename) as file:
            source = file.read()


        lexer = Lexer(source)
        tokens = lexer.tokenize()

        parser = Parser(tokens)
        tree = parser.parse()


        module_scope = {}

        old_scope = self.scopes
        old_functions = self.functions


        self.scopes = [module_scope]
        self.functions = {}


        self.visit(tree)


        module = Module(
            node.module,
            module_scope,
            self.functions
        )


        self.scopes = old_scope
        self.functions = old_functions


        self.scopes[0][node.module] = {
            "value": module,
            "mutable": False
        }

    # Data types

    def visit_String(self, node):
        return node.value

    def visit_InterpolatedString(self, node):

        result = []

        for part in node.parts:

            value = self.visit(part)

            result.append(str(value))

        return "".join(result)

    def visit_Number(self, node):
        return node.value

    def visit_Boolean(self, node):
        return node.value

    def visit_Argument(self, node):
        return self.visit(node.value)

    def visit_Identifier(self, node):

        variable = self.find_variable(node.name)

        if variable is None:
            raise WizNameError(
                f"Undefined variable '{node.name}'",
                node.line,
                node.column
            )

        return variable["value"]

    def visit_Block(self, node, scope=None):

        if scope is None:
            scope = {}

        self.scopes.append(scope)

        try:
            for statement in node.statements:
                self.visit(statement)
        finally:
            self.scopes.pop()

    # Expressions

    def visit_BinaryExpression(self, node):

        left = self.visit(node.left)
        right = self.visit(node.right)

        if node.operator == TokenType.PLUS:
            return left + right

        if node.operator == TokenType.MINUS:
            return left - right

        if node.operator == TokenType.STAR:
            return left * right

        if node.operator == TokenType.SLASH:
            return left / right

        if node.operator == TokenType.MODULO:
            return left % right

        raise WizSyntaxError(
            "Unknown operator",
            node.line,
            node.column)

    def visit_ComparisonExpression(self, node):

        left = self.visit(node.left)
        right = self.visit(node.right)

        if node.operator == TokenType.GREATER:
            return left > right

        if node.operator == TokenType.LESS:
            return left < right

        if node.operator == TokenType.GREATER_EQUAL:
            return left >= right

        if node.operator == TokenType.LESS_EQUAL:
            return left <= right

        if node.operator == TokenType.EQUAL:
            return left == right

        if node.operator == TokenType.NOT_EQUAL:
            return left != right

        raise WizSyntaxError(
            "Unknown comparison operator",
            node.line,
            node.column)

    def visit_CallExpression(self, node):

        # ---------------- Built-in functions ----------------

        if node.name in self.builtins:

            args = []
            kwargs = {}

            for argument in node.arguments:

                value = self.visit(argument.value)

                if argument.name is None:
                    args.append(value)
                else:
                    kwargs[argument.name] = value

            return self.builtins[node.name](*args, **kwargs)

        # ---------------- User functions ----------------

        if node.name not in self.functions:
            raise WizRuntimeError(
                f"Undefined function '{node.name}'",
                node.line,
                node.column
            )

        function = self.functions[node.name]

        scope = {}

        used = set()
        positional_index = 0

        for argument in node.arguments:

            value = self.visit(argument.value)

            # ---------- Named argument ----------
            if argument.name is not None:

                if argument.name not in function.params:
                    raise WizParameterError(
                        f"Unknown parameter '{argument.name}'",
                        node.line,
                        node.column
                    )

                if argument.name in used:
                    raise WizParameterError(
                        f"Parameter '{argument.name}' already assigned",
                        node.line,
                        node.column
                    )

                scope[argument.name] = {
                    "value": value,
                    "mutable": True
                }

                used.add(argument.name)

            # ---------- Positional argument ----------
            else:

                while (
                    positional_index < len(function.params)
                    and function.params[positional_index] in used
                ):
                    positional_index += 1

                if positional_index >= len(function.params):
                    raise WizRuntimeError(
                        f"Too many arguments for function '{node.name}'",
                        node.line,
                        node.column
                    )

                param = function.params[positional_index]

                scope[param] = {
                    "value": value,
                    "mutable": True
                }

                used.add(param)
                positional_index += 1

        # ---------- Missing parameters ----------

        for param in function.params:

            if param in scope:
                continue

            if param in function.defaults:

                scope[param] = {
                    "value": self.visit(function.defaults[param]),
                    "mutable": True
                }

            else:

                raise WizRuntimeError(
                    f"Missing required parameter '{param}'",
                    node.line,
                    node.column
                )

        try:
            return self.visit_Block(function.body, scope)

        except ReturnException as e:
            return e.value

        return None

    def visit_LogicalExpression(self, node):
    
            left = self.visit(node.left)
    
            if node.operator == TokenType.AND:
                return left and self.visit(node.right)
    
            if node.operator == TokenType.OR:
                return left or self.visit(node.right)
    
            raise WizSyntaxError(
                "Unknown logical operator",
                node.line,
                node.column)
    
    def visit_UnaryExpression(self, node):

        value = self.visit(node.operand)

        if node.operator == TokenType.NOT:
            return not value

        if node.operator == TokenType.MINUS:
            return -value

        if node.operator == TokenType.PLUS:
            return +value

        raise WizSyntaxError(
            "Unknown unary operator",
            node.line,
            node.column
        )

    def visit_IndexExpression(self, node):

        obj = self.visit(node.object)
        index = self.visit(node.index)

        try:

            return obj[index]

        except IndexError:

            raise WizIndexError(
                f"Index {index} out of range",
                node.line,
                node.column
            )

        except KeyError:

            raise WizKeyError(
                f"Key '{index}' not found",
                node.line,
                node.column
            )

        except TypeError:

            raise WizTypeError(
                f"Type '{type(obj).__name__}' does not support indexing",
                node.line,
                node.column
            )

    def visit_MethodCallExpression(self, node):

        obj = self.visit(node.object)

        if hasattr(obj, "functions"):

            func = obj.functions.get(node.method)

            if func is None:
                raise WizRuntimeError(
                    f"Module has no function '{node.method}'",
                    node.line,
                    node.column
                )

            arguments = [
                self.visit(arg)
                for arg in node.arguments
            ]

            if callable(func):
                return func(*arguments)

            scope = {}

            for param, value in zip(
                func.params,
                arguments
            ):
                scope[param] = {
                    "value": value,
                    "mutable": True
                }

            old_scopes = self.scopes

            self.scopes = func.closure + [scope]

            try:
                return self.visit_Block(
                    func.body,
                    scope
                )

            except ReturnException as e:
                return e.value

            finally:
                self.scopes = old_scopes

        methods = self.methods.get(type(obj))

        if methods:
            method = methods.get(node.method)

            if method:
                arguments = [
                    self.visit(arg)
                    for arg in node.arguments
                ]

                return method(obj, *arguments)

        raise WizTypeError(
            f"This type has no methods: {type(obj).__name__}",
            node.line,
            node.column
        )

    def visit_MemberCallExpression(self, node):

        obj = self.visit(node.object)

        arguments = [
            self.visit(arg)
            for arg in node.arguments
        ]


        # Module functions
        if isinstance(obj, Module):

            func = obj.functions.get(node.function)

            if func is None:
                raise WizRuntimeError(
                    f"Module has no function '{node.function}'",
                    node.line,
                    node.column
                )


            scope = {}

            for param, value in zip(
                func.params,
                arguments
            ):
                scope[param] = {
                    "value": value,
                    "mutable": True
                }


            try:
                return self.visit_Block(
                    func.body,
                    scope
                )

            except ReturnException as e:
                return e.value


        # Object methods
        methods = self.methods.get(type(obj))

        if methods:

            method = methods.get(node.function)

            if method:

                return method(
                    obj,
                    *arguments
                )


        raise WizRuntimeError(
            f"'{node.function}' is not callable on {type(obj).__name__}",
            node.line,
            node.column
        )

    def visit_MemberExpression(self, node):

        obj = self.visit(node.object)

        # Module access
        if hasattr(obj, "get"):

            value = obj.get(node.property)

            if value is None:
                raise WizMemberError(
                    f"No member '{node.property}' in module '{obj.name}'",
                    node.line,
                    node.column
                )

            return value


        # Dictionary access
        if isinstance(obj, dict):

            if node.property in obj:
                return obj[node.property]

            raise WizKeyError(
                f"Key '{node.property}' not found",
                node.line,
                node.column
            )


        # Object attribute access
        if hasattr(obj, node.property):

            return getattr(obj, node.property)


        raise WizMemberError(
            f"Cannot access member '{node.property}' on {type(obj).__name__}",
            node.line,
            node.column
        )

    def visit_FunctionCallExpression(self, node):

        func = self.visit(node.function)

        if isinstance(func, FunctionStatement):

            scope = {}

            for param, arg in zip(
                func.params,
                node.arguments
            ):
                scope[param] = {
                    "value": self.visit(arg),
                    "mutable": True
                }

            try:
                return self.visit_Block(func.body, scope)

            except ReturnException as e:
                return e.value

    # Literals

    def visit_DictLiteral(self, node):

        result = {}

        for pair in node.pairs:
            key = self.visit(pair.key)
            value = self.visit(pair.value)

            result[key] = value

        return result

    def visit_ListLiteral(self, node):

        return [
            self.visit(element)
            for element in node.elements
        ]

    # Utils

    def push_scope(self):
        self.scopes.append({})

    def pop_scope(self):
        self.scopes.pop()


    def find_variable(self, name):

        for scope in reversed(self.scopes):

            if name in scope:
                return scope[name]

        return None