from nodes import *
from errors import *
from tokens import TokenType
from lexer import Lexer
from parser import Parser
from runtime import Module, WizClass, WizInstance, Super
from stdlib import STDLIB
from decorators import *
from package_loader import PackageLoader, PackageResolution


def to_display(value, nested=False):
    if value is None:
        return "null"
    if isinstance(value, list):
        return "[" + ", ".join(
            to_display(item, True) for item in value
        ) + "]"
    if isinstance(value, dict):
        return "{" + ", ".join(
            to_display(key, True) + ": " + to_display(item, True)
            for key, item in value.items()
        ) + "}"
    if isinstance(value, str):
        return repr(value) if nested else value
    return str(value)


class ReturnException(Exception):

    def __init__(self, value):
        self.value = value

class BreakException(Exception):
    pass


class ContinueException(Exception):
    pass


#: Hidden key stored in every module scope so imports resolve relative
#: to the module's own directory (needed for multi-file Wiz packages).
#: The NUL character cannot appear in a Wiz source file, so this can
#: never collide with a real variable name.
_MODULE_DIR_KEY = "\0wiz_module_dir"

class WizFunction:
    def __init__(self, statement, interpreter=None):
        self.statement = statement
        self.interpreter = interpreter

    def __call__(self, *args, **kwargs):
        if self.interpreter is None:
            raise RuntimeError(
                "This Wiz function has no attached interpreter"
            )
        return self.interpreter.call_wiz_function(self, args, kwargs)

class Interpreter:

    def __init__(self, base_path="."):
        self.scopes = [
            {}
        ]
        self.functions = {}
        self.classes = {}
        self.stdlib = STDLIB
        self.modules = {}
        self.base_path = base_path
        self.package_loader = PackageLoader(base_path)
        self.builtins = {
            "str": to_display,
            "num": int,
            "bool": bool,
            "len": len,
            "echo": self._echo,
            "get": input,
        }
        self.decorators = {
            "timer": TimerDecorator(),
            "deprecated": DeprecatedDecorator(),
        }
        self.context_methods = {
            "call": self.decorator_call
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

    def _echo(self, *args, **kwargs):
        print(*(to_display(arg) for arg in args), **kwargs)

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

    def visit_WhenStatement(self, node):
    
        condition = self.visit(node.condition)
    
        if condition:
            self.visit(node.body)
    
        elif node.else_body:
            self.visit(node.else_body)

    def visit_WhenExpression(self, node):

        condition = self.visit(node.condition)

        if condition:
            return self.visit(node.consequent)

        if node.alternate is not None:
            return self.visit(node.alternate)

        return None

    def visit_NullCoalesceExpression(self, node):

        left = self.visit(node.left)

        if left is None:
            return self.visit(node.right)

        return left

    def visit_SafeValue(self, node):

        value = self.visit(node.value)

        if value is None:
            return "null"

        return value

    def visit_SwitchStatement(self, node):

        expression = self.visit(node.expression)

        for case in node.cases:
            case = self.visit(case)

            if expression == case["value"]:
                self.visit(case["body"])
                break
        else:
            if node.default is not None:
                self.visit(node.default)

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

        for decorator in node.decorators:
            self.apply_decorator(node, decorator)

        node.closure = self.scopes.copy()

        self.functions[node.name] = WizFunction(node, self)

    def visit_FunctionExpression(self, node):

        node.closure = self.scopes.copy()

        return WizFunction(node, self)

    def visit_ClassStatement(self, node):

        parent = None

        if node.extends is not None:

            if node.extends not in self.classes:
                raise WizNameError(
                    f"Undefined class '{node.extends}'",
                    node.line,
                    node.column
                )

            parent = self.classes[node.extends]

        klass = WizClass(node.name, node, parent)

        klass.define(self)

        self.classes[node.name] = klass

    def visit_DecoratorStatement(self, node):

        self.decorators[node.name] = UserDecorator(node)

    def visit_ReturnStatement(self, node):

        value = self.visit(node.value)

        raise ReturnException(value)

    def visit_ThrowStatement(self, node):

        value = self.visit(node.value)

        raise WizThrowError(
            to_display(value),
            node.line,
            node.column,
            value=value
        )

    def visit_TryCatchStatement(self, node):

        try:
            self.visit(node.body)

        except WizThrowError as error:

            if node.catch_body is not None:

                scope = {
                    node.catch_variable: {
                        "value": error.value,
                        "mutable": True
                    }
                }

                self.visit_Block(node.catch_body, scope)

        except WizError as error:

            if node.catch_body is not None:

                scope = {
                    node.catch_variable: {
                        "value": error.message,
                        "mutable": True
                    }
                }

                self.visit_Block(node.catch_body, scope)

        finally:

            if node.finally_body is not None:
                self.visit_Block(node.finally_body)

    def visit_BreakStatement(self, node):
        raise BreakException()

    def visit_ContinueStatement(self, node):
        raise ContinueException()

    def visit_IndexAssignmentStatement(self, node):

        obj = self.visit(node.object)

        index = self.visit(node.index)

        value = self.visit(node.value)

        obj[index] = value

    def visit_MemberAssignmentStatement(self, node):

        target = node.object

        if isinstance(target, MemberExpression):

            obj = self.visit(target.object)

            value = self.visit(node.value)

            if isinstance(obj, WizInstance):

                obj.attributes[target.property] = value

                return

            raise WizTypeError(
                f"Cannot assign to member '{target.property}' on {type(obj).__name__}",
                node.line,
                node.column
            )

        raise WizTypeError(
            "Invalid assignment target",
            node.line,
            node.column
        )

    def _find_module(self, module):

        resolution = self.package_loader.find(module)

        if resolution is None:
            return None

        return resolution.entry

    def _current_module_dir(self):
        """Directory of the module whose body is currently executing.

        Scans the active scope stack for the hidden module-dir marker
        that every module scope carries. Because function closures keep
        their module scope, this also works for imports issued from
        module functions. Returns None when running project code.
        """

        for scope in reversed(self.scopes):

            if _MODULE_DIR_KEY in scope:
                return scope[_MODULE_DIR_KEY]["value"]

        return None

    def visit_ImportStatement(self, node):

        # ---------------- Built-in stdlib modules ----------------
        # stdlib modules cannot be shadowed by external packages.
        if node.module in self.stdlib:

            if node.module not in self.modules:

                instance = self.stdlib[node.module]()

                if hasattr(instance, "interpreter"):
                    instance.interpreter = self

                self.modules[node.module] = instance

            self.scopes[0][node.module] = {
                "value": self.modules[node.module],
                "mutable": False
            }

            return

        # ---------------- External packages ----------------
        # Imports inside a module resolve relative to that module's own
        # directory first, so multi-file Wiz packages can import their
        # sibling files (e.g. main.wiz importing util.wiz).
        resolution = None

        module_dir = self._current_module_dir()

        if module_dir is not None:

            sibling = os.path.join(module_dir, node.module + ".wiz")

            if os.path.isfile(sibling):
                resolution = PackageResolution(
                    node.module,
                    "wiz",
                    entry=sibling
                )

        if resolution is None:
            resolution = self.package_loader.find(node.module)

        if resolution is None:
            raise PackageNotFoundError(
                f"Module '{node.module}' not found. "
                "Make sure the file exists or install it with "
                "'wiz install <owner/repo>'.",
                node.line,
                node.column
            )

        # ---------------- Python packages ----------------
        if resolution.kind == "python":

            if node.module not in self.modules:

                instance = self.package_loader.load_python(
                    resolution,
                    self
                )

                self.modules[node.module] = instance

            self.scopes[0][node.module] = {
                "value": self.modules[node.module],
                "mutable": False
            }

            return

        # ---------------- Wiz modules and packages ----------------
        filename = resolution.entry

        with open(filename) as file:
            source = file.read()


        lexer = Lexer(source)
        tokens = lexer.tokenize()

        parser = Parser(tokens)
        tree = parser.parse()


        module_scope = {}

        # Hidden marker so imports inside this module (and inside its
        # functions, which capture this scope in their closure) resolve
        # relative to the module's own directory.
        module_scope[_MODULE_DIR_KEY] = {
            "value": os.path.dirname(filename),
            "mutable": False
        }

        old_scope = self.scopes
        old_functions = self.functions


        self.scopes = [module_scope]
        self.functions = {}
        self.classes = {}


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

            result.append(to_display(value))

        return "".join(result)

    def visit_Number(self, node):
        return node.value

    def visit_Boolean(self, node):
        return node.value

    def visit_Null(self, node):
        return None

    def visit_Argument(self, node):
        return self.visit(node.value)

    def visit_Identifier(self, node):

        variable = self.find_variable(node.name)

        if variable is None:

            if node.name in self.functions:
                return self.functions[node.name]

            if node.name in self.classes:
                return self.classes[node.name]

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

    def visit_SwitchCase(self, node):
        return {
            "value": self.visit(node.value),
            "body": node.body
        }

    # Expressions

    def visit_BinaryExpression(self, node):

        left = self.visit(node.left)
        right = self.visit(node.right)

        if node.operator == TokenType.PLUS:
            if isinstance(left, str) and right is None:
                return left
            if isinstance(right, str) and left is None:
                return right
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

            if node.name == "echo":

                for value in args:

                    if value is None:
                        raise WizNullError(
                            f"Cannot echo a null value; "
                            "use '?' to print it",
                            node.line,
                            node.column
                        )

            return self.builtins[node.name](*args, **kwargs)

        # ---------------- User functions ----------------

        variable = self.find_variable(node.name)

        if variable is not None:

            func = variable["value"]

            if isinstance(func, WizFunction):

                function = func.statement

                scope = {}

                for param, arg in zip(
                    function.params,
                    node.arguments
                ):
                    scope[param] = {
                        "value": self.visit(arg.value),
                        "mutable": True
                    }

                for param in function.params:

                    if param not in scope:

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

                old_scopes = self.scopes

                self.scopes = function.closure + [scope]

                try:
                    return self.visit_Block(
                        function.body,
                        scope
                    )

                except ReturnException as e:
                    return e.value

                finally:
                    self.scopes = old_scopes

            # A stored callable, e.g. a native package function.
            if callable(func):

                args = []
                kwargs = {}

                for argument in node.arguments:

                    value = self.visit(argument.value)

                    if argument.name is None:
                        args.append(value)
                    else:
                        kwargs[argument.name] = value

                return func(*args, **kwargs)

        # ---------------- Classes ----------------

        if node.name in self.classes:

            klass = self.classes[node.name]

            return klass.instantiate(self, node)

        if node.name not in self.functions:
            raise WizRuntimeError(
                f"Undefined function '{node.name}'",
                node.line,
                node.column
            )

        function = self.functions[node.name].statement

        scope = self.bind_arguments(function, node)

        decorator_states = []

        for decorator in function.decorators:

            function._decorator = decorator

            runtime = self.decorators.get(decorator.name)

            if runtime:

                ctx = DecoratorContext(
                    self,
                    function
                )

                state = DecoratorState()

                runtime.before(ctx, state)

                decorator_states.append(
                    (runtime, ctx, state)
                )

        try:

            result = self.visit_Block(function.body, scope)

        except ReturnException as e:

            result = e.value

        except Exception:

            for runtime, ctx, state in decorator_states:
                runtime.error(ctx)

            raise

        for runtime, ctx, state in decorator_states:

            ctx.result = result

            runtime.after(ctx, state)

        return result

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

        if node.safe and obj is None:
            return None

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

        if node.safe and obj is None:
            return None

        if type(obj).__name__ == "DecoratorContext":

            method = self.context_methods.get(node.method)

            if method:

                arguments = [
                    self.visit(arg)
                    for arg in node.arguments
                ]

                return method(
                    obj,
                    *arguments
                )

        if isinstance(obj, Super):

            parent = obj.klass.parent

            resolved = (
                parent.find_method(node.method)
                if parent is not None
                else None
            )

            if resolved is None:
                raise WizRuntimeError(
                    f"Class '{obj.klass.name}' has no super method '{node.method}'",
                    node.line,
                    node.column
                )

            method, owner = resolved

            scope = self.bind_arguments(method, node)

            scope["self"] = {
                "value": obj.instance,
                "mutable": True
            }

            if owner.parent is not None:
                scope["super"] = {
                    "value": Super(owner, obj.instance),
                    "mutable": True
                }

            old_scopes = self.scopes

            self.scopes = method.closure + [scope]

            try:
                return self.visit_Block(method.body, scope)

            except ReturnException as e:
                return e.value

            finally:
                self.scopes = old_scopes

        if isinstance(obj, WizInstance):

            resolved = obj.klass.find_method(node.method)

            if resolved is None:
                raise WizRuntimeError(
                    f"Class '{obj.klass.name}' has no method '{node.method}'",
                    node.line,
                    node.column
                )

            method, owner = resolved

            scope = self.bind_arguments(method, node)

            scope["self"] = {
                "value": obj,
                "mutable": True
            }

            if owner.parent is not None:
                scope["super"] = {
                    "value": Super(owner, obj),
                    "mutable": True
                }

            old_scopes = self.scopes

            self.scopes = method.closure + [scope]

            try:
                return self.visit_Block(method.body, scope)

            except ReturnException as e:
                return e.value

            finally:
                self.scopes = old_scopes

        if hasattr(obj, "functions"):

            func = obj.functions.get(node.method)

            if func is None:
                raise WizRuntimeError(
                    f"Module has no function '{node.method}'",
                    node.line,
                    node.column
                )

            args = []
            kwargs = {}

            for argument in node.arguments:

                value = self.visit(argument.value)

                if argument.name is None:
                    args.append(value)
                else:
                    kwargs[argument.name] = value

            if callable(func):
                return func(*args, **kwargs)

            if isinstance(func, WizFunction):
                func = func.statement

            scope = {}

            for param, value in zip(
                func.params,
                args
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

        if node.safe and obj is None:
            return None

        args = []
        kwargs = {}

        for argument in node.arguments:

            value = self.visit(argument.value)

            if argument.name is None:
                args.append(value)
            else:
                kwargs[argument.name] = value


        # Module functions
        if isinstance(obj, Module):

            func = obj.functions.get(node.function)

            if func is None:
                raise WizRuntimeError(
                    f"Module has no function '{node.function}'",
                    node.line,
                    node.column
                )

            if isinstance(func, WizFunction):
                func = func.statement

            scope = {}

            for param, value in zip(
                func.params,
                args
            ):
                scope[param] = {
                    "value": value,
                    "mutable": True
                }

            for name, value in kwargs.items():
                scope[name] = {
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


        # Instance methods
        if isinstance(obj, WizInstance):

            resolved = obj.klass.find_method(node.function)

            if resolved is None:
                raise WizRuntimeError(
                    f"Class '{obj.klass.name}' has no method '{node.function}'",
                    node.line,
                    node.column
                )

            method, owner = resolved

            scope = {}
            scope["self"] = {
                "value": obj,
                "mutable": True
            }

            if owner.parent is not None:
                scope["super"] = {
                    "value": Super(owner, obj),
                    "mutable": True
                }

            for param, value in zip(
                method.params,
                args
            ):
                scope[param] = {
                    "value": value,
                    "mutable": True
                }

            for name, value in kwargs.items():
                scope[name] = {
                    "value": value,
                    "mutable": True
                }

            old_scopes = self.scopes

            self.scopes = method.closure + [scope]

            try:
                return self.visit_Block(method.body, scope)

            except ReturnException as e:
                return e.value

            finally:
                self.scopes = old_scopes

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

        if node.safe and obj is None:
            return None

        # Dictionary access
        if isinstance(obj, dict):

            if node.property in obj:
                return obj[node.property]

            raise WizKeyError(
                f"Key '{node.property}' not found",
                node.line,
                node.column
            )

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


        # Instance attribute access
        if isinstance(obj, WizInstance):

            if node.property in obj.attributes:
                return obj.attributes[node.property]

            value = obj.klass.find_variable(node.property)

            if value is not None:
                return value

            raise WizMemberError(
                f"Class '{obj.klass.name}' has no attribute '{node.property}'",
                node.line,
                node.column
            )


        # Class member access
        if isinstance(obj, WizClass):

            value = obj.find_variable(node.property)

            if value is not None:
                return value

            resolved = obj.find_method(node.property)

            if resolved is not None:
                return resolved[0]

            raise WizMemberError(
                f"Class '{obj.name}' has no member '{node.property}'",
                node.line,
                node.column
            )


        # Super access
        if isinstance(obj, Super):

            instance = obj.instance

            if node.property in instance.attributes:
                return instance.attributes[node.property]

            value = obj.klass.find_variable(node.property)

            if value is not None:
                return value

            raise WizMemberError(
                f"Class '{obj.klass.name}' has no super member '{node.property}'",
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

    def apply_decorator(self, function, decorator):

        runtime = self.decorators.get(decorator.name)

        if runtime is None:
            raise WizRuntimeError(
                f"Unknown decorator '{decorator.name}'",
                decorator.line,
                decorator.column
            )

        if not hasattr(function, "decorators_runtime"):
            function.decorators_runtime = []

        function.decorators_runtime.append({
            "runtime": runtime,
            "arguments": decorator.arguments
        })

        function._decorator = decorator

        runtime.define(
            DecoratorContext(self, function)
        )

    def decorator_call(self, ctx, *args):

        function = ctx.function

        scope = {}

        for param, arg in zip(
            function.params,
            args
        ):
            scope[param] = {
                "value": self.visit(arg),
                "mutable": True
            }

        try:
            return self.visit_Block(
                function.body,
                scope
            )

        except ReturnException as e:
            return e.value

    def find_variable(self, name):

        for scope in reversed(self.scopes):

            if name in scope:
                return scope[name]

        return None

    def bind_arguments(self, function, node):

        scope = {}

        used = set()
        positional_index = 0

        for argument in node.arguments:

            value = self.visit(argument.value)

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

            else:

                while (
                    positional_index < len(function.params)
                    and function.params[positional_index] in used
                ):
                    positional_index += 1

                if positional_index >= len(function.params):
                    raise WizRuntimeError(
                        f"Too many arguments for function '{function.name}'",
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

        return scope

    def call_wiz_function(self, wiz_function, args=None, kwargs=None):

        from errors import WizRuntimeError

        function = wiz_function.statement

        args = list(args or [])
        kwargs = dict(kwargs or {})

        scope = {}

        used = set()
        positional_index = 0

        for value in args:

            while (
                positional_index < len(function.params)
                and function.params[positional_index] in used
            ):
                positional_index += 1

            if positional_index >= len(function.params):
                raise WizRuntimeError(
                    f"Too many arguments for function '{function.name}'"
                )

            param = function.params[positional_index]

            scope[param] = {"value": value, "mutable": True}

            used.add(param)
            positional_index += 1

        for name, value in kwargs.items():

            if name not in function.params:
                raise WizRuntimeError(
                    f"Unknown parameter '{name}'"
                )

            if name in used:
                raise WizRuntimeError(
                    f"Parameter '{name}' already assigned"
                )

            scope[name] = {"value": value, "mutable": True}

            used.add(name)

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
                    f"Missing required parameter '{param}'"
                )

        decorator_states = []

        for decorator in getattr(function, "decorators", []):

            function._decorator = decorator

            runtime = self.decorators.get(decorator.name)

            if runtime:

                ctx = DecoratorContext(self, function)

                state = DecoratorState()

                runtime.before(ctx, state)

                decorator_states.append((runtime, ctx, state))

        old_scopes = self.scopes

        self.scopes = function.closure + [scope]

        try:

            result = self.visit_Block(function.body, scope)

        except ReturnException as e:

            result = e.value

        except Exception:

            for runtime, ctx, state in decorator_states:
                runtime.error(ctx)

            raise

        finally:

            self.scopes = old_scopes

        for runtime, ctx, state in decorator_states:

            ctx.result = result

            runtime.after(ctx, state)

        return result