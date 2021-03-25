# Whilelang

Usage: `python while.py source.while [...arguments]`

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
<factor> = [("!" | "¬")] (NAME | NUMBER | BOOLEAN | "(" <expr_a> ")")
<expr_f> = <factor> [("*" | "/") <factor>]
<expr_e> = <expr_f> [("+" | "-") <expr_f>]
<expr_d> = <expr_e> [("<=" | "<" | ">=" | ">") <expr_e>]
<expr_c> = <expr_d> ["=" <expr_d>]
<expr_b> = <expr_c> ["&" <expr_c>]
<expr_a> = <expr_b> ["|" <expr_b>]
```

This logic can be seen implemented as code in `parser.py`. Compared to the
simpler grammars often quoted, this grammar provides proper operator
precedence.
