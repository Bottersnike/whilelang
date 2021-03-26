from .const import HELP_MESSAGE
from .errors import WhileError, WhileSystemExit


def phi(n, m):
    return (2 ** n) * (2 * m + 1) - 1


def beta(x):
    return x
    # return (2 * x) if x >= 0 else (-2 * x - 1)


def numeric_name(name):
    return "xyz".index(name)
    val = 0
    for i in name:
        val = (val << 8) | ord(i)
    return val


class ASTNode:
    def __init__(self):
        pass

    def visit(self, *args):
        pass

    def numeric(self):
        raise WhileError(
            f"Node {self.__class__.__name__} does not implement numeric()"
        )


class SuiteNode(ASTNode):
    def __init__(self, statements):
        self.statements = statements

    def visit(self, *args):
        ret = 0
        for i in self.statements:
            ret = i.visit(*args)
        return ret

    def numeric(self):
        if len(self.statements) == 0:
            return 0
        if len(self.statements) == 1:
            return self.statements[0].numeric()

        val = phi(self.statements[-1].numeric(), self.statements[-2].numeric())
        val = 3 + 4 * val

        for i in self.statements[-3::-1]:
            val = 3 + 4 * phi(i.numeric(), val)
        return val


class IfNode(ASTNode):
    def __init__(self, condition, body, else_body):
        self.condition = condition
        self.body = body
        self.else_body = else_body

    def visit(self, *args):
        if self.condition.visit(*args):
            self.body.visit(*args)
        elif self.else_body is not None:
            self.else_body.visit(*args)

    def numeric(self):
        else_body = (
            self.else_body.numeric() if self.else_body is not None else 0
        )
        return 4 + 4 * phi(
            self.condition.numeric(),
            phi(self.body.numeric(), else_body)
        )


class WhileNode(ASTNode):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

    def visit(self, *args):
        while self.condition.visit(*args):
            self.body.visit(*args)

    def numeric(self):
        return 1 + 4 * phi(self.condition.numeric(), self.body.numeric())


class SkipNode(ASTNode):
    def numeric(self):
        return 0


class AssignNode(ASTNode):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def visit(self, namespace, *args):
        namespace[self.name] = self.value.visit(namespace, *args)

    def numeric(self):
        return 2 + 4 * phi(numeric_name(self.name), self.value.numeric())


class ConstantNode(ASTNode):
    def __init__(self, value):
        self.value = value

    def visit(self, *args):
        return self.value

    def numeric(self):
        if isinstance(self.value, float):
            raise NotImplementedError("Floats disallowed in canonical while")
        if isinstance(self.value, bool):
            return 1 - self.value
        return 5 * beta(self.value)


class NotNode(ASTNode):
    def __init__(self, expr):
        self.expr = expr

    def visit(self, *args):
        return not self.expr.visit(*args)

    def numeric(self):
        return 4 + 4 * self.expr.numeric()


class _BinNode(ASTNode):
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs


class MulNode(_BinNode):
    def visit(self, *args):
        return self.lhs.visit(*args) * self.rhs.visit(*args)

    def numeric(self):
        return 4 + 5 * phi(self.lhs.numeric(), self.rhs.numeric())


class DivNode(_BinNode):
    def visit(self, *args):
        return self.lhs.visit(*args) / self.rhs.visit(*args)


class AddNode(_BinNode):
    def visit(self, *args):
        return self.lhs.visit(*args) + self.rhs.visit(*args)

    def numeric(self):
        return 2 + 5 * phi(self.lhs.numeric(), self.rhs.numeric())


class SubNode(_BinNode):
    def visit(self, *args):
        return self.lhs.visit(*args) - self.rhs.visit(*args)

    def numeric(self):
        return 3 + 5 * phi(self.lhs.numeric(), self.rhs.numeric())


class EqNode(_BinNode):
    def visit(self, *args):
        return self.lhs.visit(*args) == self.rhs.visit(*args)

    def numeric(self):
        return 2 + 4 * phi(self.lhs.numeric(), self.rhs.numeric())


class AndNode(_BinNode):
    def visit(self, *args):
        return self.lhs.visit(*args) and self.rhs.visit(*args)

    def numeric(self):
        return 5 + 4 * phi(self.lhs.numeric(), self.rhs.numeric())


class OrNode(_BinNode):
    def visit(self, *args):
        return self.lhs.visit(*args) or self.rhs.visit(*args)


class CmpNode(_BinNode):
    def __init__(self, lhs, mode, rhs):
        self.lhs = lhs
        self.mode = mode
        self.rhs = rhs

    def visit(self, *args):
        lhs = self.lhs.visit(*args)
        rhs = self.rhs.visit(*args)
        if self.mode == ">":
            return lhs > rhs
        elif self.mode == ">=":
            return lhs >= rhs
        elif self.mode == "<":
            return lhs < rhs
        elif self.mode == "<=":
            return lhs <= rhs
        return False

    def numeric(self):
        if self.mode != "<=":
            raise NotImplementedError("Canonical while only supports <=")
        return 3 + 4 * phi(self.lhs.numeric(), self.rhs.numeric())


class VariableNode(ASTNode):
    def __init__(self, name):
        self.name = name

    def visit(self, namespace, *args):
        return namespace.get(self.name, 0)

    def numeric(self):
        return 1 + 5 * numeric_name(self.name)


class TraceNode(ASTNode):
    def __init__(self, location):
        self.location = location

    def visit(self, namespace, *args):
        print(f"-=-=-=- Trace on line {self.location[0] + 1} -=-=-=-")

        for i in namespace:
            print(f"  {i} := {namespace[i]}")


class ExitNode(ASTNode):
    def visit(self, *args):
        raise WhileSystemExit


class PrintNode(ASTNode):
    def __init__(self, name):
        self.name = name

    def visit(self, namespace, *args):
        print(f"{self.name} := {namespace.get(self.name, 0)}")


class ResetNode(ASTNode):
    def visit(self, namespace, *args):
        namespace.clear()


class HelpNode(ASTNode):
    def visit(self, *args):
        print(HELP_MESSAGE)
