import inspect
import re


class RegexMethod:
    def __init__(self, method, annotation):
        self.method = method
        self.name = self.method.__name__
        self.order = inspect.getsourcelines(self.method)[1] # The line in the source file
        self.regex = self.method.__annotations__[annotation]

    def match(self, s):
        return re.fullmatch(self.regex, s)

    # Make it callable
    def __call__(self, *args, **kwargs):
        return self.method(*args, **kwargs)

    def __str__(self):
        return str.format("Line: %s, method name: %s, regex: %s" % (self.order, self.name, self.regex))


class RegexDispatcher:
    def __init__(self, annotation="regex"):
        """Initialize the list of RegexMethods by adding all methods with the given annotation. Preserve order of methods in class."""
        self.annotation = annotation
        # Collect all the methods that have an annotation that matches self.annotation
        # For example, methods that have the annotation "regex", which is the default
        self.dispatchMethods = [RegexMethod(m[1], self.annotation) for m in
                                inspect.getmembers(self, predicate=inspect.ismethod) if
                                (self.annotation in m[1].__annotations__)]
        # Be sure to process the dispatch methods in the order they appear in the class!
        # This is because the order in which you test regexes is important.
        # The most specific patterns must always be tested BEFORE more general ones
        # otherwise they will never match.
        self.dispatchMethods.sort(key=lambda m: m.order)

    def noMatch(self, s=None, **kwargs):
        """Override this to perform suitable action when no matching method is found."""
        return None

    def dispatch(self, s, **kwargs):
        """Finds the FIRST match of string s against a RegexMethod in self.dispatchMethods, calls the RegexMethod and returns."""
        for m in self.dispatchMethods:
            if m.match(s):
                return m(self.annotation, **kwargs)
        return self.noMatch(s, **kwargs)


if __name__ == '__main__':

    # Simple example of the RegexDispatcher in use
    class RPNCalculator(RegexDispatcher):
        def __init__(self):
            RegexDispatcher.__init__(self)
            self.stack = []

        def push(self, x):
            return self.stack.append(x)

        def pop(self,n=1):
            if n==1:
                return self.stack.pop()
            else:
                return [self.stack.pop() for n in range(n)]

        def number(self, regex:r"[-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?", token=''):
            self.stack.append(float(token))

        # Binary operators
        def plus(self, regex:r"\+", token=''):
            a, b = self.pop(2)
            self.push(b+a)

        def minus(self, regex:r"\-", token=''):
            a, b = self.pop(2)
            self.push(b-a)

        def multiply(self, regex:r"\*", token=''):
            a, b = self.pop(2)
            self.push(b*a)

        def divide(self, regex: r"\/", token=''):
            a, b = self.pop(2)
            self.push(b / a)

        def __call__(self, expression):
            for t in expression.split():
                self.dispatch(t, token=t)
            return self.stack[-1] # return the top of the stack

    calc = RPNCalculator()
    calc('1.0 2 + 2 * 3 /')
    print(calc.stack)

    calc('1 2 3 4 5 6')
    print(calc.stack)

