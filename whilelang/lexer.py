import string

from .token import Token
from .const import DIRECTIVE, NUMBER, SYMBOL, NAME, KEYWORD, BOOLEAN, EOF
from .errors import WhileSyntaxError


class Lexer:
    WHITESPACE = " \n\r\t"
    LOWERCASE = string.ascii_lowercase
    UPPERCASE = string.ascii_uppercase
    DIGITS = string.digits

    NAME_START = LOWERCASE + UPPERCASE + "_"
    NAME_BODY = NAME_START + DIGITS

    KEYWORDS = ("skip", "if", "then", "else", "while", "do")
    DIRECTIVE_START = "@"
    BOOLEANS = ("true", "false")
    DOUBLE_SYMBOLS = ("<=", ">=", ":=")
    SYMBOLS = (">", "<", "=", "+", "-", "*", "|", "&", "¬", "!", "(", ")", ";")

    def __init__(self, text: str):
        self._text = text
        self._cursor = 0
        self._position = (0, 0)
        self._cur_char = None

        self._advance()

    def _error(self, message):
        error = f"FATAL: Syntax error on line {self._position[0] + 1}\n"
        error += "  " + message + "\n"
        error += self._text.split("\n")[self._position[0]] + "\n"
        error += " " * self._position[1] + "^"
        raise WhileSyntaxError(error)

    def _advance(self):
        y, x = self._position
        if self._cur_char == "\n":
            self._position = (y + 1, 0)
        else:
            self._position = (y, x + 1)

        if self._cursor >= len(self._text):
            self._cur_char = None
        else:
            self._cur_char = self._text[self._cursor]
        self._cursor += 1

    def _peek(self):
        if self._cursor > len(self._text) - 1:
            return None
        return self._text[self._cursor]

    def _consume_name(self):
        word = ""

        while self._cur_char is not None and self._cur_char in self.NAME_BODY:
            word += self._cur_char
            self._advance()

        if word in self.BOOLEANS:
            return Token(
                BOOLEAN, True if word == "true" else False,
                self._position, len(word)
            )
        if word in self.KEYWORDS:
            return Token(KEYWORD, word, self._position, len(word))
        return Token(NAME, word, self._position, len(word))

    def _consume_number(self):
        num = ""

        while self._cur_char is not None and self._cur_char in self.DIGITS:
            num += self._cur_char
            self._advance()

        return Token(NUMBER, int(num), self._position, len(num))

    def _consume_directive(self):
        name = ""
        while self._cur_char is not None and self._cur_char in self.NAME_BODY:
            name += self._cur_char
            self._advance()
        return Token(DIRECTIVE, name, self._position, len(name) + 1)

    def _skip_line(self):
        while self._cur_char and self._cur_char != "\n":
            self._advance()
        self._advance()

    def __next__(self):
        while self._cur_char is not None:
            if self._cur_char in self.WHITESPACE:
                self._advance()
                continue
            if self._cur_char == "/" and self._peek() == "/":
                self._skip_line()
                continue

            if self._cur_char == self.DIRECTIVE_START:
                self._advance()
                return self._consume_directive()

            if self._cur_char in self.NAME_START:
                return self._consume_name()

            for i in self.DOUBLE_SYMBOLS:
                if self._cur_char == i[0] and self._peek() == i[1]:
                    self._advance()
                    self._advance()
                    return Token(SYMBOL, i, self._position, 2)

            if self._cur_char in self.SYMBOLS:
                sym = self._cur_char
                self._advance()
                return Token(SYMBOL, sym, self._position, 1)

            if self._cur_char in self.DIGITS:
                return self._consume_number()

            self._error(f"Unexpected character '{self._cur_char}'")
        return Token(EOF, None, self._position, 0)

    def __iter__(self):
        token: Token
        while (token := next(self)).type != EOF:
            yield token
        yield token
