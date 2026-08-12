from nodes import FunctionStatement


class Module:

    def __init__(self, name, variables, functions):
        self.name = name
        self.variables = variables
        self.functions = functions


    def get(self, name):

        value = self.variables.get(name)

        if value is None:
            return None

        return value["value"]


class WizClass:

    def __init__(self, name, statement):
        self.name = name
        self.statement = statement
        self.methods = {}
        self.variables = {}

    def define(self, interpreter):

        class_scope = {}

        old_scopes = interpreter.scopes

        interpreter.scopes = old_scopes + [class_scope]

        for stmt in self.statement.body.statements:

            if isinstance(stmt, FunctionStatement):

                stmt.closure = interpreter.scopes.copy()

                self.methods[stmt.name] = stmt

            else:

                interpreter.visit(stmt)

        interpreter.scopes = old_scopes

        for name, entry in class_scope.items():
            self.variables[name] = entry["value"]

    def instantiate(self, interpreter, node):

        from interpreter import ReturnException

        instance = WizInstance(self, dict(self.variables))

        init = self.methods.get("init")

        if init is not None:

            scope = interpreter.bind_arguments(init, node)

            scope["self"] = {
                "value": instance,
                "mutable": True
            }

            old_scopes = interpreter.scopes

            interpreter.scopes = init.closure + [scope]

            try:
                interpreter.visit_Block(
                    init.body,
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