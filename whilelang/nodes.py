from .const import HELP_MESSAGE
from .errors import WhileError, WhileSystemExit
from .util import phi, beta, numeric_name
from .numeric import bool_from_num, arith_from_num, stmt_from_num


class ASTNode:
    def __init__(self):
        pass

    def visit(self, *args):
        pass

    def numeric(self):
        raise WhileError(
            f"Node {self.__class__.__name__} does not implement numeric()"
        )

    def __str__(self):
        return ""


class SuiteNode(ASTNode):
    def __init__(self, statements):
        self.statements = statements

    def __str__(self):
        return "; ".join(map(str, self.statements))

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

        val = phi(self.statements[-2].numeric(), self.statements[-1].numeric())
        val = 3 + 4 * val

        for i in self.statements[-3::-1]:
            val = 3 + 4 * phi(i.numeric(), val)
        return val


class IfNode(ASTNode):
    def __init__(self, condition, body, else_body):
        self.condition = condition
        self.body = body
        self.else_body = else_body

    def __str__(self):
        if self.else_body is None:
            return f"if ({self.condition}) then ({self.body})"
        return (
            f"if ({self.condition}) then ({self.body}) else ({self.else_body})"
        )

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

    def __str__(self):
        return f"while ({self.condition}) do ({self.body})"

    def visit(self, *args):
        while self.condition.visit(*args):
            self.body.visit(*args)

    def numeric(self):
        return 1 + 4 * phi(self.condition.numeric(), self.body.numeric())


class SkipNode(ASTNode):
    def __str__(self):
        return "skip"

    def numeric(self):
        return 0


class AssignNode(ASTNode):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __str__(self):
        return f"{self.name} := {self.value}"

    def visit(self, namespace, *args):
        namespace[self.name] = self.value.visit(namespace, *args)

    def numeric(self):
        return 2 + 4 * phi(numeric_name(self.name), self.value.numeric())


class ConstantNode(ASTNode):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value).lower()

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

    def __str__(self):
        return f"¬{self.expr}"

    def visit(self, *args):
        return not self.expr.visit(*args)

    def numeric(self):
        return 4 + 4 * self.expr.numeric()


class _BinNode(ASTNode):
    op = ""

    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs

    def __str__(self):
        lhs = (
            str(self.lhs)
            if isinstance(self.lhs, (ConstantNode, VariableNode))
            else f"({self.lhs})"
        )
        rhs = (
            str(self.rhs)
            if isinstance(self.rhs, (ConstantNode, VariableNode))
            else f"({self.rhs})"
        )
        return f"{lhs} {self.op} {rhs}"


class MulNode(_BinNode):
    op = "*"

    def visit(self, *args):
        return self.lhs.visit(*args) * self.rhs.visit(*args)

    def numeric(self):
        return 4 + 5 * phi(self.lhs.numeric(), self.rhs.numeric())


class DivNode(_BinNode):
    op = "/"

    def visit(self, *args):
        return self.lhs.visit(*args) / self.rhs.visit(*args)


class AddNode(_BinNode):
    op = "+"

    def visit(self, *args):
        return self.lhs.visit(*args) + self.rhs.visit(*args)

    def numeric(self):
        return 2 + 5 * phi(self.lhs.numeric(), self.rhs.numeric())


class SubNode(_BinNode):
    op = "-"

    def visit(self, *args):
        return self.lhs.visit(*args) - self.rhs.visit(*args)

    def numeric(self):
        return 3 + 5 * phi(self.lhs.numeric(), self.rhs.numeric())


class EqNode(_BinNode):
    op = "="

    def visit(self, *args):
        return self.lhs.visit(*args) == self.rhs.visit(*args)

    def numeric(self):
        return 2 + 4 * phi(self.lhs.numeric(), self.rhs.numeric())


class AndNode(_BinNode):
    op = "&"

    def visit(self, *args):
        return self.lhs.visit(*args) and self.rhs.visit(*args)

    def numeric(self):
        if (
            isinstance(self.lhs, VariableNode)
            or isinstance(self.rhs, VariableNode)
        ):
            raise NotImplementedError(
                "Boolean and must not operate on variables directly."
            )
        return 5 + 4 * phi(self.lhs.numeric(), self.rhs.numeric())


class OrNode(_BinNode):
    op = "|"

    def visit(self, *args):
        return self.lhs.visit(*args) or self.rhs.visit(*args)

    def numeric(self):
        # a | b === ¬(¬a & ¬b)
        return NotNode(
            OrNode(
                NotNode(self.lhs),
                NotNode(self.rhs)
            )
        ).numeric()


class CmpNode(_BinNode):
    def __init__(self, lhs, mode, rhs):
        self.lhs = lhs
        self.mode = mode
        self.rhs = rhs

    def __str__(self):
        return f"({self.lhs}) {self.mode} ({self.rhs})"

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
        if self.mode == "<=":
            return 3 + 4 * phi(self.lhs.numeric(), self.rhs.numeric())
        elif self.mode == ">=":
            # a >= b === b <= a
            return 3 + 4 * phi(self.rhs.numeric(), self.lhs.numeric())
        elif self.mode == ">":
            # a > b === ¬(a <= b)
            return NotNode(CmpNode(self.lhs, "<=", self.rhs)).numeric()
        elif self.mode == "<":
            # b > a === ¬(b <= a)
            return NotNode(CmpNode(self.rhs, "<=", self.lhs)).numeric()


class VariableNode(ASTNode):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def visit(self, namespace, *args):
        return namespace.get(self.name, 0)

    def numeric(self):
        return 1 + 5 * numeric_name(self.name)


class TraceNode(ASTNode):
    def __init__(self, location):
        self.location = location

    def __str__(self):
        return "@trace"

    def visit(self, namespace, *args):
        print(f"-=-=-=- Trace on line {self.location[0] + 1} -=-=-=-")

        for i in namespace:
            print(f"  {i} := {namespace[i]}")

    def numeric(self):
        return SkipNode().numeric()


class ExitNode(ASTNode):
    def __str__(self):
        return "@exit"

    def visit(self, *args):
        raise WhileSystemExit


class PrintNode(ASTNode):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return f"@print {self.name}"

    def visit(self, namespace, *args):
        print(f"{self.name} := {namespace.get(self.name, 0)}")

    def numeric(self):
        return SkipNode().numeric()


class ResetNode(ASTNode):
    def __str__(self):
        return "@reset"

    def visit(self, namespace, *args):
        namespace.clear()


class HelpNode(ASTNode):
    def __str__(self):
        return "@help"

    def visit(self, *args):
        print(HELP_MESSAGE)

    def numeric(self):
        return SkipNode().numeric()


class NumericNode(ASTNode):
    def __init__(self, suite):
        self.suite = suite

    def __str__(self):
        return f"@numeric {self.suite}"

    def visit(self, *args):
        return self.suite.numeric()


class FromNumericNode(ASTNode):
    def __init__(self, mode, num):
        self.mode = mode
        self.num = num

    def __str__(self):
        return f"@from_numeric {self.mode} {self.num}"

    def visit(self, *args):
        num = self.num.visit(*args)
        if self.mode == "a":
            return arith_from_num(num)
        elif self.mode == "b":
            return bool_from_num(num)
        elif self.mode == "stmt":
            return stmt_from_num(num)
        return SkipNode()


class RunNumericNode(FromNumericNode):
    def __init__(self, mode, num):
        self.mode = mode
        self.num = num

    def __str__(self):
        return f"@run_numeric {self.mode} {self.num}"

    def visit(self, *args):
        return super().visit(*args).visit(*args)


class EvalNode(ASTNode):
    def __init__(self, var):
        self.var = var

    def __str__(self):
        return f"@eval {self.var}"

    def visit(self, namespace, *args):
        if isinstance(namespace.get(self.var), ASTNode):
            return namespace[self.var].visit(*args)
        raise WhileError("Cannot evaluate non-code variable")
