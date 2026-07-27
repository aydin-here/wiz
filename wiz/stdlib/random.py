import random


class RandomModule:

    def __init__(self):
        self.functions = {
            "randint": self.randint,
            "choice": self.choice
        }

    def randint(self, a, b):

        return random.randint(a, b)


    def choice(self, values):

        return random.choice(values)