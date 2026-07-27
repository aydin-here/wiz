# Wiz Language Documentation

## Overview

Wiz is a minimal educational programming language written in Python. It is designed to be easy to understand and extend while supporting a small but useful set of programming primitives.

Wiz source files use the `.wiz` extension and are executed through the CLI entry point `wiz/main.py`.

## Getting started

From the project root, run:

```bash
python3 wiz/main.py help
```

This shows the available commands:

- `run <file.wiz>` — execute a Wiz program
- `tokens <file.wiz>` — print lexer tokens
- `ast <file.wiz>` — print parsed AST
- `version` — show language version

Example:

```bash
python3 wiz/main.py run examples/hello.wiz
```

## Language syntax

### Files and whitespace

- Wiz source is tokenized line by line.
- Newlines are meaningful and may separate statements.
- There is no comment syntax in the current implementation.
- Only double-quoted strings are supported.

### Literals

Wiz supports:

- numbers: `123`
- strings: `"hello"`
- booleans: `true`, `false`
- lists: `[1, 2, 3]`
- dictionaries: `{ "key": "value", "age": 30 }`

### Variables

Wiz supports two forms of variable declaration:

- `let x = 10` — declares an immutable variable
- `var x = 10` — declares a mutable variable

Example:

```wiz
let name = "Ava"
var count = 1
count = count + 1
```

Attempting to assign to a `let` variable produces a runtime error.

### Expressions

#### Arithmetic

- `+` addition
- `-` subtraction
- `*` multiplication
- `/` division
- `%` modulo

Example:

```wiz
let total = 5 * (3 + 2)
```

#### Comparison

- `==` equal
- `!=` not equal
- `>` greater than
- `<` less than
- `>=` greater than or equal
- `<=` less than or equal

Example:

```wiz
let ok = score >= 60
```

#### Logical operators

- `and`
- `or`
- `not`

Example:

```wiz
when not active or count == 0 {
    echo("inactive")
}
```

#### Grouping

Parentheses can group expressions:

```wiz
let value = (a + b) * c
```

#### Identifiers

Identifiers are names for variables, functions, and modules. They may contain letters, digits, and underscores but must start with a letter or underscore.

### Indexing

Lists and dictionaries support indexing with square brackets:

```wiz
let list = [10, 20, 30]
echo(list[1])

let obj = { "name": "Wiz" }
echo(obj["name"])
```

### Member access and method calls

Wiz supports the dot operator for member access and methods.

- `obj.key` accesses a dictionary entry or module member
- `obj.method(args)` calls methods on built-in objects or module functions

Built-in methods currently supported:

- `list.append(value)`
- `list.pop(index?)`
- `list.sort()`
- `list.reverse()`
- `list.remove(value)`
- `list.insert(index, value)`
- `list.copy()`
- `list.clear()`
- `list.extend(other)`
- `list.count(value)`
- `list.index(value)`
- `dict.get(key)`
- `dict.keys()`
- `dict.values()`
- `dict.items()`
- `dict.pop(key)`
- `dict.clear()`
- `dict.update(other)`
- `dict.copy()`
- `str.upper()`
- `str.lower()`
- `str.replace(a, b)`
- `str.split(sep?)`
- `str.strip()`

Example:

```wiz
let text = "Hello"
echo(text.upper())

let data = { "name": "Ava" }
echo(data.name)
```

### Function calls

Functions and built-in routines are invoked with parentheses:

```wiz
echo("Hello")
let count = len([1, 2, 3])
```

### Built-in functions

Wiz includes these built-in functions:

- `echo(value)` — print a value to standard output
- `get()` — read a line from standard input
- `str(value)` — convert to string
- `num(value)` — convert to integer
- `bool(value)` — convert to boolean
- `len(value)` — get length of list, string, or dictionary

## Statements

### Conditional branching

Wiz uses `when` and optional `else` blocks:

```wiz
when count > 0 {
    echo("positive")
}
else {
    echo("zero or negative")
}
```

### Loops

A `while` loop repeats while the condition is true:

```wiz
var i = 0
while i < 5 {
    echo(i)
    i = i + 1
}
```

Inside loops, you may use:

- `break` — exit the loop early
- `continue` — skip to the next iteration

### Functions

Define functions with `func` and return values with `return`:

```wiz
func add(a, b) {
    return a + b
}

let result = add(2, 3)
echo(result)
```

If a function does not explicitly return a value, it returns `None`.

### Importing modules

Use `import` to load another `.wiz` file from the same directory.

```wiz
import utils
let message = utils.format_message("Wiz")
echo(message)
```

The imported module is available as a namespace object. Its variables and functions are accessed by dot notation.

## Scope and mutability

- Variables declared with `let` are immutable.
- Variables declared with `var` are mutable.
- Each block and function call creates a new local scope.
- Function calls also capture the surrounding function definitions.

## Example programs

### Hello world

```wiz
echo("Hello, Wiz!")
```

### Counter loop

```wiz
var count = 1
while count <= 5 {
    echo("Count: " + str(count))
    count = count + 1
}
```

### Recursive factorial

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

### Working with collections

```wiz
let numbers = [5, 2, 9, 1]
numbers.sort()
echo(numbers)

echo(numbers[0])

echo(len(numbers))

let settings = { "debug": true, "theme": "dark" }
echo(settings.debug)
```

### Module example

`utils.wiz`:

```wiz
func format_message(name) {
    return "Hello, " + name
}
```

`main.wiz`:

```wiz
import utils
let message = utils.format_message("Wiz")
echo(message)
```

### Standard libraries example

`main.wiz`:

- Http library is for connecting and sending get/post requests to pages
```wiz
import http

let response = http.get("https://example.com")

echo(response)
```

- random library is to get a random integer between two numbers or select one random index in a list
```wiz
import random

echo(random.randint(1,5))
```

## Implementation notes

- The lexer recognizes keywords, identifiers, numbers, strings, symbols, and newlines.
- The parser supports expressions, statements, blocks, function definitions, and module imports.
- The interpreter executes the AST and maintains a stack of scopes.
- Built-in methods are implemented for Python `list`, `dict`, and `str` values.

## Limitations

- There is no comment syntax yet.
- Error messages are runtime exceptions and may not show source locations.
- There is no support for floating-point numbers.
- Only `true` and `false` are supported boolean literals.

## Extending Wiz

Useful extension points:

- add comments and improved parser diagnostics
- support additional operators and data types
- add string interpolation or formatted output
- support modules from nested directories
- add a standard library of utility functions
