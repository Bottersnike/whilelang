from .base_parser import BaseParser
from .const import DIRECTIVE, NUMBER, SYMBOL, NAME, KEYWORD, BOOLEAN, EOF, ANY
from .nodes import (
    EvalNode, SuiteNode, SkipNode, IfNode, WhileNode, AssignNode, VariableNode, NotNode,
    ConstantNode, MulNode, SubNode, AddNode, CmpNode, EqNode, AndNode, OrNode,
    TraceNode, ExitNode, PrintNode, HelpNode, ResetNode, NumericNode,
    FromNumericNode, RunNumericNode
)


class Parser(BaseParser):
    def program(self):
        suite = self.suite()
        self.eat(EOF)
        return suite

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
            self._cur.type not in (KEYWORD, NAME)
            or (
                self._cur.type == NAME
                and not (self._next.type == SYMBOL and self._next.meta == ":=")
            )
        ):
            return self.expr_a()

        token = self.eat_list({
            KEYWORD: ("skip", "if", "while"),
            NAME: ANY,
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
            SYMBOL: ("(", ),
            DIRECTIVE: ANY,
        })
        if token.type == SYMBOL:
            token = self.expr_a()
            self.eat(SYMBOL, ")")
        elif token.type == NAME:
            token = VariableNode(token.meta)
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
            elif token.meta == "numeric":
                return NumericNode(self.suite())
            elif token.meta == "from_numeric":
                return FromNumericNode(self.eat(NAME).meta, self.statement())
            elif token.meta == "run_numeric":
                return RunNumericNode(self.eat(NAME).meta, self.statement())
            elif token.meta == "eval":
                return EvalNode(self.eat(NAME).meta)
            else:
                self._error(f"Unknown directive '{token.meta}'", token)
        else:
            token = ConstantNode(token.meta)
        if negate:
            token = NotNode(token)
        return token

    def expr_f(self):
        node = self.factor()
        while self._cur.type == SYMBOL and self._cur.meta in ("*", "/"):
            if self.try_eat(SYMBOL, "*"):
                node = MulNode(node, self.factor())
            if self.try_eat(SYMBOL, "/"):
                node = SubNode(node, self.factor())
        return node

    def expr_e(self):
        node = self.expr_f()
        while self._cur.type == SYMBOL and self._cur.meta in ("+", "-"):
            if self.try_eat(SYMBOL, "+"):
                node = AddNode(node, self.expr_f())
            if self.try_eat(SYMBOL, "-"):
                node = SubNode(node, self.expr_f())
        return node

    def expr_d(self):
        node = self.expr_e()
        while (
            self._cur.type == SYMBOL
            and self._cur.meta in ("<=", "<", ">", ">=")
        ):
            sym = self.eat(SYMBOL)
            node = CmpNode(node, sym.meta, self.expr_e())
        return node

    def expr_c(self):
        node = self.expr_d()
        while self._cur.type == SYMBOL and self._cur.meta in ("=", ):
            if self.try_eat(SYMBOL, "="):
                node = EqNode(node, self.expr_d())
        return node

    def expr_b(self):
        node = self.expr_c()
        while self._cur.type == SYMBOL and self._cur.meta in ("&", ):
            if self.try_eat(SYMBOL, "&"):
                node = AndNode(node, self.expr_c())
        return node

    def expr_a(self):
        node = self.expr_b()
        while self._cur.type == SYMBOL and self._cur.meta in ("|", ):
            if self.try_eat(SYMBOL, "|"):
                node = OrNode(node, self.expr_b())
        return node
