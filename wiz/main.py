import sys
import os
from lexer import Lexer
from parser import Parser
from interpreter import Interpreter

VERSION = "0.8.4"
BANNER = """__        ___     
\ \      / (_)____
 \ \ /\ / /| |_  /
  \ V  V / | |/ / 
   \_/\_/  |_/___|
"""


def load_file(filename):
    if not filename.endswith(".wiz"):
        print("Error: expected a .wiz file")
        sys.exit(1)

    try:
        with open(filename, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: '{filename}' not found")
        sys.exit(1)


def print_help():
    print(f"""
Wiz Programming Language v{VERSION}

Usage:
    wiz <command> [file]

Commands:
    run <file.wiz>       Execute a Wiz program
    tokens <file.wiz>    Print lexer tokens
    ast <file.wiz>       Print parsed AST
    version              Show language version
    help                 Show this help
""")


def print_version():
    print(BANNER)
    print(f"Wiz Programming Language v{VERSION}")


def run(filename):
    source = load_file(filename)

    lexer = Lexer(source)
    tokens = lexer.tokenize()

    parser = Parser(tokens)
    tree = parser.parse()

    interpreter = Interpreter(os.path.dirname(filename))
    interpreter.visit(tree)


def print_tokens(filename):
    source = load_file(filename)

    lexer = Lexer(source)

    for token in lexer.tokenize():
        print(token)


def print_ast(filename):
    source = load_file(filename)

    lexer = Lexer(source)
    tokens = lexer.tokenize()

    parser = Parser(tokens)

    tree = parser.parse()

    print(tree)


def main():

    if len(sys.argv) < 2:
        print_help()
        return

    command = sys.argv[1]

    if command == "help":
        print_help()
        return

    if command == "version":
        print_version()
        return

    if len(sys.argv) != 3:
        print("Missing wiz command argument")
        return

    filename = sys.argv[2]

    if command == "run":
        run(filename)

    elif command == "tokens":
        print_tokens(filename)

    elif command == "ast":
        print_ast(filename)

    else:
        print(f"Unknown command '{command}'")
        print("Type 'wiz help'")


if __name__ == "__main__":
    main()