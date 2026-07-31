### (This documentation is behind the current version and it is not up to date)

# Wiz Language Documentation

## Overview

Wiz is a lightweight interpreted programming language written in Python. It was built as an educational project to demonstrate how a programming language works internally, from lexical analysis and parsing to runtime execution.

Wiz focuses on simplicity while still supporting modern language features such as functions, named arguments, modules, collections, loops, conditions, and a small standard library.

Source files use the `.wiz` extension.

---

# Running Wiz

Execute programs from the project root:

```bash
python3 wiz/main.py run examples/hello.wiz
```

Show help:

```bash
python3 wiz/main.py help
```

Available CLI commands:

```text
run <file.wiz>       Execute a program
tokens <file.wiz>    Print lexer tokens
ast <file.wiz>       Print parsed AST
version              Show current version
help                 Show help
```

---

# Basic Syntax

## Comments

Single-line comments begin with `//`.

```wiz
// This is a comment

let age = 18
```

---

## Variables

Immutable variable:

```wiz
let name = "Aydin"
```

Mutable variable:

```wiz
var counter = 0
counter = counter + 1
```

Attempting to modify a `let` variable raises a runtime error.

---

# Data Types

Wiz currently supports:

## Numbers

```wiz
123
```

## Strings

```wiz
"Hello"
```

## Booleans

```wiz
true
false
```

## Lists

```wiz
[1, 2, 3]
```

## Dictionaries

```wiz
{
    "name": "Aydin",
    "age": 18
}
```

---

# Operators

## Arithmetic

```text
+
-
*
/
%
```

Example:

```wiz
let result = 5 * (3 + 2)
```

---

## Comparison

```text
==
!=
>
<
>=
<=
```

Example:

```wiz
when age >= 18 {
    echo("Adult")
}
```

---

## Logical

```text
and
or
not
```

Example:

```wiz
when logged_in and admin {
    echo("Welcome")
}
```

---

# Conditions

```wiz
when score >= 60 {
    echo("Passed")
}
else {
    echo("Failed")
}
```

---

# Loops

```wiz
var i = 0

while i < 5 {

    echo(i)

    i = i + 1
}
```

Supported loop controls:

```wiz
break
continue
```

---

# Functions

Simple function:

```wiz
func hello(name) {
    echo(name)
}

hello("Aydin")
```

Returning values:

```wiz
func add(a, b) {
    return a + b
}

echo(add(5, 7))
```

---

# Default Parameters

Parameters may have default values.

```wiz
func greet(name, age = 18) {

    echo(name)
    echo(age)
}

greet("Aydin")
```

Output:

```text
Aydin
18
```

---

# Named Arguments

Arguments may be passed by name.

```wiz
func hello(name, age) {

    echo(name)
    echo(age)
}

hello(
    age = 18,
    name = "Aydin"
)
```

Named arguments may appear in any order.

Mixing positional and named arguments is also supported.

```wiz
hello(
    "Aydin",
    age = 18
)
```

Rules:

* Unknown parameter names produce an error.
* Missing required parameters produce an error.
* Parameters cannot be assigned twice.
* Positional arguments automatically fill the next available parameter.

---

# Built-in Functions

## echo

Print a value.

```wiz
echo("Hello")
```

Supports keyword arguments because it wraps Python's `print()`.

```wiz
echo("Hello", end = "")
echo("World")
```

---

## get

Read input.

```wiz
let name = get("Name: ")
```

---

## len

```wiz
echo(len([1,2,3]))
```

---

## str

```wiz
echo(str(123))
```

---

## num

```wiz
echo(num("42"))
```

---

## bool

```wiz
echo(bool(1))
```

---

# Lists

```wiz
let items = [1,2,3]
```

Indexing:

```wiz
echo(items[0])
```

Assignment:

```wiz
items[0] = 10
```

Supported methods:

```text
append
pop
sort
reverse
remove
insert
copy
clear
extend
count
index
```

Example:

```wiz
items.append(5)
items.sort()
```

---

# Dictionaries

```wiz
let person = {
    "name": "Aydin",
    "age": 18
}
```

Index access:

```wiz
echo(person["name"])
```

Member access:

```wiz
echo(person.name)
```

Methods:

```text
get
keys
values
items
pop
clear
update
copy
```

---

# Strings

Methods:

```text
upper
lower
replace
split
strip
```

Example:

```wiz
let text = "hello"

echo(text.upper())
```

---

# Modules

Import another Wiz file:

```wiz
import utils
```

Call module functions:

```wiz
utils.say_hello()
```

Access module variables:

```wiz
echo(utils.VERSION)
```

Modules are loaded only once during execution.

---

# Standard Library

## files

```wiz
import files

let content = files.read("test.txt")

echo(content)

files.write("out.txt", "Hello")

files.append("out.txt", " World")
```

---

## json

```wiz
import json

let text = json.encode({
    "name": "Aydin"
})

echo(text)
```

---

## random

```wiz
import random

echo(random.randint(1,10))
```

---

## http

```wiz
import http

let page = http.get("https://example.com")

echo(page)
```

---

# Collections

Lists:

```wiz
let numbers = [5,2,9]

numbers.sort()

echo(numbers)
```

Dictionary:

```wiz
let config = {
    "debug": true
}

echo(config.debug)
```

---

# Example

```wiz
import random

func hello(name, age = 18)
{
    echo(name, end=" ")
    echo(age)
}

let user = "Aydin"

hello(user)

when random.randint(1,10) > 5 {

    echo("Lucky!")
}
else {

    echo("Try again!")
}
```

---

# Runtime Errors

The interpreter reports descriptive runtime errors, including:

* Undefined variable
* Undefined function
* Unknown parameter
* Missing required parameter
* Too many arguments
* Immutable variable modification
* Invalid index
* Missing dictionary key
* Unsupported method
* Module not found

---

# Project Architecture

```text
wiz/
├── lexer.py
├── parser.py
├── interpreter.py
├── nodes.py
├── tokens.py
├── runtime.py
├── main.py
└── stdlib/
    ├── files.py
    ├── http.py
    ├── json.py
    ├── random.py
    └── __init__.py

examples/
├── calculator.wiz
├── conditions.wiz
├── dictionaries.wiz
├── files.wiz
├── functions.wiz
├── hello.wiz
├── lists.wiz
├── modules.wiz
├── named_arguments.wiz
├── variables.wiz
└── while.wiz
```

---

# Current Features

* Variables (`let`, `var`)
* Numbers
* Strings
* Booleans
* Lists
* Dictionaries
* Arithmetic operators
* Comparison operators
* Logical operators
* `when / else`
* `while`
* `break`
* `continue`
* Functions
* Recursion
* Default parameters
* Named arguments
* Module imports
* Member access
* Collection methods
* Standard library (`files`, `http`, `json`, `random`)
* Comments (`//`)
* AST printer
* Token printer
* CLI interface

---

# Planned Features

Future versions may include:

* Floating-point numbers
* Classes
* Enums
* Match expressions
* Lambdas
* Package manager
* Bytecode compiler
* Native executable compilation
* Better error diagnostics
* VS Code Language Server
