# <p align="center"><img src="https://github.com/user-attachments/assets/b08d3085-c609-4752-b567-b2de943afb6b" width="220"></p>

<h1 align="center">Wiz Programming Language</h1>

<p align="center">
  <strong>A modern educational programming language written entirely in Python.</strong><br>
  Built to learn how interpreters and programming languages work without unnecessary complexity.
</p>

<p align="center">
  <img src="https://img.shields.io/github/v/tag/aydin-here/wiz?label=version&sort=semver">
  <img src="https://img.shields.io/github/license/aydin-here/wiz">
  <img src="https://img.shields.io/badge/python-3.10%2B-blue">
  <img src="https://img.shields.io/github/downloads/aydin-here/wiz/total">
  <img src="https://img.shields.io/github/stars/aydin-here/wiz?style=social">
</p>

---

# About

Wiz is a lightweight interpreted programming language implemented completely in Python.

The goal of Wiz is **education**, not performance.

Instead of hiding implementation details behind thousands of lines of code, Wiz keeps every part of the language readable so anyone can understand how a programming language actually works.

The language currently contains:

* Lexer
* Parser
* AST
* Tree-Walking Interpreter
* Runtime
* Module System
* Decorator System
* Standard Library
* Package Manager
* Static Linter
* VSCode Extension

Everything is written using pure Python.

---

# Language Features

## Variables

### Immutable

```wiz
let pi = 3.14
```

### Mutable

```wiz
var counter = 0

counter = counter + 1
```

---

## Data Types

Supported types

* Number
* String
* Boolean
* List
* Dictionary
* Null

```wiz
let age = 14
let name = "Aydin"
let admin = false

let numbers = [1,2,3]

let user = {
    "name": "Aydin",
    "age": 14
}
```

---

## Operators

### Arithmetic

```
+
-
*
/
%
```

### Comparison

```
==
!=
>
<
>=
<=
```

### Logical

```
and
or
not
```

---

## Conditions

```wiz
when age >= 18 {
    echo("Adult")
}
else {
    echo("Child")
}
```

---

## Switch Statement

```wiz
switch day {

    case 1 {
        echo("Monday")
    }

    case 2 {
        echo("Tuesday")
    }

    default {
        echo("Unknown")
    }

}
```

---

## While Loop

```wiz
var i = 0

while i < 5 {

    echo(i)

    i = i + 1

}
```

Supports

* break
* continue

---

## For Loop

Numeric loop

```wiz
for i in 0..10 {

    echo(i)

}
```

With step

```wiz
for i in 0..20 step 2 {

    echo(i)

}
```

Iterable loop

```wiz
let numbers = [1,2,3]

for number in numbers {

    echo(number)

}
```

Supports

* break
* continue

---

# Functions

```wiz
func hello(name) {

    echo(name)

}

hello("Aydin")
```

Supports

* Return values
* Default values
* Named arguments
* Positional arguments
* Mixed arguments
* Recursion

Example

```wiz
func hello(name, age=18) {

    echo(name)
    echo(age)

}

hello("Aydin")

hello(
    age=20,
    name="John"
)
```

---

# Decorators

Wiz supports decorators for modifying function behavior.

## Built-in Decorators

### Timer

```wiz
#timer

func hello() {

    return 5

}

hello()
```

Output

```
0.000012s
```

---

### Deprecated

```wiz
#deprecated

func old_function() {

}

old_function()
```

Output

```
Warning: old_function is deprecated
```

---

## Custom Decorators

Decorators can also be written directly in Wiz.

```wiz
decorator on_command(command) {

    define(ctx) {

        echo($"Registering {ctx.function.name}")

    }

    before(ctx) {

        echo("Executing command")

    }

    after(ctx, state) {

        echo($"Finished {command}")

    }

    error(ctx) {

        echo("Command failed")

    }

}
```

Usage

```wiz
#on_command("start")

func start() {

    echo("Hello!")

}

start()
```

### Available Hooks

| Hook   | Description                                            |
| ------ | ------------------------------------------------------ |
| define | Executed when the decorator is defined for a function  |
| before | Executed before the function                           |
| after  | Executed after the function                            |
| error  | Executed if the function throws an error               |

---

## String Interpolation

```wiz
let name = "Wiz"

echo($"Hello {name}")
```

---

## Lists

```wiz
let numbers = [1,2,3]

numbers.append(4)

echo(numbers)
```

Available methods

* append
* pop
* insert
* remove
* clear
* copy
* reverse
* sort
* extend
* count
* index

---

## Dictionaries

```wiz
let person = {

    "name": "Aydin",
    "age": 14

}

echo(person.name)

echo(person["age"])
```

Available methods

* get
* keys
* values
* items
* update
* pop
* clear
* copy

---

## Strings

```wiz
let text = "wiz"

echo(text.upper())
```

Available methods

* upper
* lower
* replace
* split
* strip

---

# Standard Library

Current modules

```
archive   bars      clipboard
colors    console   crypto
database  date      files
gtk       html      http
image     json      math
matrix    os        process
random    re        socket
sys       table     text
thread    time      tk
yaml
```

Example

```wiz
import files

let text = files.read("hello.txt")
```

---

# Imports

```wiz
import math

math.sum(1,2)
```

Modules are loaded from

```
module.wiz
wiz_modules/module.wiz
wiz_modules/module/module.wiz
```

inside the current project.

---

# Package Manager

Wiz can install packages directly from GitHub.

Install all dependencies from `wiz.pkg`:

```bash
python wiz/main.py install
```

Install a single package (optionally pinned to a tag):

```bash
python wiz/main.py install aydin-here/mylib
python wiz/main.py install aydin-here/mylib@v1.0.0
```

Remove, update and list packages:

```bash
python wiz/main.py uninstall mylib
python wiz/main.py update
python wiz/main.py update mylib
python wiz/main.py list
```

`wiz update` re-fetches every installed package from its latest
(default) branch, dropping any `@tag` pin. `wiz update mylib` updates a
single installed package by name.

Installed packages are extracted into `wiz_modules/` and imported like
any other module. Each package can declare a `wiz.pkg` manifest with a
`name`, `version`, and `dependencies`, which are installed recursively.

```wiz
import mylib

mylib.greet("Wiz")
```

---

# Self-Update

Wiz can update itself by checking the latest release on GitHub.

Check for a newer release without installing:

```bash
python wiz/main.py update-self --check
```

Download and apply the latest release:

```bash
python wiz/main.py update-self
```

`wiz upgrade` is an alias for `wiz update-self`. The update compares the
current version with the newest release tag on `github.com/aydin-here/wiz`:

- Installed from a compiled binary: the matching platform binary
  (`wiz-linux`, `wiz-macos`, `wiz-windows.exe`) is downloaded and
  replaces the running executable.
- Running from source: the source tarball of that release tag is
  downloaded and extracted over the `wiz/` package.

---

# Linter

Wiz ships with a static linter that analyzes a file without running it.

```bash
python wiz/main.py lint hello.wiz
```

If no problems are found:

```text
  examples/hello.wiz: no issues found
```

Reported problems look like:

```text
  examples/bad.wiz:13:1  W005  Cannot assign to immutable variable 'count'
  examples/bad.wiz:15:1  W008  'break' used outside of a loop
```

### Checks

| Code  | Severity | Description                                    |
| ----- | -------- | ---------------------------------------------- |
| E001  | error    | Syntax or lexical error                        |
| S001  | style    | Trailing whitespace                            |
| S002  | style    | Missing newline at end of file                 |
| W001  | warning  | Duplicate function in the same scope           |
| W002  | warning  | Variable already declared in the same scope    |
| W003  | warning  | Function defined but never used                |
| W004  | warning  | Variable declared but never used               |
| W005  | warning  | Assignment to an immutable (`let`) variable    |
| W008  | warning  | `break` / `continue` outside a loop            |
| W009  | warning  | `return` outside a function                    |
| W010  | warning  | Unreachable code after return / break / continue |
| W011  | warning  | Call to an undefined function                  |
| W012  | warning  | Use of an undefined decorator                  |

---

# Built-in Functions

```
echo()

get()

len()

str()

num()

bool()
```

---

# Command Line

Run

```bash
python wiz/main.py run hello.wiz
```

Tokens

```bash
python wiz/main.py tokens hello.wiz
```

AST

```bash
python wiz/main.py ast hello.wiz
```

Version

```bash
python wiz/main.py version
```

Packages

```bash
python wiz/main.py install aydin-here/mylib
python wiz/main.py update
python wiz/main.py uninstall mylib
python wiz/main.py list
```

Lint

```bash
python wiz/main.py lint hello.wiz
```

Help

```bash
python wiz/main.py help
```

---

# Example Programs

```
examples/

├── calculator.wiz
├── decorators.wiz
├── dictionaries.wiz
├── files.wiz
├── for.wiz
├── functions.wiz
├── hello.wiz
├── interpolation.wiz
├── lists.wiz
├── modules.wiz
├── named_arguments.wiz
├── switch.wiz
├── variables.wiz
└── while.wiz
```

Run any example

```bash
python wiz/main.py run examples/decorators.wiz
```

---

# Project Structure

```text
wiz/

├── decorators.py
├── errors.py
├── interpreter.py
├── lexer.py
├── linter.py
├── main.py
├── nodes.py
├── package_manager.py
├── parser.py
├── runtime.py
├── stdlib
│   ├── files.py
│   ├── http.py
│   ├── json.py
│   ├── random.py
│   └── __init__.py
├── tokens.py
└── vscode-extension
```

---

# VSCode Extension

The official extension provides

* Syntax Highlighting
* Keywords
* Decorators
* Hooks
* Built-in Functions
* Numbers
* Strings
* Variables
* Parameters
* Comments

---

# Roadmap

Upcoming features

* Classes
* Interfaces
* Enums
* Pattern Matching
* Exceptions
* Lambdas
* Bytecode Compiler
* Virtual Machine
* REPL
* Debugger
* Formatter
* Package Registry
* Language Server Protocol (LSP)

---

# Contributing

Pull requests are always welcome.

Areas that can be improved

* Interpreter
* Parser
* Error Reporting
* Runtime
* Standard Library
* VSCode Extension
* Documentation

---

# License

This project is licensed under the MIT License.

See the **LICENSE** file for more information.

---

<p align="center">
Made with ❤️ in Python.<br>
Aydin Rahbaran &copy 2026
</p>
