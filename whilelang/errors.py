class WhileError(BaseException):
    pass


class WhileSyntaxError(WhileError):
    pass


class WhileSystemExit(WhileError):
    pass
