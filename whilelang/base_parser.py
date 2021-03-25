from .const import ANY


class BaseParser:
    def __init__(self, lexer):
        self._lex = lexer
        self._cur = next(lexer)

    def _error(self, message):
        print(f"Syntax error at line {self._cur.location[0] + 1}")
        print("  " + message)
        print(self._lex._text.split("\n")[self._cur.location[0]])
        if self._cur.length:
            print(" " * (self._cur.location[1] - 1) + "^")
        else:
            print(" " * (self._cur.location[1] - self._cur.length)
                  + "^" + "~" * (self._cur.length - 1))
        quit()

    def eat(self, token=None, meta=None):
        if token is not None and self._cur.type != token:
            self._error(
                f"Unexpected '{self._cur.type}' at this time. "
                f"Expected '{token}'."
            )
        if meta is not None and self._cur.meta != meta:
            self._error(
                f"Unexpected '{self._cur.type} {self._cur.meta}' "
                f"at this time. Expected '{token} {meta}'."
            )
        last = self._cur
        self._cur = next(self._lex)
        return last

    def try_eat(self, token, meta=None):
        if self._cur.type != token:
            return False
        if meta is not None and self._cur.meta != meta:
            return False
        self.eat(token, meta)
        return True

    def eat_list(self, matcher):
        if self._cur.type not in matcher:
            self._error(
                f"Unexpected '{self._cur.type}' at this time. "
                f"Expected '{matcher}'."
            )

        if matcher[self._cur.type] is ANY:
            return self.eat()
        if self._cur.meta not in matcher[self._cur.type]:
            self._error()

        return self.eat()
