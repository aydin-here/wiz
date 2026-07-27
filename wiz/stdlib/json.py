import json


class JsonModule:

    def __init__(self):
        self.functions = {
            "parse": self.parse,
            "dump": self.stringify
        }

    def parse(self, text):

        return json.loads(text)


    def stringify(self, obj):

        return json.dumps(obj)