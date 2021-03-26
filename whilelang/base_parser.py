from .const import ANY
from .errors import WhileSyntaxError


class BaseParser:
    def __init__(self, lexer):
        self._lex = lexer
        self._cur = next(lexer)
        self._next = next(lexer)

    def _error(self, message, token=None):
        if token is None:
            token = self._cur

        error = f"Syntax error at line {token.location[0] + 1}\n"
        error += "  " + message + "\n"
        error += self._lex._text.split("\n")[token.location[0]] + "\n"
        if not token.length:
            error += " " * (token.location[1] - 1) + "^"
        else:
            error += (
                " " * (token.location[1] - token.length - 1)
                + "^" + "~" * (token.length - 1)
            )
        raise WhileSyntaxError(error)

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
        self._cur = self._next
        self._next = next(self._lex)
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
            self._error(
                f"Unexpected '{self._cur.type} {self._cur.meta}' at this time."
                f"Expected one of {matcher[self._cur.type]}"
            )

        return self.eat()
