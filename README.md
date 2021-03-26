# Whilelang

The recommended way to install While is via pip, using `pip install whilelang`.

```
usage: while.py [-h] [-c] [-n] [source] [arguments ...]

positional arguments:
  source         Source code, or path to source file
  arguments      Arguments to pass to the program

optional arguments:
  -h, --help     show this help message and exit
  -c, --code     Interpret source as source, not a filename
  -n, --numeric  Calculate the Göbel number rather than evaluating
```

Running `while` without arguments will start a REPL for quick testing and
experimentation.

## Implemented grammar

The grammar implemented here is slightly different to the definitions of While
that can be found online, largely for ease of implementation.

```
<suite> = EOF
        | "(" <suite> ")"
        | <statement> *(";" <statement>)
<statement> = "skip"
            | "while" <expr_a> "do" <suite>
            | "if" <expr_a> "then" <suite> ["else" <suite>]
            | NAME ":=" <expr_a>
            | <expr_a>
<factor> = [("!" | "¬")] (NAME
                         | NUMBER
                         | BOOLEAN
                         | "(" <expr_a> ")"
                         | "@" <directive>)
<directive> = "trace"
            | "exit"
            | "help"
            | "reset"
            | "print" NAME
            | "numeric" <suite>
            | "from_numeric" NAME <statement>
            | "run_numeric" NAME <statement>
            | "eval" NAME
<expr_f> = <factor> [("*" | "/") <expr_f>]
<expr_e> = <expr_f> [("+" | "-") <expr_e>]
<expr_d> = <expr_e> [("<=" | "<" | ">=" | ">") <expr_d>]
<expr_c> = <expr_d> ["=" <expr_c>]
<expr_b> = <expr_c> ["&" <expr_b>]
<expr_a> = <expr_b> ["|" <expr_a>]
```

This logic can be seen implemented as code in `parser.py`. Compared to the
simpler grammars often quoted, this grammar provides proper operator
precedence.

## Notes on Göbel number calculation

Canonical While lacks certain features implemented in this interpreter.
Notable, the numeric comparisons are restricted to only `<=`, and boolean
comparisons to only `&`. Where possible, `@numeric` will attempt to convert
code into functionally equivalent code. This means `@from_numeric` may noy
always return the exact same code.

Following is a (potentially non-exhaustive) list of operations that has no such
equivalence implemented:

- Division. The `/` operator has no trivial alternative.
- `[variable] [& |] [variable]`. Canonical while disallows the storage of
    booleans in variables, and therefore this statement would make no sense.
- `@trace`. This is convert to `skip` when calculating Göbel numbers
- `@exit`
- `@print`. This is convert to `skip` when calculating Göbel numbers
- `@reset`
- `@help`. This is convert to `skip` when calculating Göbel numbers
- `@numeric`
- `@from_numeric`
- `@run_numeric`
- `@eval`
