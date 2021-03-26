from .base_parser import BaseParser
from .const import DIRECTIVE, NUMBER, SYMBOL, NAME, KEYWORD, BOOLEAN, EOF, ANY
from .nodes import (
    SuiteNode, SkipNode, IfNode, WhileNode, AssignNode, VariableNode, NotNode,
    ConstantNode, MulNode, SubNode, AddNode, CmpNode, EqNode, AndNode, OrNode,
    TraceNode, ExitNode, PrintNode, HelpNode, ResetNode
)


class Parser(BaseParser):
    def suite(self):
        statements = []
        while self._cur.type != EOF:
            if self.try_eat(SYMBOL, "("):
                statements.append(self.suite())
                self.eat(SYMBOL, ")")
            else:
                statements.append(self.statement())

            if self._cur.type == EOF:
                break
            if not self.try_eat(SYMBOL, ";"):
                break
        return SuiteNode(statements)

    def statement(self):
        if (
            self._cur.type not in (KEYWORD, NAME, DIRECTIVE)
            or (
                self._cur.type == NAME
                and not (self._next.type == SYMBOL and self._next.meta == ":=")
            )
        ):
            return self.expr_a()

        token = self.eat_list({
            KEYWORD: ("skip", "if", "while", "trace"),
            NAME: ANY,
            DIRECTIVE: ANY,
        })

        if token.type == KEYWORD:
            if token.meta == "skip":
                return SkipNode()
            elif token.meta == "if":
                if_condition = self.expr_a()
                self.eat(KEYWORD, "then")
                if_body = self.suite()
                if self.try_eat(KEYWORD, "else"):
                    if_else = self.suite()
                else:
                    if_else = None
                return IfNode(if_condition, if_body, if_else)
            elif token.meta == "while":
                while_condition = self.expr_a()
                self.eat(KEYWORD, "do")
                while_body = self.suite()
                return WhileNode(while_condition, while_body)
        elif token.type == DIRECTIVE:
            if token.meta == "trace":
                return TraceNode(token.location)
            elif token.meta == "exit":
                return ExitNode()
            elif token.meta == "help":
                return HelpNode()
            elif token.meta == "reset":
                return ResetNode()
            elif token.meta == "print":
                return PrintNode(self.eat(NAME).meta)
            else:
                self._error(f"Unknown directive '{token.meta}'", token)
        elif token.type == NAME:
            name = token.meta
            self.eat(SYMBOL, ":=")
            value = self.expr_a()
            return AssignNode(name, value)

    def factor(self):
        negate = False
        if self.try_eat(SYMBOL, "!"):
            negate = True
        elif self.try_eat(SYMBOL, "¬"):
            negate = True
        token = self.eat_list({
            NAME: ANY,
            NUMBER: ANY,
            BOOLEAN: ANY,
            SYMBOL: ("(", )
        })
        if token.type == SYMBOL:
            token = self.expr_a()
            self.eat(SYMBOL, ")")
        elif token.type == NAME:
            token = VariableNode(token.meta)
        else:
            token = ConstantNode(token.meta)
        if negate:
            token = NotNode(token)
        return token

    def expr_f(self):
        lhs = self.factor()
        if self.try_eat(SYMBOL, "*"):
            return MulNode(lhs, self.expr_a())
        if self.try_eat(SYMBOL, "/"):
            return SubNode(lhs, self.expr_a())
        return lhs

    def expr_e(self):
        lhs = self.expr_f()
        if self.try_eat(SYMBOL, "+"):
            return AddNode(lhs, self.expr_a())
        if self.try_eat(SYMBOL, "-"):
            return SubNode(lhs, self.expr_a())
        return lhs

    def expr_d(self):
        lhs = self.expr_e()
        if (
            self._cur.type == SYMBOL
            and self._cur.meta in ("<=", "<", ">", ">=")
        ):
            sym = self.eat(SYMBOL)
            return CmpNode(lhs, sym.meta, self.expr_a())
        return lhs

    def expr_c(self):
        lhs = self.expr_d()
        if self.try_eat(SYMBOL, "="):
            return EqNode(lhs, self.expr_a())
        return lhs

    def expr_b(self):
        lhs = self.expr_c()
        if self.try_eat(SYMBOL, "&"):
            return AndNode(lhs, self.expr_a())
        return lhs

    def expr_a(self):
        lhs = self.expr_b()
        if self.try_eat(SYMBOL, "|"):
            return OrNode(lhs, self.expr_a())
        return lhs
