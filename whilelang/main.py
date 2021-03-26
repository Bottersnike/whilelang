import traceback
import argparse
import time
import sys

from .lexer import Lexer
from .parser import Parser
from .errors import WhileSystemExit, WhileError


def run(code, initial=None):
    namespace = initial
    if namespace is None:
        namespace = {}

    try:
        parser = Parser(Lexer(code))

        start = time.time_ns()
        parser.program().visit(namespace)
    except WhileSystemExit:
        pass
    except WhileError as e:
        print(e)
        return -1
    return time.time_ns() - start


def repl(args):
    print(
        "While interpreter running on Python "
        f"{sys.version_info.major}.{sys.version_info.minor}"
    )
    print("Type @help for basic help, @reset to reset the repl, "
          "and @exit to exit")
    namespace = {}
    while True:
        try:
            code = input(">>> ")
        except KeyboardInterrupt:
            print()
            continue
        if not code.strip():
            continue

        try:
            ast = Parser(Lexer(code)).program()

            if args.numeric:
                print(ast.numeric())
            else:
                if (ret := ast.visit(namespace)) is not None:
                    print(ret)
        except WhileSystemExit:
            break
        except WhileError as e:
            print(e)
        except:  # noqa: E722
            traceback.print_exc()


def main():
    parser = argparse.ArgumentParser(prog="while")
    parser.add_argument(
        "source", default=None, nargs="?",
        help="Source code, or path to source file",
    )
    parser.add_argument(
        "-c", "--code", action="store_true",
        help="Interpret source as source, not a filename",
    )
    parser.add_argument(
        "-n", "--numeric", action="store_true",
        help="Calculate the Gobel number rather than evaluating",
    )
    parser.add_argument(
        "arguments", nargs="*",
        help="Arguments to pass to the program",
    )
    args = parser.parse_args()

    namespace = {}
    for n, i in enumerate(args.arguments):
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

    if not args.source:
        repl(args)
        return

    if not args.code:
        try:
            with open(args.source) as source_file:
                source = source_file.read()
        except FileNotFoundError:
            print(f"while: {args.code}: No such file or directory")
            return
    else:
        source = args.source

    if args.numeric:
        try:
            num = Parser(Lexer(source)).suite().numeric()
        except WhileError as e:
            print(e)
        else:
            print(num)
        return

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

    duration_ns = run(source, namespace)
    print(f"Completed in {duration_ns / 1000000}ms")
    for i in namespace:
        if i.startswith("_"):
            continue
        print(f"{i} := {namespace[i]}")