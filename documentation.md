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
run <file.wiz>                Execute a program
tokens <file.wiz>             Print lexer tokens
ast <file.wiz>                Print parsed AST
lint <file.wiz>               Statically analyze a Wiz file
install [owner/repo[@tag]]    Install all dependencies or a package
update [package]              Update all packages or a specific one
uninstall <package>           Remove an installed package
list                          List installed packages
info <package>                Show details about an installed package
version                       Show current version
help                          Show help
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

# Packages

Packages are shareable libraries that you install **globally**. They are
stored in your Wiz home directory (`~/.wiz/packages`, overridable with
the `WIZ_HOME` environment variable) and are available to **every
project** on the machine, like Python's global site-packages rather than
a per-project `venv`. They are imported like any other module:

```wiz
import hello_wiz

hello_wiz.hello("Wiz")
echo(hello_wiz.VERSION)
```

A package is either a **Wiz package** (implemented in Wiz) or a
**native package** (implemented in Python). Both kinds look the same from
Wiz code; only the manifest `type` and the entry file differ.

---

## The `wiz.pkg` manifest

Every project *and* every package may carry a JSON manifest called
`wiz.pkg`. A project manifest lists the dependencies the project wants;
a package manifest describes the package itself. The project manifest is
optional — you only need one if you want `wiz install` (with no
arguments) to reinstall your declared dependencies.

Example project manifest:

```json
{
    "name": "my-app",
    "version": "1.0.0",
    "dependencies": {
        "hello_wiz": "owner/repo",
        "hello_native": "./packages/hello_native"
    }
}
```

Fields:

| Field | Required | Description |
| ----- | -------- | ----------- |
| `name` | yes | Package name, used as the install directory under `~/.wiz/packages/` |
| `version` | yes | Semantic version, e.g. `"1.0.0"` |
| `type` | no | `"wiz"` (default) or `"native"`; see [Package types](#package-types) |
| `entry` | no | Entry file, relative to the package directory. Defaults to `main.wiz` (wiz) or `main.py` (native) |
| `description` | no | Short human description |
| `author` | no | Package author |
| `license` | no | License identifier, e.g. `"MIT"` |
| `repository` | no | Source URL |
| `dependencies` | no | Map of package name to dependency spec (`owner/repo[@tag]` or a local path) |
| `python_dependencies` | no | Python modules a native package needs (see [Native packages](#native-packages)) |
| `wiz_version` | no | Minimum compatible interpreter version, e.g. `">=0.22.0"` |

---

## Installing packages

Install every dependency listed in the current project's `wiz.pkg` into
the global store:

```bash
python3 wiz/main.py install
```

Install a package from GitHub:

```bash
python3 wiz/main.py install owner/repo
python3 wiz/main.py install owner/repo@v1.0.0
```

Install a package from a local directory (offline):

```bash
python3 wiz/main.py install ./packages/hello_wiz
```

Packages are downloaded as GitHub tarballs and extracted into
`~/.wiz/packages/<name>/`. A package may declare its own dependencies,
which are installed recursively into the same global store. A record of
every installed package and its source spec is kept in
`~/.wiz/packages.json`. Reinstalling an already-installed package
replaces it in place. Installing never modifies the current project's
files.

---

## Managing packages

List globally installed packages with their version and type:

```bash
python3 wiz/main.py list
```

Show the manifest of an installed package:

```bash
python3 wiz/main.py info mylib
```

Update all packages to their latest versions:

```bash
python3 wiz/main.py update
```

Update a single installed package by name:

```bash
python3 wiz/main.py update mylib
```

Remove a package:

```bash
python3 wiz/main.py uninstall mylib
```

Updating re-fetches each package from its latest (default) branch and
removes any `@tag` pin from the registry.

---

## Package types

Every package directory contains a `wiz.pkg` manifest. The `type` field
decides which implementation the package uses and, therefore, which file
is its entry point:

| `type` | Implementation | Entry file | Description |
| ------ | -------------- | ---------- | ----------- |
| `wiz` (default) | Wiz | `main.wiz` | A package written entirely in Wiz |
| `native` | Python | `main.py` | A package written in Python (always native) |

Rules:

- If `type` is omitted, it **defaults to `wiz`** — the package is a Wiz
  package.
- `"native"` means the package is implemented in Python and exposes
  callable functions to Wiz.
- `"python"` is accepted as a legacy alias for `"native"` and is
  normalized to `"native"` when the manifest is read.
- Any other value is rejected with an `UnsupportedPackageTypeError`.

---

## How imports resolve

When you `import <name>`, the interpreter looks in this order:

1. **Stdlib modules** — built-in modules (`files`, `json`, `random`,
   `http`, ...). They are resolved before anything else and can never be
   shadowed by an installed package.
2. **Inside a module**, a sibling file in that module's own directory
   (`<module_dir>/<name>.wiz`). This is how a multi-file Wiz package
   imports its own helper files.
3. **Local project module** — `./<name>.wiz` next to the running program.
4. **Legacy flat module** — `~/.wiz/packages/<name>.wiz`.
5. **Installed package** — `~/.wiz/packages/<name>/`, loaded through its
   manifest: `main.wiz` for a Wiz package, `main.py` for a native one.
   A legacy directory without a manifest uses
   `~/.wiz/packages/<name>/<name>.wiz`.

```text
stdlib
<current module dir>/<name>.wiz   (inside a module)
<name>.wiz                        (local project module)
~/.wiz/packages/<name>.wiz
~/.wiz/packages/<name>/main.wiz   (or main.py for a native package)
```

---

## Writing a Wiz package

A Wiz package is a directory with a `wiz.pkg` manifest and a `main.wiz`
entry file:

```text
hello_wiz/
├── wiz.pkg
└── main.wiz
```

`main.wiz`:

```wiz
func hello(name = "Wiz") {
    return "Hello, " + name + "!"
}

let VERSION = "1.0.0"
```

`wiz.pkg`:

```json
{
    "name": "hello_wiz",
    "version": "1.0.0",
    "description": "Example Wiz package"
}
```

The whole package is imported under its name and its module-level
functions, variables and classes are accessed through the module:

```wiz
import hello_wiz

echo(hello_wiz.hello("Wiz"))      # -> Hello, Wiz!
echo(hello_wiz.VERSION)           # -> 1.0.0
```

Classes are imported the same way as functions: a class declared at the
top level of the entry file is available as `module.ClassName(...)`, and
functions in the module may instantiate the module's own classes by name:

```wiz
# main.wiz
class Greeter {
    let greeting = "Hi"
    func init(name) { self.name = name }
    func greet() { return self.greeting + ", " + self.name }
}

func make_greeter(name) { return Greeter(name) }
```

```wiz
import hello_wiz

let g = hello_wiz.make_greeter("Sam")   # -> Hi, Sam
echo(hello_wiz.Greeter("Zoe").greet())  # -> Hi, Zoe
```

Notes:

- `let VERSION` is **not required** — it is just a convention. Anything
  declared at the top level of `main.wiz` becomes part of the module.
- The entry file defaults to `main.wiz`. `import hello_wiz` maps the
  package name to `~/.wiz/packages/hello_wiz/main.wiz`.
- The entry file can be relocated with the manifest `entry` field. Use it
  to keep a clean source layout:

```text
widget/
├── wiz.pkg          { "name": "widget", ..., "entry": "lib/widget.wiz" }
└── lib/
    └── widget.wiz   <- loaded when you `import widget`
```
- You may keep a package's runtime state in module variables; the module
  is loaded only once per execution, and module functions keep access to
  their module scope no matter how they are called.

### Multi-file packages

A Wiz package may be split into several `.wiz` files. `main.wiz` is the
public entry point; other files are implementation details and are
imported *relative to the module*, not by package name:

```text
bundle/
├── wiz.pkg
├── main.wiz
└── util.wiz
```

`util.wiz`:

```wiz
func double(n) {
    return n * 2
}
```

`main.wiz`:

```wiz
import util

func quadruple(n) {
    return util.double(util.double(n))
}
```

Helper files are **private** to the package: a project can `import
bundle` but cannot `import util` from outside the package.

If a helper file declares classes that should be part of the package's
public API, re-export them from the entry file with a `let` alias:

```wiz
# main.wiz
import util

let double = util.double          # re-export a function
```

Classes and functions re-exported this way are callable through the
package module like any other member.

---

## Writing a native package

A native package is a directory with a `wiz.pkg` manifest of type
`native` and a `main.py` entry file:

```text
hello_native/
├── wiz.pkg
└── main.py
```

The entry file defaults to `main.py`, but you can put it anywhere with
the manifest `entry` field — this lets a native package keep a clean
`src/` layout and import its own submodules:

```text
mybot/
├── wiz.pkg          { "name": "mybot", ..., "type": "native", "entry": "src/bot.py" }
└── src/
    ├── bot.py       <- loaded when you `import mybot`
    └── core.py      <- imported by bot.py
```

`wiz.pkg`:

```json
{
    "name": "hello_native",
    "version": "1.0.0",
    "type": "native",
    "description": "Example Python package for Wiz"
}
```

The entry file **must** define a top-level variable named `module`. That
object is what Wiz imports. It should expose at least a `functions`
dictionary mapping Wiz function names to Python callables:

```python
class HelloNativeModule:

    def __init__(self):
        self.functions = {
            "hello": self.hello,
            "greet": self.greet,
        }

    def hello(self, name="Wiz"):
        return f"Hello, {name}!"

    def greet(self, name, excited=False):
        return f"Hello, {name}!" + ("!!" if excited else "")


module = HelloNativeModule()
```

If `main.py` does not define a `module` object, importing it fails.

### What the module object may expose

The `module` object is a plain Python object that Wiz reads attributes
from:

| Attribute | Purpose |
| --------- | ------- |
| `functions` | Dict of name -> callable. Exposed as callable module members. |
| `values` | Dict of name -> value. Exposed as module variables. |
| `classes` | Dict of name -> class. Exposed as module classes. |
| `interpreter` | Set automatically by Wiz to the running interpreter, so a package can call back into Wiz. |

At minimum `functions` is expected; `values` and `classes` are optional.

Classes exposed via `classes` are used like Wiz classes: calling
`module.ClassName(args)` builds the Python instance with `args` passed
to its constructor, and the instance's Python methods are callable from
Wiz:

```python
# render.py — a native package
class Widget:
    def __init__(self, name):
        self.name = name

    def describe(self):
        return f"widget {self.name}"

module = type("m", (), {"classes": {"Widget": Widget}})()
```

```wiz
import render

let w = render.Widget("submit")   # -> Widget.__init__("submit")
echo(w.describe())                # -> widget submit
```

### Calling conventions

- Python functions receive Wiz arguments positionally and by keyword:
  named Wiz arguments map to Python keyword arguments.
- Missing arguments fall back to the Python default values; required
  parameters that are not supplied raise an error.
- Return values (strings, numbers, lists, dicts, Wiz instances, `None`,
  and `WizFunction` wrappers) are passed back to Wiz unchanged.
- A `WizFunction` can be stored by a package and invoked later, which is
  how a native framework can register callbacks written in Wiz.

### Python dependencies

If a native package needs third-party Python modules, declare them in
`python_dependencies`. Wiz checks that they are importable before loading
the package and fails with a clear message otherwise:

```json
{
    "name": "my_bot",
    "version": "1.0.0",
    "type": "native",
    "python_dependencies": {
        "requests": ">=2.0"
    }
}
```

(The version strings are informational; the actual check is only that
the module can be imported. Install them with `pip`.)

---

## Dependencies between packages

A package can depend on other packages. Dependencies may be GitHub specs
or local relative paths. They are installed recursively, into the same
global store (`~/.wiz/packages/`):

```json
{
    "name": "calculator",
    "version": "1.0.0",
    "dependencies": {
        "mathutil": "owner/mathutil",
        "logger": "./packages/logger"
    }
}
```

Inside a package's code, its dependencies are imported by their own names:

```wiz
import mathutil

func twice(n) {
    return mathutil.times2(n)
}
```

---

## Version compatibility

A package can require a minimum interpreter version. Wiz checks the
constraint before running any package code and refuses to load it when
incompatible:

```json
{
    "name": "modern",
    "version": "1.0.0",
    "wiz_version": ">=0.22.0"
}
```

Supported operators: `==`, `!=`, `>`, `<`, `>=`, `<=`, or a bare version
number meaning "exactly this version".


# Self-Update

Wiz can update itself by checking the latest release on GitHub.

Check for a newer release without installing:

```bash
python3 wiz/main.py update-self --check
```

Download and apply the latest release:

```bash
python3 wiz/main.py update-self
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

The `lint` command statically analyzes a `.wiz` file without running it:

```bash
python3 wiz/main.py lint examples/hello.wiz
```

When the file is clean it prints:

```text
  examples/hello.wiz: no issues found
```

Otherwise it lists every problem found:

```text
  examples/bad.wiz:13:1  W005  Cannot assign to immutable variable 'count'
  examples/bad.wiz:15:1  W008  'break' used outside of a loop
```

## Checks

| Code  | Severity | Description                                     |
| ----- | -------- | ----------------------------------------------- |
| E001  | error    | Syntax or lexical error                         |
| S001  | style    | Trailing whitespace                             |
| S002  | style    | Missing newline at end of file                  |
| W001  | warning  | Duplicate function in the same scope            |
| W002  | warning  | Variable already declared in the same scope     |
| W003  | warning  | Function defined but never used                 |
| W004  | warning  | Variable declared but never used                |
| W005  | warning  | Assignment to an immutable (`let`) variable     |
| W008  | warning  | `break` / `continue` outside a loop             |
| W009  | warning  | `return` outside a function                     |
| W010  | warning  | Unreachable code after return / break / continue |
| W011  | warning  | Call to an undefined function                   |
| W012  | warning  | Use of an undefined decorator                   |

---

# Standard Library

Wiz ships with a rich standard library. Every module is imported with
`import` and exposes callable functions through `.`:

```wiz
import files

files.write("out.txt", "Hello")
```

Some modules depend on optional third-party Python packages
(`beautifulsoup4`, `numpy`, `Pillow`, `pyyaml`, `pygobject`, `requests`,
`pyperclip`). Importing the module always works; calling a function that
needs a missing dependency raises a clear error telling you what to
install.

## Overview

| Module       | Description                                        |
| ------------ | -------------------------------------------------- |
| archive      | Create and inspect zip / tar archives              |
| bars         | Progress bars, spinners and block widgets          |
| clipboard    | System clipboard get / set / clear                 |
| colors       | ANSI color and text styling helpers                |
| console      | Terminal clear, size and title                     |
| crypto       | Hashing (md5/sha*), uuid, base64 and hex helpers   |
| database     | SQLite connections and queries                     |
| date         | Dates and times                                    |
| files        | Read, write, append, delete and inspect files      |
| gtk          | GTK3 GUI widgets and events                        |
| html         | HTML parsing with BeautifulSoup                    |
| http         | GET / POST requests                                |
| image        | Image loading and editing with Pillow              |
| json         | Encode and decode JSON                             |
| math         | Math functions and constants                       |
| matrix       | Matrices and linear algebra with numpy             |
| os           | OS, filesystem and environment helpers             |
| process      | Run and control subprocesses                       |
| random       | Random integers and choices                        |
| re           | Regular expressions                                |
| socket       | TCP sockets                                        |
| sys          | Interpreter / system information                   |
| table        | Render tables (plain, markdown, csv)               |
| text         | String manipulation and case conversion            |
| thread       | Run functions in threads                           |
| time         | Sleep, timestamps and time formatting              |
| tk           | Tkinter GUI widgets and dialogs                    |
| yaml         | Parse and dump YAML                                |

## archive

```wiz
import archive

archive.zip("docs", "backup.zip")
let names = archive.list("backup.zip")
let info = archive.inspect("backup.zip")
```

Functions: `zip`, `unzip`, `tar`, `untar`, `list`, `inspect`

## bars

```wiz
import bars

echo(bars.progress(70, 100))
echo(bars.track(3, 10))
echo(bars.spinner(index=2))
```

Functions: `bar`, `progress`, `track`, `spinner`, `blocks`

## clipboard

```wiz
import clipboard

clipboard.set("hello")
echo(clipboard.get())
```

Functions: `get`, `set`, `clear` (requires `pyperclip`)

## colors

```wiz
import colors

echo(colors.red("danger"))
echo(colors.paint("hello", "blue", bg="white"))
echo(colors.strip(colors.green("plain text")))
```

Functions: `black`, `red`, `green`, `yellow`, `blue`, `magenta`,
`cyan`, `white`, `gray`, `bold`, `dim`, `italic`, `underline`, `blink`,
`reverse`, `paint`, `strip`, `rainbow`, `palette`

## console

```wiz
import console

console.clear()
echo(console.size())
console.title("Wiz app")
```

Functions: `clear`, `size`, `title`

## crypto

```wiz
import crypto

echo(crypto.md5("hello"))
echo(crypto.sha256("hello"))
echo(crypto.uuid())
echo(crypto.base64_encode("hello"))
echo(crypto.hex_encode("hello"))
```

Functions: `md5`, `sha1`, `sha224`, `sha256`, `sha384`, `sha512`,
`uuid`, `random_bytes`, `base64_encode`, `base64_decode`,
`hex_encode`, `hex_decode`

## database

```wiz
import database

let db = database.open("app.db")
database.execute(db, "CREATE TABLE IF NOT EXISTS users (name TEXT)")
database.execute(db, "INSERT INTO users VALUES ('Aydin')")
database.commit(db)
echo(database.query(db, "SELECT * FROM users"))
database.close(db)
```

Functions: `open`, `close`, `execute`, `query`, `commit`

## date

```wiz
import date

echo(date.now())
echo(date.format("%Y-%m-%d"))
echo(date.weekday_name(2024, 1, 1))
echo(date.is_leap(2024))
echo(date.add_days(2024, 1, 1, 10))
```

Functions: `today`, `now`, `iso`, `unix`, `from_unix`, `format`,
`parse`, `weekday`, `weekday_name`, `month_name`, `is_leap`,
`days_in_month`, `add_days`, `add_seconds`, `diff`, `component`, `age`

## files

```wiz
import files

let content = files.read("test.txt")

echo(content)

files.write("out.txt", "Hello")

files.append("out.txt", " World")

files.exists("out.txt")
```

Functions: `read`, `write`, `append`, `exists`, `delete`, `mkdir`,
`list`, `rename`

## gtk

```wiz
import gtk

let win = gtk.window("App", size=(400, 300))
let label = gtk.label(win, "Hello")
gtk.show_all(win)
gtk.mainloop()
```

Functions: `window`, `title`, `size`, `show`, `show_all`, `mainloop`,
`run`, `quit`, `destroy`, `timeout`, `box`, `frame`, `notebook`,
`add`, `pack_start`, `pack_end`, `grid`, `label`, `button`, `entry`,
`textarea`, `checkbox`, `radio`, `slider`, `combo`, `image`,
`progressbar`, `spinner`, `value`, `set`, `set_text`, `clear`,
`sensitive`, `show_widget`, `hide_widget`, `append`, `selected`,
`connect`, `on_click` (requires `pygobject`)

## html

```wiz
import html

let doc = "<h1>Hi</h1><p>World</p>"
echo(html.title(doc))
echo(html.find_all(doc, "p"))
```

Functions: `title`, `text`, `find`, `find_all`, `select`, `get`,
`tag`, `children`, `parent`, `attrs`, `pretty`, `extract`, `parse`
(requires `beautifulsoup4`)

## http

```wiz
import http

let page = http.get("https://example.com")
```

Functions: `get`, `post` (requires `requests`)

## image

```wiz
import image

let img = image.create(200, 100, "red")
image.save(img, "out.png")
let small = image.resize(img, 100, 50)
```

Functions: `open`, `create`, `save`, `resize`, `thumbnail`, `crop`,
`rotate`, `flip`, `grayscale`, `invert`, `blur`, `size`, `width`,
`height`, `mode`, `format`, `pixel`, `paste`, `copy`, `to_list`
(requires `Pillow`)

## json

```wiz
import json

let text = json.encode({
    "name": "Aydin"
})

echo(json.decode(text))
```

Functions: `encode`, `decode`, `stringify`, `parse`, `dump`, `load`

## math

```wiz
import math

echo(math.sqrt(16))
echo(math.pi)
echo(math.max([3, 9, 4]))
```

Functions: `abs`, `ceil`, `floor`, `round`, `sqrt`, `pow`, `exp`,
`log`, `log10`, `sin`, `cos`, `tan`, `asin`, `acos`, `atan`, `atan2`,
`degrees`, `radians`, `hypot`, `gcd`, `lcm`, `factorial`, `comb`,
`perm`, `sum`, `min`, `max`, `clamp`, `avg`, `rand`, `randint`

Constants: `pi`, `e`, `tau`, `inf`, `nan`

## matrix

```wiz
import matrix

let m = matrix.create([[1, 2], [3, 4]])
echo(matrix.determinant(m))
echo(matrix.flatten(m))
```

Functions: `create`, `zeros`, `ones`, `eye`, `identity`, `diag`,
`random`, `arange`, `linspace`, `shape`, `dim`, `size`, `transpose`,
`add`, `subtract`, `multiply`, `multiply_wise`, `divide`, `dot`,
`determinant`, `inverse`, `trace`, `min`, `max`, `mean`, `sum`,
`reshape`, `flatten`, `to_list`, `row`, `column`
(requires `numpy`)

## os

```wiz
import os

echo(os.name())
echo(os.cwd())
echo(os.exists("test.txt"))
echo(os.join("foo", "bar"))
```

Functions: `name`, `platform`, `arch`, `user`, `home`, `cwd`,
`chdir`, `env`, `getenv`, `setenv`, `unsetenv`, `listdir`, `abspath`,
`basename`, `dirname`, `join`, `split`, `exists`, `isfile`, `isdir`,
`sep`, `linesep`, `remove`, `mkdir`, `rmdir`, `rename`, `walk`

## process

```wiz
import process

let result = process.run("echo hi")
echo(result["stdout"])
```

Functions: `run`, `call`, `open`, `kill`, `wait`, `pid`, `alive`,
`stdin`, `stdout`, `stderr`

## random

```wiz
import random

echo(random.randint(1,10))
echo(random.choice(["a", "b", "c"]))
```

Functions: `randint`, `choice`

## re

```wiz
import re

echo(re.test("h.llo", "hello"))
echo(re.findall("\\d+", "a1b22"))
echo(re.replace("\\s+", "hello world", "-"))
```

Functions: `match`, `search`, `find`, `findall`, `split`, `replace`,
`test`, `escape`, `groups`

## socket

```wiz
import socket

let sock = socket.tcp()
socket.connect(sock, "example.com", 80)
socket.send(sock, "GET / HTTP/1.0\r\n\r\n")
echo(socket.recv(sock))
socket.close(sock)
```

Functions: `tcp`, `bind`, `listen`, `accept`, `connect`, `send`,
`recv`, `close`

## sys

```wiz
import sys

echo(sys.platform())
echo(sys.args())
```

Functions: `args`, `exit`, `platform`, `python`, `pid`, `version`,
`executable`, `stdout`, `stderr`, `stdin`, `path`, `modules`, `gc`

## table

```wiz
import table

echo(table.render([[1, 2], [3, 4]], headers=["a", "b"]))
echo(table.markdown([["x", "y"]]))
echo(table.csv([["1", "2"]]))
```

Functions: `render`, `print`, `md`, `markdown`, `csv`

## text

```wiz
import text

echo(text.upper("hello"))
echo(text.snake_case("HelloWorld"))
echo(text.camel_case("make it camel"))
echo(text.words("a quick brown fox"))
```

Functions: `upper`, `lower`, `title`, `cap`, `casefold`, `swapcase`,
`trim`, `ltrim`, `rtrim`, `strip`, `split`, `lines`, `words`, `chars`,
`join`, `replace`, `count`, `index`, `contains`, `starts_with`,
`ends_with`, `slice`, `reverse`, `repeat`, `pad`, `lpad`, `rpad`,
`length`, `is_alpha`, `is_digit`, `is_space`, `is_upper`, `is_lower`,
`title_case`, `snake_case`, `camel_case`, `kebab_case`, `wrap`,
`truncate`, `tabulate`

## thread

```wiz
import thread

func task()
{
    echo("working")
}

let t = thread.start(task)
thread.join(t)
```

Functions: `start`, `sleep`, `join`, `alive`

## time

```wiz
import time

time.sleep(1)
echo(time.timestamp())
echo(time.format("%H:%M"))
```

Functions: `now`, `sleep`, `sleep_ms`, `timestamp`, `format`, `year`,
`month`, `day`, `hour`, `minute`, `second`

## tk

```wiz
import tk

let win = tk.window("App", size=(400, 300))
tk.pack(tk.label(win, "Hello"))
tk.mainloop(win)
```

Functions: `window`, `app`, `title`, `size`, `resizable`, `mainloop`,
`run`, `destroy`, `after`, `exit`, `frame`, `label`, `button`,
`entry`, `textarea`, `checkbox`, `radio`, `slider`, `listbox`,
`combo`, `canvas`, `image`, `picture`, `progressbar`, `pack`, `grid`,
`place`, `draw_line`, `draw_rect`, `draw_oval`, `draw_text`,
`variable`, `value`, `set`, `get_text`, `set_text`, `clear`,
`config`, `disable`, `enable`, `focus`, `selected`, `bind`,
`on_click`, `alert`, `info`, `warn`, `error`, `confirm`, `ask_file`,
`ask_save`, `ask_dir`, `ask_color`, `ask_text`

## yaml

```wiz
import yaml

echo(yaml.dump({"name": "wiz"}))
let data = yaml.parse("name: wiz")
```

Functions: `parse`, `load`, `dump`, `stringify` (requires `pyyaml`)

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
├── decorators.py
├── errors.py
├── linter.py
├── package_manager.py
├── main.py
└── stdlib/
    ├── archive.py    ├── bars.py       ├── clipboard.py
    ├── colors.py     ├── console.py    ├── crypto.py
    ├── database.py   ├── date.py       ├── files.py
    ├── gtk.py        ├── html.py       ├── http.py
    ├── image.py      ├── json.py       ├── math.py
    ├── matrix.py     ├── os.py         ├── process.py
    ├── random.py     ├── re.py         ├── socket.py
    ├── sys.py        ├── table.py      ├── text.py
    ├── thread.py     ├── time.py       ├── tk.py
    ├── yaml.py
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
* Standard library (28 modules: `files`, `http`, `json`, `random`, `text`, `math`, `os`, `date`, `re`, `crypto`, `table`, `bars`, `colors`, `archive`, `yaml`, `image`, `matrix`, `process`, `socket`, `sys`, `thread`, `time`, `database`, `console`, `clipboard`, `gtk`, `tk`, `html`)
* Package manager (install, update, uninstall, list, info)
* Wiz and native (Python) packages with multi-file support
* Static linter
* Comments (`//`)
* AST printer
* Token printer
* CLI interface

---

# Planned Features

Future versions may include:

* Floating-point numbers
* Enums
* Match expressions
* Lambdas
* Bytecode compiler
* Native executable compilation
* Better error diagnostics
* VS Code Language Server
