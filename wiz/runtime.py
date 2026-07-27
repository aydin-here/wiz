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