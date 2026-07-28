# <p align="center"><img src="https://github.com/user-attachments/assets/b08d3085-c609-4752-b567-b2de943afb6b" width="220"></p>

<h1 align="center">Wiz Programming Language</h1>

<p align="center">
  <strong>A small, educational programming language written in Python.</strong><br>
  Designed to make interpreter and programming language development easy to understand.
</p>

<p align="center">
  <img src="https://img.shields.io/github/v/tag/aydin-here/wiz?label=version&sort=semver">
  <img src="https://img.shields.io/github/license/aydin-here/wiz">
  <img src="https://img.shields.io/badge/python-3.10%2B-blue">
  <img src="https://img.shields.io/github/actions/workflow/status/aydin-here/wiz/release.yml?branch=main">
  <img src="https://img.shields.io/github/downloads/aydin-here/wiz/total">
  <img src="https://img.shields.io/github/stars/aydin-here/wiz?style=social">
</p>

---

# About

Wiz is a lightweight interpreted programming language implemented entirely in Python.

The goal of the project is **education**, not performance.

Instead of hiding language internals behind complicated code, Wiz keeps every component readable and easy to extend so anyone can learn how programming languages actually work.

The project contains:

* Lexer
* Parser
* AST
* Tree-walking Interpreter
* Runtime
* Module System
* Standard Library
* VSCode Extension
* Automatic Releases

Everything is written in pure Python.

---

# Features

Current language features include:

## Variables

* Immutable variables (`let`)
* Mutable variables (`var`)
* Assignment

```wiz
let pi = 3.14

var counter = 0

counter = counter + 1
```

---

## Data Types

* Number
* String
* Boolean
* List
* Dictionary

```wiz
let number = 15
let text = "Hello"
let flag = true

let list = [1,2,3]

let person = {
    "name": "Aydin",
    "age": 14
}
```

---

## Operators

Arithmetic

```
+
-
*
/
%
```

Comparison

```
==
!=
>
<
>=
<=
```

Logical

```
and
or
not
```

---

## Conditions

```wiz
when age >= 18
{
    echo("Adult")
}
else
{
    echo("Child")
}
```

---

## While Loops

```wiz
var i = 0

while i < 5
{
    echo(i)
    i = i + 1
}
```

Supports

* break
* continue

---

## Functions

```wiz
func hello(name)
{
    echo(name)
}

hello("Aydin")
```

Supports

* return
* recursion
* named arguments
* positional arguments
* default values

Example

```wiz
func hello(name, age=18)
{
    echo(name)
    echo(age)
}

hello("Aydin")

hello(
    age=20,
    name="John"
)
```

Mixed arguments are also supported.

---

## Comments

```wiz
// This is a comment
```

---

## Lists

```wiz
let numbers = [1,2,3]

numbers.append(4)

echo(numbers)
```

Built-in methods

* append
* pop
* insert
* remove
* clear
* reverse
* sort
* copy
* extend
* count
* index

---

## Dictionaries

```wiz
let person = {
    "name":"Aydin",
    "age":14
}

echo(person.name)

echo(person["age"])
```

Built-in methods

* get
* keys
* values
* items
* pop
* update
* copy
* clear

---

## Strings

Supported methods

* upper
* lower
* replace
* split
* strip

```wiz
let name = "wiz"

echo(name.upper())
```

---

## Standard Library

Currently available modules

### files

```wiz
import files

let text = files.read("hello.txt")
```

---

### json

```wiz
import json
```

---

### random

```wiz
import random
```

---

### http

```wiz
import http
```

---

## Imports

```wiz
import utils

utils.sayHello()
```

Modules are loaded from

```
module.wiz
```

inside the current project.

---

# Built-in Functions

```
echo()
get()

str()
num()
bool()

len()
```

---

# Command Line

Show help

```bash
python wiz/main.py help
```

Run a program

```bash
python wiz/main.py run hello.wiz
```

Print tokens

```bash
python wiz/main.py tokens hello.wiz
```

Print AST

```bash
python wiz/main.py ast hello.wiz
```

Version

```bash
python wiz/main.py version
```

---

# Example Programs

The repository contains ready-to-run examples.

```
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

Run any example

```bash
python wiz/main.py run examples/hello.wiz
```

---

# Project Structure

```text
.
├── documentation.md
├── examples
│   ├── calculator.wiz
│   ├── conditions.wiz
│   ├── dictionaries.wiz
│   ├── files.wiz
│   ├── functions.wiz
│   ├── hello.wiz
│   ├── lists.wiz
│   ├── modules.wiz
│   ├── named_arguments.wiz
│   ├── variables.wiz
│   └── while.wiz
├── .github
│   └── workflows
│       └── release.yml
├── LICENSE
├── README.md
└── wiz
    ├── interpreter.py
    ├── lexer.py
    ├── main.py
    ├── nodes.py
    ├── parser.py
    ├── runtime.py
    ├── tokens.py
    └── stdlib
        ├── files.py
        ├── http.py
        ├── json.py
        ├── random.py
        └── __init__.py
```

---

# VSCode Extension

A dedicated Visual Studio Code extension is available.

Features

* Syntax Highlighting
* Comments
* Keywords
* Functions
* Numbers
* Strings
* Operators

Install

```
wiz-*.vsix
```

or install it directly from the Marketplace once published.

---

# Building

Create a standalone executable

```bash
pyinstaller \
    --onefile \
    --name wiz \
    wiz/main.py
```

---

# Documentation

More implementation details are available in

```
documentation.md
```

---

# Roadmap

Planned features

* Classes
* Interfaces
* Enums
* Pattern Matching
* Lambda Expressions
* Switch Statement
* For Loops
* Package Manager
* Bytecode Compiler
* Virtual Machine
* Language Server (LSP)
* Debugger
* REPL
* Official Formatter
* Package Registry

---

# Contributing

Contributions are welcome.

Possible areas to improve

* Parser
* Interpreter
* Error reporting
* Standard Library
* Optimizations
* Documentation
* VSCode Extension

---

# License

This project is licensed under the MIT License.

See the **LICENSE** file for details.

---

<p align="center">
Made with ❤️ using Python.
</p>
