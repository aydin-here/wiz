import sys
import os
from lexer import Lexer
from parser import Parser
from interpreter import Interpreter
from errors import WizError
from package_manager import (
    install_package,
    install_all,
    update_package,
    update_all,
    uninstall_package,
    list_packages
)
from linter import Linter

VERSION = "0.18.8"
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
    wiz <command> [args...]

Commands:
    run <file.wiz>                Execute a Wiz program
    tokens <file.wiz>             Print lexer tokens
    ast <file.wiz>                Print parsed AST
    lint <file.wiz>               Statically analyze a Wiz file
    install [owner/repo[@tag]]    Install all dependencies or a package
    update [package]              Update all packages or a specific one
    uninstall <package>           Remove an installed package
    list                          List installed packages
    version                       Show language version
    help                          Show this help
""")


def print_version():
    print(BANNER)
    print(f"Wiz Programming Language v{VERSION}")


def run(filename):
    source = load_file(filename)

    try:
        lexer = Lexer(source)
        tokens = lexer.tokenize()

        parser = Parser(tokens)
        tree = parser.parse()

        interpreter = Interpreter(os.path.dirname(filename))
        interpreter.visit(tree)

    except WizError as e:
        e.attach_source(source)
        e.filename = filename
        print(e)
        sys.exit(1)
    except Exception as e:
        print("┌──────────────────────────────┐")
        print("│        INTERNAL WIZ ERROR    │")
        print("└──────────────────────────────┘")
        print()
        print(f"An unexpected error occurred in {filename}:")
        print()
        print(f"  {type(e).__name__}: {e}")
        sys.exit(1)


def print_tokens(filename):
    source = load_file(filename)

    try:
        lexer = Lexer(source)

        for token in lexer.tokenize():
            print(token)
    except WizError as e:
        e.attach_source(source)
        e.filename = filename
        print(e)
        sys.exit(1)


def print_ast(filename):
    source = load_file(filename)

    try:
        lexer = Lexer(source)
        tokens = lexer.tokenize()

        parser = Parser(tokens)

        tree = parser.parse()

        print(tree)
    except WizError as e:
        e.attach_source(source)
        e.filename = filename
        print(e)
        sys.exit(1)


def lint(filename):
    source = load_file(filename)

    linter = Linter(source, filename)
    issues = linter.run()

    if not issues:
        print(f"  {filename}: no issues found")
        return

    counts = {}

    for issue in issues:
        counts[issue["severity"]] = counts.get(issue["severity"], 0) + 1

    print(f"  Analyzing {filename}")

    for issue in issues:
        location = f"{filename}:{issue['line']}:{issue['column']}"
        marker = "ERROR" if issue["severity"] == "error" else issue["code"]
        print(f"  {location}  {marker}  {issue['message']}")

    summary = ", ".join(
        f"{count} {severity}"
        for severity, count in sorted(counts.items())
    )

    print(f"  {summary} found")


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

    if command == "install":
        try:
            if len(sys.argv) == 3:
                install_package(sys.argv[2])
            elif len(sys.argv) == 2:
                install_all()
            else:
                print("Usage: wiz install [owner/repo[@tag]]")
        except WizError as error:
            print(f"Error: {error.message}")
            sys.exit(1)
        return

    if command == "uninstall":
        if len(sys.argv) != 3:
            print("Usage: wiz uninstall <package>")
            return
        try:
            uninstall_package(sys.argv[2])
        except WizError as error:
            print(f"Error: {error.message}")
            sys.exit(1)
        return

    if command == "update":
        try:
            if len(sys.argv) == 3:
                update_package(sys.argv[2])
            elif len(sys.argv) == 2:
                update_all()
            else:
                print("Usage: wiz update [package]")
        except WizError as error:
            print(f"Error: {error.message}")
            sys.exit(1)
        return

    if command == "list":
        try:
            list_packages()
        except WizError as error:
            print(f"Error: {error.message}")
            sys.exit(1)
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

    elif command == "lint":
        lint(filename)

    else:
        print(f"Unknown command '{command}'")
        print("Type 'wiz help'")


if __name__ == "__main__":
    main()