<img width="1254" height="1254" alt="Wiz Logo" src="https://github.com/user-attachments/assets/b08d3085-c609-4752-b567-b2de943afb6b" />


# Wiz Programming Language

Wiz is a small, educational programming language implemented in Python. It is built around a simple interpreter pipeline:

- `lexer.py` converts source text into tokens
- `parser.py` builds an abstract syntax tree (AST)
- `interpreter.py` executes the AST

The language is intentionally compact so learners can study interpreter design, language features, and runtime behavior without being overwhelmed.

## Version

Current version: `0.8.4`

## Language features

Wiz supports:

- Immutable and mutable variables with `let` and `var`
- Literal values: numbers, strings, booleans
- Arithmetic operators: `+`, `-`, `*`, `/`, `%`
- Comparison operators: `==`, `!=`, `>=`, `<=`, `>`, `<`
- Logical operators: `and`, `or`, `not`
- Conditionals: `when <condition> { ... } else { ... }`
- Loops: `while <condition> { ... }`
- `break` and `continue`
- Functions with `func name(params) { ... }` and `return`
- First-class function values and function calls
- Lists: `[a, b, c]`
- Dictionaries: `{ key: value, ... }`
- Indexing: `arr[0]`, `obj["key"]`
- Member access: `dict.key`, `module.function`, `string.upper()`
- Built-in standard library functions: `echo`, `get`, `str`, `num`, `bool`, `len`
- Module imports: `import module` loads `module.wiz` from the same directory

## Built-in types and methods

Wiz supports these built-in runtime types and methods:

- `list`
  - `append`, `pop`, `sort`, `reverse`, `remove`, `insert`, `copy`, `clear`, `extend`, `count`, `index`
- `dict`
  - `get`, `keys`, `values`, `items`, `pop`, `clear`, `update`, `copy`
- `str`
  - `upper`, `lower`, `replace`, `split`, `strip`

## CLI commands

Run the interpreter from the project root:

```bash
python3 wiz/main.py help
```

Available commands:

```bash
python3 wiz/main.py run <file.wiz>
python3 wiz/main.py tokens <file.wiz>
python3 wiz/main.py ast <file.wiz>
python3 wiz/main.py version
```

## Example programs

### Conditional example

```wiz
let age = 20

when age >= 18 {
    echo("Adult")
}
else {
    echo("Child")
}
```

### Function and loop example

```wiz
func factorial(n) {
    when n == 0 {
        return 1
    }

    return n * factorial(n - 1)
}

let result = factorial(5)
echo(result)
```

### List and dictionary example

```wiz
let items = [1, 2, 3, 4]
items.append(5)

let person = { "name": "Ava", "age": 25 }
echo(person.name)
echo(items[2])
echo(len(items))
```

### Module import example

```wiz
import utils

let greeting = utils.format_message("Wiz")
echo(greeting)
```

## Project structure

```text
wiz/
  interpreter.py   # Executes the parsed program
  lexer.py         # Converts source code into tokens
  main.py          # CLI entry point
  nodes.py         # AST node definitions
  parser.py        # Builds the AST from tokens
  runtime.py       # Module runtime support
  tokens.py        # Token and token-type definitions
examples/
  (empty)
```

## Contributing and extending Wiz

Wiz is designed for experimentation and learning. Good places to extend the language include:

- New keywords and syntax
- Additional expression and statement forms
- Standard library functions
- Error reporting and diagnostics
- A richer module system

If you want to contribute, start by exploring `wiz/parser.py`, `wiz/interpreter.py`, and `wiz/lexer.py`.
