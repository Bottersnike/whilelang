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
  @numeric [suite]: Calculate the Gödel number for a block of code
  @from_numeric [mode] [expr]: Convert a Gödel number back to code. mode should
      be one of "a" for arithmetic expressions, "b" for boolean expressions, or
      "stmt" for a statement.
  @run_numeric [mode] [expr]: As with @from_numeric, except the resulting code
      is executed immediately.
  @eval [name]: Execute the contents of a variable as code

All directives can be used both in the REPL and in scripts.
""".strip()
