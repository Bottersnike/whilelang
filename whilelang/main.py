import time
import sys

from .lexer import Lexer
from .parser import Parser


def run(code, initial=None):
    namespace = initial
    if namespace is None:
        namespace = {}

    parser = Parser(Lexer(code))

    start = time.time_ns()
    parser.suite().visit(namespace)
    return time.time_ns() - start


def main():
    if len(sys.argv) < 2:
        print("Usage: while filename [...args]")
        return
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

    duration_ns = run(code, namespace)
    print(f"Completed in {duration_ns / 1000000}ms")
    for i in namespace:
        if i.startswith("_"):
            continue
        print(f"{i} := {namespace[i]}")