import os
import sys


RESET = "\033[0m"
BOLD = "\033[1m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
GRAY = "\033[90m"


def use_color():
    return (
        os.environ.get("WIZ_NO_COLOR") is None
        and hasattr(sys.stdout, "isatty")
        and sys.stdout.isatty()
    )


def style(text, codes):
    if not use_color() or not codes:
        return text
    return codes + text + RESET


BANNER_WIDTH = 52


def _banner(label):
    inner_width = BANNER_WIDTH - 2
    padded = label.upper().center(inner_width)
    border = "═" * inner_width

    red = RED + BOLD

    return "\n".join(
        [
            style("╔" + border + "╗", red),
            style("║" + padded + "║", red),
            style("╚" + border + "╝", red),
        ]
    )


def _code_snippet(error):
    if error.line is None or error.source is None:
        return None

    lines = error.source.splitlines()

    if error.line < 1 or error.line > len(lines):
        return None

    error_line = lines[error.line - 1]

    error_column = max(1, error.column or 1)
    error_column = min(error_column, len(error_line) + 1)

    start = max(1, error.line - 2)
    end = min(len(lines), error.line + 1)

    line_width = len(str(end))

    rows = []

    for number in range(start, end + 1):
        text = lines[number - 1].expandtabs(8)
        gutter = str(number).rjust(line_width)
        marker = ">" if number == error.line else " "
        rows.append(f"{gutter} {marker} │ {text}")

    before = error_line[: error_column - 1].expandtabs(8)
    caret_column = len(before) + 1

    rows.append(
        f"{' ' * line_width}   │ {' ' * (caret_column - 1)}^"
    )

    return "\n".join(rows)


def render_error(error):
    label = getattr(error, "label", "Wiz Error")

    parts = [_banner(label)]

    location = f"Line {error.line}, Column {error.column}"

    if getattr(error, "filename", None):
        location = f"{error.filename}:{error.line}:{error.column}"

    parts.append("")
    parts.append(style("  Location", BOLD) + f" : {location}")
    parts.append(style("  Message ", BOLD) + f" : {error.message}")

    snippet = _code_snippet(error)

    if snippet is not None:
        parts.append("")
        parts.append(snippet)

    parts.append("")

    return "\n".join(parts)


class WizError(Exception):

    label = "Wiz Error"

    def __init__(self, message, line=None, column=None):
        super().__init__(message)
        self.message = message
        self.line = line
        self.column = column
        self.source = None
        self.filename = None

    def attach_source(self, source):
        self.source = source
        return self

    def __str__(self):
        return render_error(self)


class WizSyntaxError(WizError):
    label = "Syntax Error"


class WizRuntimeError(WizError):
    label = "Runtime Error"


class WizTypeError(WizError):
    label = "Type Error"


class WizNameError(WizError):
    label = "Name Error"


class WizMemberError(WizError):
    label = "Member Error"


class WizIndexError(WizError):
    label = "Index Error"


class WizKeyError(WizError):
    label = "Key Error"


class WizVariableNotImmutable(WizError):
    label = "Immutable Error"


class WizVariableDeclared(WizError):
    label = "Declaration Error"


class WizParameterError(WizError):
    label = "Parameter Error"
