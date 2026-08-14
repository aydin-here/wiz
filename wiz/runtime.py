from nodes import FunctionStatement


class Module:

    def __init__(self, name, variables, functions):
        self.name = name
        self.variables = variables
        self.functions = functions


    def get(self, name):

        variable = self.variables.get(name)

        if variable is not None:
            return variable["value"]

        return self.functions.get(name)


class WizClass:

    def __init__(self, name, statement, parent=None):
        self.name = name
        self.statement = statement
        self.parent = parent
        self.methods = {}
        self.variables = {}

    def define(self, interpreter):

        class_scope = {}

        old_scopes = interpreter.scopes

        interpreter.scopes = old_scopes + [class_scope]

        for stmt in self.statement.body.statements:

            if isinstance(stmt, FunctionStatement):

                stmt.closure = interpreter.scopes.copy()

                self.methods[stmt.name] = (stmt, self)

            else:

                interpreter.visit(stmt)

        interpreter.scopes = old_scopes

        for name, entry in class_scope.items():
            self.variables[name] = entry["value"]

    def find_method(self, name):

        klass = self

        while klass is not None:

            method = klass.methods.get(name)

            if method is not None:
                return method

            klass = klass.parent

        return None

    def find_variable(self, name):

        klass = self

        while klass is not None:

            if name in klass.variables:
                return klass.variables[name]

            klass = klass.parent

        return None

    def all_variables(self):

        chain = []

        klass = self

        while klass is not None:

            chain.append(klass)

            klass = klass.parent

        variables = {}

        for klass in reversed(chain):
            variables.update(klass.variables)

        return variables

    def instantiate(self, interpreter, node):

        from interpreter import ReturnException

        instance = WizInstance(self, self.all_variables())

        init = self.find_method("init")

        if init is not None:

            method, owner = init

            scope = interpreter.bind_arguments(method, node)

            scope["self"] = {
                "value": instance,
                "mutable": True
            }

            if self.parent is not None:
                scope["super"] = {
                    "value": Super(owner, instance),
                    "mutable": True
                }

            old_scopes = interpreter.scopes

            interpreter.scopes = method.closure + [scope]

            try:
                interpreter.visit_Block(
                    method.body,
                    scope
                )
            except ReturnException:
                pass
            finally:
                interpreter.scopes = old_scopes

        return instance


class WizInstance:

    def __init__(self, klass, attributes):
        self.klass = klass
        self.attributes = attributes

    def __repr__(self):
        return f"[{self.klass.name} instance]"

    def __str__(self):
        return self.__repr__()


class Super:

    def __init__(self, klass, instance):
        self.klass = klass
        self.instance = instance

    def __repr__(self):
        return f"[super of {self.klass.name}]"

    def __str__(self):
        return self.__repr__()


class NativeModule:

    """Runtime wrapper for a Python-backed external package.

    The underlying Python package object follows the stdlib module
    convention and exposes at least a ``functions`` dict. Optional
    ``values`` and ``classes`` dicts are also supported so new package
    features can be added without changing the package manager.
    """

    def __init__(self, name, module):
        self.name = name
        self.module = module
        self.functions = getattr(module, "functions", None) or {}
        self.values = getattr(module, "values", None) or {}
        self.classes = getattr(module, "classes", None) or {}

    def get(self, name):

        if name in self.functions:
            return self.functions[name]

        if name in self.values:
            return self.values[name]

        if name in self.classes:
            return self.classes[name]

        return None

    @property
    def interpreter(self):
        return getattr(self.module, "interpreter", None)

    @interpreter.setter
    def interpreter(self, value):
        self.module.interpreter = value

    def __repr__(self):
        return f"[native module {self.name}]"

    def __str__(self):
        return self.__repr__()
