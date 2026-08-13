from errors import WizError
from lexer import Lexer
from nodes import *
from parser import Parser


BUILTIN_FUNCTIONS = {"echo", "get", "len", "str", "num", "bool"}
BUILTIN_DECORATORS = {"timer", "deprecated"}


class _Scope:

    def __init__(self):
        self.variables = {}


class Linter:

    def __init__(self, source, filename=None):
        self.source = source
        self.filename = filename
        self.issues = []
        self.scopes = [_Scope()]
        self.loop_depth = 0
        self.function_depth = 0
        self.class_depth = 0
        self.referenced_names = set()
        self.defined_functions = {}
        self.defined_classes = set()
        self.defined_decorators = set()

    def run(self):

        self._style_checks()

        try:
            lexer = Lexer(self.source)
            tokens = lexer.tokenize()

            parser = Parser(tokens)
            tree = parser.parse()

        except WizError as error:
            self.issues.append({
                "code": "E001",
                "message": error.message,
                "line": error.line or 1,
                "column": error.column or 1,
                "severity": "error"
            })
            return self._sorted()

        self._collect_definitions(tree)

        self._walk(tree)

        self._report_unused_functions()

        return self._sorted()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _add(self, code, message, line, column, severity):
        self.issues.append({
            "code": code,
            "message": message,
            "line": line,
            "column": column,
            "severity": severity
        })

    def _sorted(self):
        return sorted(
            self.issues,
            key=lambda issue: (issue["line"], issue["column"], issue["code"])
        )

    def _children(self, node):

        for value in vars(node).values():

            if isinstance(value, Node):
                yield value

            elif isinstance(value, list):

                for item in value:

                    if isinstance(item, Node):
                        yield item

    def _collect_definitions(self, node):
        self._collect_node(node, in_class=False)

    def _collect_node(self, node, in_class):

        if isinstance(node, FunctionStatement):

            if not in_class:
                self.defined_functions.setdefault(
                    node.name, (node.line, node.column)
                )

        elif isinstance(node, ClassStatement):
            self.defined_classes.add(node.name)

        elif isinstance(node, DecoratorStatement):
            self.defined_decorators.add(node.name)

        for child in self._children(node):
            self._collect_node(child, in_class or isinstance(node, ClassStatement))

    # ------------------------------------------------------------------
    # Scope management
    # ------------------------------------------------------------------

    def _push_scope(self):
        self.scopes.append(_Scope())

    def _pop_scope(self):

        scope = self.scopes.pop()

        for name, info in scope.variables.items():

            if (
                info["kind"] in ("let", "var")
                and info["check_unused"]
                and not info["read"]
            ):
                self._add(
                    "W004",
                    f"Variable '{name}' is declared but never used",
                    info["line"],
                    info["column"],
                    "warning"
                )

    def _declare(self, name, kind, line, column, check_unused=True):

        if kind in ("let", "var") and self.class_depth > 0:
            check_unused = False

        scope = self.scopes[-1]

        if name in scope.variables:
            self._add(
                "W002",
                f"Variable '{name}' is already declared in this scope",
                line,
                column,
                "warning"
            )
            return

        scope.variables[name] = {
            "kind": kind,
            "line": line,
            "column": column,
            "read": False,
            "check_unused": check_unused
        }

    def _find(self, name):

        for scope in reversed(self.scopes):

            if name in scope.variables:
                return scope.variables[name]

        return None

    def _mark_read(self, name):

        info = self._find(name)

        if info is not None:
            info["read"] = True

    # ------------------------------------------------------------------
    # Traversal
    # ------------------------------------------------------------------

    def _walk(self, node):

        if node is None:
            return

        handler = getattr(self, f"_node_{type(node).__name__}", None)

        if handler is not None:
            handler(node)
            return

        for child in self._children(node):
            self._walk(child)

    def _walk_statements(self, statements):

        ended = False

        for statement in statements:

            if ended:
                self._add(
                    "W010",
                    "Unreachable code after return, break or continue",
                    statement.line,
                    statement.column,
                    "warning"
                )

            self._walk(statement)

            if isinstance(
                statement,
                (ReturnStatement, BreakStatement, ContinueStatement)
            ):
                ended = True

    # ------------------------------------------------------------------
    # Nodes
    # ------------------------------------------------------------------

    def _node_Block(self, node):
        self._push_scope()
        self._walk_statements(node.statements)
        self._pop_scope()

    def _node_LetStatement(self, node):
        self._declare(node.name, "let", node.line, node.column)
        self._walk(node.value)

    def _node_VarStatement(self, node):
        self._declare(node.name, "var", node.line, node.column)
        self._walk(node.value)

    def _node_AssignmentStatement(self, node):

        info = self._find(node.name)

        if info is not None and info["kind"] == "let":
            self._add(
                "W005",
                f"Cannot assign to immutable variable '{node.name}'",
                node.line,
                node.column,
                "warning"
            )

        self._walk(node.value)

    def _node_WhenStatement(self, node):
        self._walk(node.condition)
        self._walk(node.body)

        if node.else_body is not None:
            self._walk(node.else_body)

    def _node_WhileStatement(self, node):
        self._walk(node.condition)

        self.loop_depth += 1
        self._walk(node.body)
        self.loop_depth -= 1

    def _node_ForStatement(self, node):

        self._walk(node.iterable)
        self._walk(node.start)
        self._walk(node.end)
        self._walk(node.step)

        self.loop_depth += 1
        self._push_scope()

        self._declare(
            node.variable, "var", node.line, node.column
        )

        self._walk_statements(node.body.statements)

        self._pop_scope()
        self.loop_depth -= 1

    def _node_FunctionStatement(self, node):

        scope = self.scopes[-1]

        if node.name in scope.variables:
            self._add(
                "W001",
                f"Function '{node.name}' is already defined in this scope",
                node.line,
                node.column,
                "warning"
            )

        scope.variables[node.name] = {
            "kind": "function",
            "line": node.line,
            "column": node.column,
            "read": False,
            "check_unused": False
        }

        for decorator in node.decorators:
            self._walk(decorator)

        for default in node.defaults.values():
            self._walk(default)

        self.function_depth += 1
        self._push_scope()

        for param in node.params:
            self._declare(param, "param", node.line, node.column)

        self._walk_statements(node.body.statements)

        self._pop_scope()
        self.function_depth -= 1

    def _node_ClassStatement(self, node):
        self._declare(node.name, "class", node.line, node.column, check_unused=False)

        self.class_depth += 1
        self._walk(node.body)
        self.class_depth -= 1

    def _node_DecoratorStatement(self, node):
        self._declare(node.name, "decorator", node.line, node.column, check_unused=False)

        self._push_scope()

        for param in node.params:
            self._declare(param, "param", node.line, node.column)

        for default in node.defaults.values():
            self._walk(default)

        for block in (node.define, node.before, node.after, node.error):

            if block is not None:
                self._walk(block)

        self._pop_scope()

    def _node_ImportStatement(self, node):
        self._declare(node.module, "import", node.line, node.column, check_unused=False)

    def _node_ReturnStatement(self, node):

        if self.function_depth == 0:
            self._add(
                "W009",
                "'return' used outside of a function",
                node.line,
                node.column,
                "warning"
            )

        self._walk(node.value)

    def _node_BreakStatement(self, node):

        if self.loop_depth == 0:
            self._add(
                "W008",
                "'break' used outside of a loop",
                node.line,
                node.column,
                "warning"
            )

    def _node_ContinueStatement(self, node):

        if self.loop_depth == 0:
            self._add(
                "W008",
                "'continue' used outside of a loop",
                node.line,
                node.column,
                "warning"
            )

    def _node_SwitchStatement(self, node):

        self._walk(node.expression)

        for case in node.cases:
            self._walk(case.value)
            self._walk(case.body)

        if node.default is not None:
            self._walk(node.default)

    def _node_Identifier(self, node):
        self.referenced_names.add(node.name)
        self._mark_read(node.name)

    def _node_CallExpression(self, node):

        self.referenced_names.add(node.name)

        valid = (
            BUILTIN_FUNCTIONS | set(self.defined_functions) | self.defined_classes
        )

        if node.name not in valid:
            self._add(
                "W011",
                f"Call to undefined function '{node.name}'",
                node.line,
                node.column,
                "warning"
            )

        for argument in node.arguments:
            self._walk(argument)

    def _node_Decorator(self, node):

        valid = BUILTIN_DECORATORS | self.defined_decorators

        if node.name not in valid:
            self._add(
                "W012",
                f"Decorator '#{node.name}' is not defined",
                node.line,
                node.column,
                "warning"
            )

        for argument in node.arguments:
            self._walk(argument)

    # ------------------------------------------------------------------
    # Style checks
    # ------------------------------------------------------------------

    def _style_checks(self):

        lines = self.source.splitlines()

        empty = self.source.strip() == ""

        if empty:
            return

        for index, line in enumerate(lines, start=1):

            if line != line.rstrip():
                self._add(
                    "S001",
                    "Trailing whitespace",
                    index,
                    len(line.rstrip()) + 1,
                    "style"
                )

        if not self.source.endswith("\n"):
            self._add(
                "S002",
                "Missing newline at end of file",
                len(lines),
                len(lines[-1]) + 1,
                "style"
            )

    def _report_unused_functions(self):

        for name, (line, column) in self.defined_functions.items():

            if name not in self.referenced_names:
                self._add(
                    "W003",
                    f"Function '{name}' is defined but never used",
                    line,
                    column,
                    "warning"
                )