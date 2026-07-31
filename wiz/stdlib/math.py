import math
import random


class MathModule:

    def __init__(self):
        self.pi = math.pi
        self.e = math.e
        self.tau = math.tau
        self.inf = math.inf
        self.nan = math.nan

        self.functions = {
            "abs": self.abs,
            "ceil": self.ceil,
            "floor": self.floor,
            "round": self.round,
            "sqrt": self.sqrt,
            "pow": self.pow,
            "exp": self.exp,
            "log": self.log,
            "log10": self.log10,
            "sin": self.sin,
            "cos": self.cos,
            "tan": self.tan,
            "asin": self.asin,
            "acos": self.acos,
            "atan": self.atan,
            "atan2": self.atan2,
            "degrees": self.degrees,
            "radians": self.radians,
            "hypot": self.hypot,
            "gcd": self.gcd,
            "lcm": self.lcm,
            "factorial": self.factorial,
            "comb": self.comb,
            "perm": self.perm,
            "sum": self.sum,
            "min": self.min,
            "max": self.max,
            "clamp": self.clamp,
            "avg": self.avg,
            "rand": self.rand,
            "randint": self.randint,
        }

    def abs(self, value):
        return abs(value)

    def ceil(self, value):
        return math.ceil(value)

    def floor(self, value):
        return math.floor(value)

    def round(self, value, digits=0):
        return round(value, digits)

    def sqrt(self, value):
        return math.sqrt(value)

    def pow(self, base, exponent):
        return math.pow(base, exponent)

    def exp(self, value):
        return math.exp(value)

    def log(self, value, base=math.e):
        return math.log(value, base)

    def log10(self, value):
        return math.log10(value)

    def sin(self, value):
        return math.sin(value)

    def cos(self, value):
        return math.cos(value)

    def tan(self, value):
        return math.tan(value)

    def asin(self, value):
        return math.asin(value)

    def acos(self, value):
        return math.acos(value)

    def atan(self, value):
        return math.atan(value)

    def atan2(self, y, x):
        return math.atan2(y, x)

    def degrees(self, value):
        return math.degrees(value)

    def radians(self, value):
        return math.radians(value)

    def hypot(self, x, y):
        return math.hypot(x, y)

    def gcd(self, a, b):
        return math.gcd(int(a), int(b))

    def lcm(self, a, b):
        return math.lcm(int(a), int(b))

    def factorial(self, value):
        return math.factorial(int(value))

    def comb(self, n, r):
        return math.comb(int(n), int(r))

    def perm(self, n, r=None):
        if r is None:
            return math.perm(int(n))
        return math.perm(int(n), int(r))

    def sum(self, values):
        return sum(values)

    def min(self, values):
        return min(values)

    def max(self, values):
        return max(values)

    def clamp(self, value, minimum, maximum):
        return max(minimum, min(value, maximum))

    def avg(self, values):
        return sum(values) / len(values)

    def rand(self):
        return random.random()

    def randint(self, minimum, maximum):
        return random.randint(int(minimum), int(maximum))