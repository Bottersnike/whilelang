import time
import sys

from whilelang import Lexer
from whilelang import Parser


def main():
    if len(sys.argv) < 2:
        print("Usage: while filename [...args]")
    filename = sys.argv[1]
    namespace = {}
    for n, i in enumerate(sys.argv[2:]):
        if i == "true":
            i = True
        elif i == "false":
            i = False
        elif i.isdigit():
            i = int(i)
        else:
            print(f"Invalid argument '{i}'")
            print("Only booleans and integers may be passed this way.")
            return
        namespace[f"_arg{n}"] = i
    with open(filename) as code_file:
        code = code_file.read()
    parser = Parser(Lexer(code))

    start = time.time_ns()
    parser.suite().visit(namespace)
    duration_ns = time.time_ns() - start
    print(f"Completed in {duration_ns / 1000000}ms")
    for i in namespace:
        if i.startswith("_"):
            continue
        print(f"{i} := {namespace[i]}")


if __name__ == "__main__":
    main()
