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
* Exceptions (try / catch / finally)
* Null Safety (null, ??, ?.)
* Standard Library
* Package Manager
* Static Linter
* Formatter
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

### Null Safety

`null` represents the absence of a value. The `??` operator returns the
left side unless it is `null`, and `?.` safely navigates members, methods
and indexes of possibly-`null` values.

```wiz
let name = null

echo(name ?? "unknown")    // unknown

let user = null

echo(user?.name ?? "guest")    // guest

echo(user?.name.upper())       // null (whole chain is safe)
```

A null value cannot be echoed directly. A trailing `?` marks a value as
safe to print, so the interpreter prints it as `null` instead of raising
a null error:

```wiz
let nick = null

echo(nick)    // Null Error: Cannot echo a null value
echo(nick?)   // null

let name = "Aydin"
echo(name?)   // Aydin

echo("a" + nick)    // a
echo("a" + nick?)   // anull
```

The null error is ordinary and can be caught with `try` / `catch`.

---

## Exceptions

Wiz supports error handling with `try`, `catch`, `finally` and `throw`.

```wiz
func divide(a, b) {
    when b == 0 {
        throw "cannot divide by zero"
    }
    return a / b
}

try {
    echo(divide(10, 0))
}
catch err {
    echo("caught: " + err)
}
finally {
    echo("cleanup done")
}
```

* `throw` raises any value; the message is the value's string form.
* `catch <name>` binds the caught error to a variable.
* `finally` always runs, even when an error, `return`, `break` or
  `continue` passes through.
* Runtime errors (bad index, unknown key, type errors, ...) are also
  catchable inside a `try` block.

`finally` on its own (without `catch`) is allowed.

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

### One-line Conditions

`when` can also be used as an expression that produces a value, in any
expression position (assignments, arguments, interpolated strings, ...).

```wiz
let status = when age >= 18 { "Adult" } else { "Child" }

echo($"You are {when age >= 18 { "adult" } else { "child" }}")
```

Braces are optional when the branches are single expressions:

```wiz
let allowed = when admin true else false
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

### One-line Functions

Functions can have an expression body with `=>`, returning the expression's
value. Anonymous functions can be created with `func(params) ...`.

```wiz
func is_even(n) => n % 2 == 0

let double = func(x) => x * 2

let max = func(a, b) => when a > b { a } else { b }

echo(is_even(4))
echo(double(5))
echo(max(3, 7))
```

Anonymous functions also support block bodies:

```wiz
let add = func(a, b) {
    return a + b
}
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

# Classes & Inheritance

Classes group state and behavior together.

```wiz
class Animal {

    let kingdom = "Animalia"

    func init(name, sound) {
        self.name = name
        self.sound = sound
    }

    func speak() {
        echo(self.name + " says " + self.sound)
    }

}

let animal = Animal("Cat", "Meow")

animal.speak()
```

A class can extend another class with `extends`, inheriting its methods and
class variables. The child may override inherited members and call the parent
with `super`.

```wiz
class Dog extends Animal {

    func init(name) {
        super.init(name, "Woof!")
    }

    func speak() {
        super.speak()
        echo("Also wags its tail")
    }

}

let dog = Dog("Rex")

dog.speak()
```

* Child classes inherit parent methods and class variables.
* Children can override any inherited method or variable.
* `super` calls the parent implementation from inside a child method.
* Inheritance chains (grandparent -> parent -> child) are supported.

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

Modules are resolved in this order:

```
stdlib
<current module dir>/<name>.wiz   (sibling file inside a module)
<name>.wiz                         (local project module)
~/.wiz/packages/<name>.wiz         (legacy flat global module)
~/.wiz/packages/<name>/            (global package: main.wiz or main.py)
```

---

# Package Manager

Wiz installs packages globally into the user's Wiz home directory
(`~/.wiz/packages`, overridable with the `WIZ_HOME` environment
variable). Once installed, a package is available to every project on
the machine.

Install every dependency declared in the current project's `wiz.pkg`:

```bash
python wiz/main.py install
```

Install a single package (optionally pinned to a tag):

```bash
python wiz/main.py install aydin-here/mylib
python wiz/main.py install aydin-here/mylib@v1.0.0
```

Install a package straight from a local directory (offline):

```bash
python wiz/main.py install ./packages/mylib
```

Remove, update and list packages:

```bash
python wiz/main.py uninstall mylib
python wiz/main.py update
python wiz/main.py update mylib
python wiz/main.py list
python wiz/main.py info mylib
```

`wiz update` re-fetches every installed package from its latest
(default) branch, dropping any `@tag` pin. `wiz update mylib` updates a
single installed package by name.

Installed packages live in `~/.wiz/packages/<name>/` and are imported
like any other module. Each package declares a `wiz.pkg` manifest with a
`name`, `version` and optional `type` (`"wiz"` by default, `"native"`
for Python-backed packages). Dependencies are installed recursively into
the same global store.

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

Format

```bash
python wiz/main.py format hello.wiz
```

Prints the formatted source to stdout. Pass `-w` to overwrite the file:

```bash
python wiz/main.py format hello.wiz -w
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
├── classes.wiz
├── decorators.wiz
├── dictionaries.wiz
├── exceptions.wiz
├── files.wiz
├── for_loop.wiz
├── functions.wiz
├── hello.wiz
├── inheritance.wiz
├── interpolated_strings.wiz
├── lists.wiz
├── modules.wiz
├── named_arguments.wiz
├── null_safety.wiz
├── one_line.wiz
├── switch_case.wiz
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

* Interfaces
* Enums
* Pattern Matching
* Lambdas
* Bytecode Compiler
* Virtual Machine
* REPL
* Debugger
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
