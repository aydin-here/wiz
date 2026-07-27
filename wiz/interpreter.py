from nodes import *
from tokens import TokenType
from lexer import Lexer
from parser import Parser
from runtime import Module
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
            raise Exception(
                f"Variable '{node.name}' already declared"
            )

        value = self.visit(node.value)

        scope[node.name] = {
            "value": value,
            "mutable": False
        }

    def visit_VarStatement(self, node):

        scope = self.scopes[-1]

        if node.name in scope:
            raise Exception(
                f"Variable '{node.name}' already declared"
            )

        value = self.visit(node.value)

        scope[node.name] = {
            "value": value,
            "mutable": True
        }

    def visit_AssignmentStatement(self, node):

        variable = self.find_variable(node.name)

        if variable is None:
            raise Exception(
                f"Undefined variable '{node.name}'"
            )

        if not variable["mutable"]:
            raise Exception(
                f"Cannot modify immutable variable '{node.name}'"
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

    def visit_Number(self, node):
        return node.value

    def visit_Boolean(self, node):
        return node.value

    def visit_Identifier(self, node):

        variable = self.find_variable(node.name)

        if variable is None:
            raise Exception(
                f"Undefined variable '{node.name}'"
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

        raise Exception("Unknown operator")

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

        raise Exception("Unknown comparison operator")

    def visit_CallExpression(self, node):
    
            # Built-in functions
            if node.name in self.builtins:
    
                arguments = [
                    self.visit(argument)
                    for argument in node.arguments
                ]
    
                return self.builtins[node.name](*arguments)
    
            # User-defined functions
            if node.name not in self.functions:
                raise Exception(
                    f"Undefined function '{node.name}'"
                )
    
            function = self.functions[node.name]
    
            if len(node.arguments) != len(function.params):
                raise Exception(
                    f"Function '{node.name}' expects "
                    f"{len(function.params)} arguments, "
                    f"got {len(node.arguments)}"
                )
    
            scope = {}

            for param, argument in zip(function.params, node.arguments):
                scope[param] = {
                    "value": self.visit(argument),
                    "mutable": True
                }

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
    
            raise Exception("Unknown logical operator")
    
    def visit_UnaryExpression(self, node):
    
        value = self.visit(node.operand)
    
        if node.operator == TokenType.NOT:
            return not value
    
        raise Exception("Unknown unary operator")

    def visit_IndexExpression(self, node):

        obj = self.visit(node.object)
        index = self.visit(node.index)

        try:

            return obj[index]

        except IndexError:

            raise Exception(
                f"Index {index} out of range"
            )

        except KeyError:

            raise Exception(
                f"Key '{index}' not found"
            )

        except TypeError:

            raise Exception(
                f"Type '{type(obj).__name__}' does not support indexing"
            )

    def visit_MethodCallExpression(self, node):

        obj = self.visit(node.object)

        if isinstance(obj, Module):

            func = obj.functions.get(node.method)

            if func is None:
                raise Exception(
                    f"Module has no function '{node.method}'"
                )

            arguments = [
                self.visit(arg)
                for arg in node.arguments
            ]

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


        raise Exception(
            f"This type has no methods: {type(obj).__name__}"
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
                raise Exception(
                    f"Module has no function '{node.function}'"
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


        raise Exception(
            f"'{node.function}' is not callable on {type(obj).__name__}"
        )

    def visit_MemberExpression(self, node):

        obj = self.visit(node.object)

        # Module access
        if isinstance(obj, Module):

            value = obj.get(node.property)

            if value is None:
                raise Exception(
                    f"No member '{node.property}' in module '{obj.name}'"
                )

            return value


        # Dictionary access
        if isinstance(obj, dict):

            if node.property in obj:
                return obj[node.property]

            raise Exception(
                f"Key '{node.property}' not found"
            )


        # Object attribute access
        if hasattr(obj, node.property):

            return getattr(obj, node.property)


        raise Exception(
            f"Cannot access member '{node.property}' on {type(obj).__name__}"
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