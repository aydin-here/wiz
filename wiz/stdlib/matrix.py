try:
    import numpy as np

    NUMPY_AVAILABLE = True
except Exception:
    np = None
    NUMPY_AVAILABLE = False

from errors import WizError


class MatrixModule:

    def __init__(self):

        if not NUMPY_AVAILABLE:
            return

        self.functions = {
            "create": self.create,
            "zeros": self.zeros,
            "ones": self.ones,
            "eye": self.eye,
            "identity": self.eye,
            "diag": self.diag,
            "random": self.random,
            "arange": self.arange,
            "linspace": self.linspace,
            "shape": self.shape,
            "dim": self.dim,
            "size": self.size,
            "transpose": self.transpose,
            "add": self.add,
            "subtract": self.subtract,
            "multiply": self.multiply,
            "multiply_wise": self.multiply_wise,
            "divide": self.divide,
            "dot": self.dot,
            "determinant": self.determinant,
            "inverse": self.inverse,
            "trace": self.trace,
            "min": self.min,
            "max": self.max,
            "mean": self.mean,
            "sum": self.sum,
            "reshape": self.reshape,
            "flatten": self.flatten,
            "to_list": self.to_list,
            "row": self.row,
            "column": self.column,
        }

    def _check(self):
        if not NUMPY_AVAILABLE or np is None:
            raise WizError("The 'matrix' module requires numpy.")

    def create(self, rows):
        self._check()
        return np.array(rows)

    def zeros(self, shape, value=0.0):
        self._check()
        return np.full(shape, float(value))

    def ones(self, shape, value=1.0):
        self._check()
        return np.full(shape, float(value))

    def eye(self, size, value=1.0):
        self._check()
        return np.eye(int(size)) * float(value)

    def diag(self, values):
        self._check()
        return np.diag(values)

    def random(self, rows, columns=None, minimum=0.0, maximum=1.0):
        self._check()
        size = (int(rows), int(columns)) if columns else int(rows)
        return np.random.uniform(float(minimum), float(maximum), size)

    def arange(self, start, stop=None, step=1):
        self._check()
        if stop is None:
            return np.arange(int(start), step=float(step))
        return np.arange(int(start), int(stop), float(step))

    def linspace(self, start, stop, count=50):
        self._check()
        return np.linspace(start, stop, int(count))

    def shape(self, matrix):
        return list(matrix.shape)

    def dim(self, matrix):
        return matrix.ndim

    def size(self, matrix):
        return int(matrix.size)

    def transpose(self, matrix):
        return matrix.T

    def add(self, a, b):
        return np.add(a, b)

    def subtract(self, a, b):
        return np.subtract(a, b)

    def multiply(self, a, b):
        return np.multiply(a, b)

    def multiply_wise(self, a, b):
        return np.multiply(a, b)

    def divide(self, a, b):
        return np.divide(a, b)

    def dot(self, a, b):
        return np.dot(a, b)

    def determinant(self, matrix):
        return float(np.linalg.det(matrix))

    def inverse(self, matrix):
        return np.linalg.inv(matrix)

    def trace(self, matrix):
        return float(np.trace(matrix))

    def min(self, matrix):
        return float(np.min(matrix))

    def max(self, matrix):
        return float(np.max(matrix))

    def mean(self, matrix):
        return float(np.mean(matrix))

    def sum(self, matrix):
        return float(np.sum(matrix))

    def reshape(self, matrix, rows, columns):
        return matrix.reshape(int(rows), int(columns))

    def flatten(self, matrix):
        return matrix.flatten().tolist()

    def to_list(self, matrix):
        return matrix.tolist()

    def row(self, matrix, index):
        return matrix[int(index)].tolist()

    def column(self, matrix, index):
        return matrix[:, int(index)].tolist()