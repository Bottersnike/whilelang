NUMBER, SYMBOL, NAME, KEYWORD, BOOLEAN, EOF, DIRECTIVE = (
    "NUMBER", "SYMBOL", "NAME", "KEYWORD", "BOOLEAN", "EOF", "DIRECTIVE"
)
ANY = None

HELP_MESSAGE = """
While directives list:
  @trace: Output a list of all variables
  @exit: Kill the interpreter
  @help: This help message
  @reset: Reset the interpreter
  @print [variable]: Output a single variable

All directives can be used both in the REPL and in scripts.
""".strip()
