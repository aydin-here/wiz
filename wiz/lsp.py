import os

from lsprotocol.types import (
    CompletionItem,
    CompletionItemKind,
    CompletionList,
    Diagnostic,
    DiagnosticSeverity,
    DocumentSymbol,
    Hover,
    Location,
    MarkupContent,
    MarkupKind,
    Position,
    PublishDiagnosticsParams,
    Range,
    SymbolKind,
    TextEdit,
)

from pygls.lsp.server import LanguageServer

from errors import WizError
from formatter import Formatter
from lexer import Lexer
from linter import Linter
from nodes import *
from parser import Parser


KEYWORDS = [
    "let", "var", "func", "when", "else", "switch", "case", "default",
    "return", "while", "for", "in", "step", "break", "continue",
    "class", "extends", "import", "decorator", "before", "after",
    "error", "try", "catch", "finally", "throw", "null", "and", "or",
    "not", "true", "false",
]

BUILTINS = {
    "echo": "Print a value to the console",
    "get": "Read a value from an input source",
    "len": "Return the length of a string, list or dictionary",
    "str": "Convert a value to a string",
    "num": "Convert a value to a number",
    "bool": "Convert a value to a boolean",
}

SEVERITY_MAP = {
    "error": DiagnosticSeverity.Error,
    "warning": DiagnosticSeverity.Warning,
    "style": DiagnosticSeverity.Hint,
}

MODULE_DIR = os.path.dirname(os.path.abspath(__file__))

SYMBOL_KIND = {
    "function": SymbolKind.Function,
    "class": SymbolKind.Class,
    "let": SymbolKind.Variable,
    "var": SymbolKind.Variable,
    "import": SymbolKind.Module,
}

COMPLETION_KIND = {
    "function": CompletionItemKind.Function,
    "class": CompletionItemKind.Class,
    "let": CompletionItemKind.Variable,
    "var": CompletionItemKind.Variable,
    "import": CompletionItemKind.Module,
}


def module_names():
    stdlib = os.path.join(MODULE_DIR, "stdlib")
    names = set()

    if os.path.isdir(stdlib):
        for entry in os.listdir(stdlib):
            if entry.endswith(".py") and entry != "__init__.py":
                names.add(entry[:-3])

    packages = os.path.join(
        os.environ.get("WIZ_HOME", os.path.expanduser("~/.wiz")),
        "packages",
    )

    if os.path.isdir(packages):
        for entry in os.listdir(packages):
            names.add(entry)

    return sorted(names)


MODULES = module_names()


def _position(line, column):
    return Position(line=line - 1, character=column - 1)


def _range(line, column):
    start = _position(line, column)
    return Range(start=start, end=Position(line=start.line, character=start.character + 1))


class _Symbol:

    def __init__(self, name, kind, line, column, parent=None, **extra):
        self.name = name
        self.kind = kind
        self.line = line
        self.column = column
        self.parent = parent
        self.extra = extra

    def signature(self):
        kind = self.kind

        if kind == "function":
            params = ", ".join(p.name for p in self.extra.get("params", []))
            return f"func {self.name}({params})"

        if kind == "class":
            name = self.extra.get("extends")
            suffix = f" extends {name}" if name else ""
            return f"class {self.name}{suffix}"

        if kind == "import":
            return f"import {self.name}"

        return self.name

    def is_top_level(self):
        return self.parent is None


class WizAnalyzer:
    """Parses Wiz source and indexes definitions for navigation features."""

    def __init__(self, source):
        self.source = source
        self.top = []
        self.by_name = {}

        try:
            tokens = Lexer(source).tokenize()
            self.tree = Parser(tokens).parse()
        except WizError:
            self.tree = None
            return

        self._walk(self.tree.body)

    # ------------------------------------------------------------------
    # Walking
    # ------------------------------------------------------------------

    def _children(self, node):
        for value in vars(node).values():
            if isinstance(value, Node):
                yield value
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, Node):
                        yield item

    def _register(self, symbol):
        if symbol.parent is None:
            self.top.append(symbol)

        self.by_name.setdefault(symbol.name, symbol)

        return symbol

    def _walk(self, nodes, parent=None):

        if nodes is None:
            return

        if isinstance(nodes, Node):
            nodes = nodes.statements if isinstance(nodes, Block) else [nodes]

        for node in nodes:

            if isinstance(node, (LetStatement, VarStatement, ImportStatement)):
                self._register(_Symbol(
                    node.module if isinstance(node, ImportStatement) else node.name,
                    "let" if isinstance(node, LetStatement) else
                    "var" if isinstance(node, VarStatement) else "import",
                    node.line,
                    node.column,
                    parent=parent,
                ))

            elif isinstance(node, FunctionStatement):
                params = [
                    _Symbol(p, "param", node.line, node.column)
                    for p in node.params
                ]

                symbol = self._register(_Symbol(
                    node.name, "function", node.line, node.column,
                    parent=parent,
                    params=params,
                ))

                for child in node.decorators:
                    self._walk([child], parent=symbol)

                self._walk(node.body, parent=symbol)

            elif isinstance(node, FunctionExpression):
                self._walk(node.body, parent=parent)

            elif isinstance(node, ClassStatement):
                symbol = self._register(_Symbol(
                    node.name, "class", node.line, node.column,
                    parent=parent,
                    extends=node.extends,
                ))

                for member in self._class_members(node.body):
                    member_symbol = _Symbol(
                        member.name,
                        "function" if isinstance(member, FunctionStatement) else
                        "let" if isinstance(member, LetStatement) else "var",
                        member.line,
                        member.column,
                        parent=symbol,
                    )

                    if isinstance(member, FunctionStatement):
                        member_symbol.extra["params"] = [
                            _Symbol(p, "param", member.line, member.column)
                            for p in member.params
                        ]

                    symbol.extra.setdefault("members", []).append(member_symbol)
                    self.by_name.setdefault(member.name, member_symbol)

                self._walk(node.body, parent=symbol)

            elif isinstance(node, DecoratorStatement):
                for block in (node.define, node.before, node.after, node.error):
                    self._walk(block, parent=parent)

            elif isinstance(node, Block):
                self._walk(node.body, parent=parent)

            elif isinstance(node, ForStatement):
                self._walk(node.iterable, parent=parent)
                self._walk(node.start, parent=parent)
                self._walk(node.end, parent=parent)
                self._walk(node.step, parent=parent)
                self._walk(node.body, parent=parent)

            else:
                for child in self._children(node):
                    self._walk(child, parent=parent)

    @staticmethod
    def _class_members(body):
        members = []

        if body is None:
            return members

        statements = body.statements if isinstance(body, Block) else [body]

        for statement in statements:

            if isinstance(statement, (FunctionStatement, LetStatement, VarStatement)):
                members.append(statement)

        return members

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def word_at(self, line, character):
        lines = self.source.splitlines()

        if line < 0 or line >= len(lines):
            return None

        text = lines[line]

        if character > len(text):
            character = len(text)

        start = character
        end = character

        while start > 0 and (text[start - 1].isalnum() or text[start - 1] == "_"):
            start -= 1

        while end < len(text) and (text[end].isalnum() or text[end] == "_"):
            end += 1

        word = text[start:end]

        if not word:
            return None

        return {
            "word": word,
            "line": line + 1,
            "column": start + 1,
            "range": Range(
                start=Position(line=line, character=start),
                end=Position(line=line, character=end),
            ),
        }

    def definition(self, name):
        return self.by_name.get(name)


class WizLanguageServer(LanguageServer):

    def __init__(self):
        super().__init__("wiz-language-server", "0.4.0")
        self._analysis = {}

    def _analyze(self, uri, source):
        self._analysis[uri] = WizAnalyzer(source)
        return self._analysis[uri]

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def _diagnostics(self, source):
        issues = Linter(source).run()

        if not issues:
            return []

        diagnostics = []

        for issue in issues:
            diagnostics.append(Diagnostic(
                range=_range(issue["line"], issue["column"]),
                message=issue["message"],
                severity=SEVERITY_MAP.get(
                    issue["severity"], DiagnosticSeverity.Information
                ),
                code=issue["code"],
                source="wiz",
            ))

        return diagnostics

    def _publish(self, doc):
        self.protocol.notify(
            "textDocument/publishDiagnostics",
            PublishDiagnosticsParams(
                uri=doc.uri,
                diagnostics=self._diagnostics(doc.source),
            ),
        )

    def _update(self, params):
        doc = self.workspace.get_text_document(params.text_document.uri)
        self._analyze(doc.uri, doc.source)
        self._publish(doc)

    # ------------------------------------------------------------------
    # Features
    # ------------------------------------------------------------------

    def feature_formatting(self, params):
        doc = self.workspace.get_text_document(params.text_document.uri)

        try:
            formatted = Formatter(doc.source).format()
        except WizError:
            return None

        if formatted is None or formatted == doc.source:
            return None

        lines = doc.source.splitlines()

        return [TextEdit(
            range=Range(
                start=Position(line=0, character=0),
                end=Position(line=max(len(lines) - 1, 0), character=10**9),
            ),
            new_text=formatted,
        )]

    def feature_definition(self, params):
        doc = self.workspace.get_text_document(params.text_document.uri)
        analyzer = self._analyze(doc.uri, doc.source)

        word = analyzer.word_at(
            params.position.line, params.position.character
        )

        if word is None:
            return None

        symbol = analyzer.definition(word["word"])

        if symbol is None:
            return None

        return Location(
            uri=doc.uri,
            range=_range(symbol.line, symbol.column),
        )

    def feature_completion(self, params):
        doc = self.workspace.get_text_document(params.text_document.uri)
        analyzer = self._analyze(doc.uri, doc.source)

        word = analyzer.word_at(
            params.position.line, params.position.character
        )

        prefix = (word or {}).get("word", "").lower()

        items = []

        for keyword in KEYWORDS:
            if keyword.startswith(prefix):
                items.append(CompletionItem(
                    label=keyword,
                    kind=CompletionItemKind.Keyword,
                    detail="keyword",
                ))

        for name, help_text in BUILTINS.items():
            if name.startswith(prefix):
                items.append(CompletionItem(
                    label=name,
                    kind=CompletionItemKind.Function,
                    detail=help_text,
                ))

        for symbol in analyzer.top:
            if symbol.name.startswith(prefix):
                items.append(CompletionItem(
                    label=symbol.name,
                    kind=COMPLETION_KIND.get(
                        symbol.kind, CompletionItemKind.Variable
                    ),
                    detail=symbol.kind,
                ))

        for module in MODULES:
            if module.startswith(prefix):
                items.append(CompletionItem(
                    label=module,
                    kind=CompletionItemKind.Module,
                    detail="module",
                ))

        seen = set()
        unique = []

        for item in items:

            if item.label in seen:
                continue

            seen.add(item.label)
            unique.append(item)

        return CompletionList(is_incomplete=False, items=unique)

    def feature_symbols(self, params):
        doc = self.workspace.get_text_document(params.text_document.uri)
        analyzer = self._analyze(doc.uri, doc.source)

        result = []

        for symbol in analyzer.top:

            if symbol.kind == "class":
                children = []

                for member in symbol.extra.get("members", []):
                    if member.kind == "param":
                        continue

                    children.append(DocumentSymbol(
                        name=member.name,
                        detail=member.signature() if member.kind == "function" else None,
                        kind=SYMBOL_KIND[member.kind],
                        range=_range(member.line, member.column),
                        selection_range=_range(member.line, member.column),
                        children=[],
                    ))

                result.append(DocumentSymbol(
                    name=symbol.name,
                    detail=symbol.signature(),
                    kind=SymbolKind.Class,
                    range=_range(symbol.line, symbol.column),
                    selection_range=_range(symbol.line, symbol.column),
                    children=children,
                ))

            elif symbol.kind == "import":
                result.append(DocumentSymbol(
                    name=f"import {symbol.name}",
                    detail=None,
                    kind=SymbolKind.Module,
                    range=_range(symbol.line, symbol.column),
                    selection_range=_range(symbol.line, symbol.column),
                    children=[],
                ))

            else:
                result.append(DocumentSymbol(
                    name=symbol.name,
                    detail=symbol.signature() if symbol.kind == "function" else None,
                    kind=SYMBOL_KIND.get(symbol.kind, SymbolKind.Variable),
                    range=_range(symbol.line, symbol.column),
                    selection_range=_range(symbol.line, symbol.column),
                    children=[],
                ))

        return result

    def feature_hover(self, params):
        doc = self.workspace.get_text_document(params.text_document.uri)
        analyzer = self._analyze(doc.uri, doc.source)

        word = analyzer.word_at(
            params.position.line, params.position.character
        )

        if word is None:
            return None

        symbol = analyzer.definition(word["word"])

        if symbol is not None:
            return Hover(
                contents=MarkupContent(
                    kind=MarkupKind.Markdown,
                    value=f"```wiz\n{symbol.signature()}\n```",
                )
            )

        if word["word"] in BUILTINS:
            return Hover(
                contents=MarkupContent(
                    kind=MarkupKind.Markdown,
                    value=(
                        f"```wiz\n{word['word']}()\n```\n\n"
                        f"{BUILTINS[word['word']]}"
                    ),
                )
            )

        return None


SERVER = WizLanguageServer()


@SERVER.feature("textDocument/didOpen")
def did_open(ls, params):
    ls._update(params)


@SERVER.feature("textDocument/didChange")
def did_change(ls, params):
    ls._update(params)


@SERVER.feature("textDocument/didSave")
def did_save(ls, params):
    ls._update(params)


@SERVER.feature("textDocument/formatting")
def formatting(ls, params):
    return ls.feature_formatting(params)


@SERVER.feature("textDocument/definition")
def definition(ls, params):
    return ls.feature_definition(params)


@SERVER.feature("textDocument/completion")
def completion(ls, params):
    return ls.feature_completion(params)


@SERVER.feature("textDocument/documentSymbol")
def document_symbols(ls, params):
    return ls.feature_symbols(params)


@SERVER.feature("textDocument/hover")
def hover(ls, params):
    return ls.feature_hover(params)


def main():
    SERVER.start_io()


if __name__ == "__main__":
    main()