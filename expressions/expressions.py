"""implement classes."""
from numbers import Number as num
from functools import singledispatch


class Expression:
    """implement expression class."""

    def __init__(self, *operands):
        self.operands = operands

    def __add__(self, other):
        if isinstance(other, num):
            return Add(self, Number(other))
        elif isinstance(other, Expression):
            return Add(self, other)
        else:
            return NotImplemented

    def __radd__(self, other):
        if isinstance(other, num):
            return Add(Number(other), self)
        else:
            return NotImplemented

    def __sub__(self, other):
        if isinstance(other, num):
            return Sub(self, Number(other))
        elif isinstance(other, Expression):
            return Sub(self, other)
        else:
            return NotImplemented
    
    def __rsub__(self, other):
        if isinstance(other, num):
            return Sub(Number(other), self)
        else:
            return NotImplemented

    def __mul__(self, other):
        if isinstance(other, num):
            return Mul(self, Number(other))
        elif isinstance(other, Expression):
            return Mul(self, other)
        else:
            return NotImplemented
        
    def __rmul__(self, other):
        if isinstance(other, num):
            return Mul(Number(other), self)
        else:
            return NotImplemented

    def __truediv__(self, other):
        if isinstance(other, num):
            return Div(self, Number(other))
        elif isinstance(other, Expression):
            return Div(self, other)
        else:
            return NotImplemented
        
    def __rtruediv__(self, other):
        if isinstance(other, num):
            return Div(Number(other), self)
        else:
            return NotImplemented

    def __pow__(self, other):
        if isinstance(other, num):
            return Pow(self, Number(other))
        elif isinstance(other, Expression):
            return Pow(self, other)
        else:
            return NotImplemented

    def __rpow__(self, other):
        if isinstance(other, num):
            return Pow(Number(other), self)
        else:
            return NotImplemented


class Operator(Expression):
    """implement operator class."""

    def __repr__(self):
        return type(self).__name__ + repr(self.operands)

    def __str__(self):
        if self.precedence > self.operands[0].precedence:
            lhs = f"({self.operands[0]})"
        else:
            lhs = f"{self.operands[0]}"
        if self.precedence > self.operands[1].precedence:
            rhs = f"({self.operands[1]})"
        else:
            rhs = f"{self.operands[1]}"
        return f"{lhs} {self.symbol} {rhs}"


class Terminal(Expression):
    """implement terminal class."""

    precedence = 4

    def __init__(self, value):
        self.value = value
        super().__init__()

    def __repr__(self):
        return repr(self.value)

    def __str__(self):
        return str(self.value)


class Symbol(Terminal):

    def __init__(self, value):
        if not isinstance(value, str):
            return ValueError("value should be a string")
        super().__init__(value)

class Number(Terminal):

    def __init__(self, value):
        if not isinstance(value, num):
            return ValueError("value should be a number")
        super().__init__(value)


class Add(Operator):
    symbol = '+'
    precedence = 1
class Sub(Operator):
    symbol = '-'
    precedence = 1
class Mul(Operator):
    symbol = '*'
    precedence = 2
class Div(Operator):
    symbol = '/'
    precedence = 2
class Pow(Operator):
    symbol = '^'
    precedence = 3


def postvisitor(expr, fn, **kwargs):
    stack = []
    visited = {}
    stack.append(expr)
    while stack:
        e = stack.pop()
        unvisited_children = []
        for o in e.operands:
            if o not in visited:
                unvisited_children.append(o)

        if unvisited_children:
            stack.append(e)  # Not ready to visit this node yet.
            # Need to visit children before e.
            stack += unvisited_children
        else:
            # Any children of e have been visited, so we can visit it.
            visited[e] = fn(e, *(visited[o] for o in e.operands), **kwargs)

    # When the stack is empty, we have visited every subexpression,
    # including expr itself.
    return visited[expr]


@singledispatch
def differentiate(expr, *o, var=''):
    raise NotImplementedError(
        f"Cannot differentiate a  {type(expr)}")

@differentiate.register(Number)
def _(expr, *o, var=''):
    return Number(0)

@differentiate.register(Symbol)
def _(expr, *o, var=''):
    if expr.value == var:
        return Number(1)
    else:
        return Number(0)

@differentiate.register(Add)
def _(expr, *o, var=''):
    return o[0] + o[1]

@differentiate.register(Sub)
def _(expr, *o, var=''):
    return o[0]-o[1]

@differentiate.register(Mul)
def _(expr, *o, var=''):
    return o[0]*expr.operands[1]+expr.operands[0]*o[1]

@differentiate.register(Div)
def _(expr, *o, var=''):
    return (o[0]*expr.operands[1]-expr.operands[0]*o[1])/(expr.operands[1]**2)

@differentiate.register(Pow)
def _(expr, *o, var=''):
    return expr.operands[1]*expr.operands[0]**(expr.operands[1]-1)*o[0]
