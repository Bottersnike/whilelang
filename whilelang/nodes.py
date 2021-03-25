class ASTNode:
    def __init__(self):
        pass

    def visit(self, *args):
        pass


class SuiteNode(ASTNode):
    def __init__(self, statements):
        self.statements = statements

    def visit(self, *args):
        for i in self.statements:
            i.visit(*args)


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


class WhileNode(ASTNode):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

    def visit(self, *args):
        while self.condition.visit(*args):
            self.body.visit(*args)


class SkipNode(ASTNode):
    pass


class AssignNode(ASTNode):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def visit(self, namespace, *args):
        namespace[self.name] = self.value.visit(namespace, *args)


class ConstantNode(ASTNode):
    def __init__(self, value):
        self.value = value

    def visit(self, *args):
        return self.value


class NotNode(ASTNode):
    def __init__(self, expr):
        self.expr = expr

    def visit(self, *args):
        return not self.expr.visit(*args)


class _BinNode(ASTNode):
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs


class MulNode(_BinNode):
    def visit(self, *args):
        return self.lhs.visit(*args) * self.rhs.visit(*args)


class DivNode(_BinNode):
    def visit(self, *args):
        return self.lhs.visit(*args) / self.rhs.visit(*args)


class AddNode(_BinNode):
    def visit(self, *args):
        return self.lhs.visit(*args) + self.rhs.visit(*args)


class SubNode(_BinNode):
    def visit(self, *args):
        return self.lhs.visit(*args) - self.rhs.visit(*args)


class EqNode(_BinNode):
    def visit(self, *args):
        return self.lhs.visit(*args) == self.rhs.visit(*args)


class AndNode(_BinNode):
    def visit(self, *args):
        return self.lhs.visit(*args) and self.rhs.visit(*args)


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


class VariableNode(ASTNode):
    def __init__(self, name):
        self.name = name

    def visit(self, namespace, *args):
        return namespace.get(self.name, 0)


class TraceNode(ASTNode):
    def __init__(self, location):
        self.location = location

    def visit(self, namespace, *args):
        print(f"-=-=-=- Trace on line {self.location[0] + 1} -=-=-=-")

        for i in namespace:
            print(f"  {i} := {namespace[i]}")


class ExitNode(ASTNode):
    def visit(self, *args):
        exit()


class PrintNode(ASTNode):
    def __init__(self, name):
        self.name = name

    def visit(self, namespace, *args):
        print(f"{self.name} := {namespace.get(self.name, 0)}")
