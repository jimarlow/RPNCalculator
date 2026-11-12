from RegexDispatcher import *
import math

class RPNCalculator(RegexDispatcher):
    def __init__(self):
        RegexDispatcher.__init__(self)
        self.stack = []
        self.variables = {}

    def __str__(self):
        """Returns the whole stack as a string."""
        return str(self.stack)

    def __call__(self, expression):
        """On call, process the stack and return the top of the stack."""
        stack = self.stack.copy()
        variables = self.variables.copy()
        succeeded = False
        try:
            tokens = expression.split()
            for index, t in enumerate(tokens):
                is_assignment_target = (
                    index + 1 < len(tokens) and tokens[index + 1] == "="
                )
                if t in self.variables and not is_assignment_target:
                    t = str(self.variables[t])
                self.dispatch(t, token=t)
            result = self.top()
            succeeded = True
            return result
        finally:
            if not succeeded:
                self.stack = stack
                self.variables = variables

    def noMatch(self, s=None, **kwargs):
        raise ValueError(f"Unknown token: {s!r}")

    # Stack management
    def top(self):
        """Return the top of the stack."""
        return self.stack[-1] if len(self.stack) > 0 else []

    def push(self, x):
        """Push an item on to the top of the stack."""
        return self.stack.append(x)

    def pop(self, n=1):
        """Pop 1 or more items off the top of the stack."""
        return self.stack.pop() if n == 1 else [self.stack.pop() for n in range(n)]

    def peek(self, n=1):
        """Returns a list of the top n items on the stack."""
        return self.stack[-1] if n == 1 else self.stack[-n:]

    def swap(self, regex: r"swap", **kwargs):
        """Swap the top two items on the stack."""
        a, b = self.pop(2)
        self.push(a)
        self.push(b)

    def cls(self, regex: r"cls", **kwargs):
        """Clear the stack."""
        self.stack=[]
        self.variables = {}

    # Handle numbers
    def number(self, regex: r"[-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?", **kwargs):
        """Push an item on to the top of the stack."""
        self.push(float(kwargs['token']))

    # Binary operators
    def pow(self, regex: r"\*\*", **kwargs):
        """Pop a and b off the stack and push b ** a on to the top of the stack."""
        a, b = self.pop(2)
        self.push(b ** a)

    def plus(self, regex: r"\+", **kwargs):
        """Pop a and b off the stack and push b + a on to the top of the stack."""
        a, b = self.pop(2)
        self.push(b + a)

    def minus(self, regex: r"\-", **kwargs):
        """Pop a and b off the stack and push b - a on to the top of the stack."""
        a, b = self.pop(2)
        self.push(b - a)

    def multiply(self, regex: r"\*", **kwargs):
        """Pop a and b off the stack and push b * a on to the top of the stack."""
        a, b = self.pop(2)
        self.push(b * a)

    def divide(self, regex: r"\/", **kwargs):
        """Pop a and b off the stack and push b / a on to the top of the stack."""
        a, b = self.pop(2)
        self.push(b / a)

    def mod(self, regex: r"%", **kwargs):
        """Pop a and b off the stack and push b / a on to the top of the stack."""
        a, b = self.pop(2)
        self.push(b % a)

    def logN(self, regex: r"logN", **kwargs):
        """Pop a and b off the stack and push log base a of b on to the top of the stack."""
        a, b = self.pop(2)
        self.push(math.log(b,a))

    def percent(self, regex: r"percent", **kwargs):
        """Pop a and b off the stack and push b * a / 100 on to the top of the stack."""
        a, b = self.pop(2)
        self.push(b * a / 100)

    def roundN(self, regex: r"roundN", **kwargs):
        """Pop a and b off the stack and push round(b, a) on to the top of the stack."""
        a, b = self.pop(2)
        self.push(round(b, int(a)))

    def hypot(self, regex: r"hypot", **kwargs):
        """Pop a and b off the stack and push hypot(b, a) on to the top of the stack."""
        a, b = self.pop(2)
        self.push(math.hypot(b, a))


    # Unary operators
    def neg(self, regex: r"neg", **kwargs):
        """Negate the top of the stack."""
        self.push(-self.pop())

    def int(self, regex: r"int", **kwargs):
        """Negate the top of the stack."""
        self.push(int(self.pop()))

    def ceil(self, regex: r"ceil", **kwargs):
        """Replace the top of the stack with the smallest integer greater than or equal to it."""
        self.push(math.ceil(self.pop()))

    def floor(self, regex: r"floor", **kwargs):
        """Replace the top of the stack with the largest integer less than or equal to it."""
        self.push(math.floor(self.pop()))

    def round(self, regex: r"round", **kwargs):
        """Replace the top of the stack with the its rounded value."""
        self.push(round(self.pop()))

    def fabs(self, regex: r"fabs", **kwargs):
        """The absolute value of the top of the stack."""
        self.push(math.fabs(self.pop()))

    def factorial(self, regex: r"factorial", **kwargs):
        """Replace the top value with its factorial if it is a non-negative integer."""
        value = self.pop()
        if (
            not isinstance(value, (int, float))
            or not math.isfinite(value)
            or not float(value).is_integer()
            or value < 0
        ):
            raise ValueError("factorial requires a non-negative integer")
        self.push(math.factorial(int(value)))

    def sqrt(self, regex: r"sqrt", **kwargs):
        """Take the square root of the top of the stack."""
        self.push(math.sqrt(self.pop()))

    def log2(self, regex: r"log2", **kwargs):
        """Take the log base 2 of the top of the stack."""
        self.push(math.log2(self.pop()))

    def log10(self, regex: r"log10", **kwargs):
        """Take the log base 10 of the top of the stack."""
        self.push(math.log10(self.pop()))

    # Constants
    def pi(self, regex: r"pi", **kwargs):
        """Push Pi on to the top of the stack."""
        self.push(math.pi)

    def e(self, regex: r"e", **kwargs):
        """Push e on to the top of the stack."""
        self.push(math.e)

    # Trig functions
    def deg(self, regex: r"deg", **kwargs):
        """Convert the top of the stack to degrees."""
        self.push(math.degrees(self.pop()))

    def rad(self, regex: r"rad", **kwargs):
        """Convert the top of the stack to radians."""
        self.push(math.radians(self.pop()))

    def sin(self, regex: r"sin", **kwargs):
        """Convert the top of the stack to sin."""
        self.push(math.sin(self.pop()))

    def cos(self, regex: r"cos", **kwargs):
        """Convert the top of the stack to cos."""
        self.push(math.cos(self.pop()))

    def tan(self, regex: r"tan", **kwargs):
        """Convert the top of the stack to tan."""
        self.push(math.tan(self.pop()))

    def asin(self, regex: r"asin", **kwargs):
        """Convert the top of the stack to asin."""
        self.push(math.asin(self.pop()))

    def acos(self, regex: r"acos", **kwargs):
        """Convert the top of the stack to cos."""
        self.push(math.acos(self.pop()))

    def atan(self, regex: r"atan", **kwargs):
        """Convert the top of the stack to tan."""
        self.push(math.atan(self.pop()))

    def atan2(self, regex: r"atan2", **kwargs):
        """Push atan2(y, x), where x is topmost and y is next on the stack."""
        x, y = self.pop(2)
        self.push(math.atan2(y, x))

    # Whole stack operators
    def sum(self, regex: r"sum", **kwargs):
        """Sum the whole stack."""
        self.stack=[math.fsum(self.stack)]

    # Variables
    def assign(self, regex:r"=", **kwargs):
        """Store the value below the variable name and leave the value on the stack."""
        name, val = self.pop(2)
        self.push(val)
        self.variables[name] = val

    def variable(self, regex:r"[a-z]+", **kwargs):
        """Push a variable name on to the top of the stack."""
        self.push(kwargs["token"])


if __name__ == '__main__':
    calc = RPNCalculator()

    print(calc('2 2 exp 3 + neg'))

    print(calc('cls 1 2 3 4 sum'))

    print(calc('cls 1 2 3 4 5 sum 2 * 2 / pi'))

    print(calc('cls pi 2 * deg'))

    print(calc('cls 2 2 logN'))


