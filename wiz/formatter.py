from lexer import Lexer
from tokens import TokenType


_TOKEN_TEXT = {
    TokenType.LET: "let",
    TokenType.VAR: "var",
    TokenType.FUNC: "func",
    TokenType.WHEN: "when",
    TokenType.ELSE: "else",
    TokenType.SWITCH: "switch",
    TokenType.CASE: "case",
    TokenType.DEFAULT: "default",
    TokenType.RETURN: "return",
    TokenType.WHILE: "while",
    TokenType.FOR: "for",
    TokenType.IN: "in",
    TokenType.STEP: "step",
    TokenType.RANGE: "..",
    TokenType.BREAK: "break",
    TokenType.CONTINUE: "continue",
    TokenType.CLASS: "class",
    TokenType.EXTENDS: "extends",
    TokenType.IMPORT: "import",
    TokenType.DECORATOR: "decorator",
    TokenType.TRY: "try",
    TokenType.CATCH: "catch",
    TokenType.FINALLY: "finally",
    TokenType.THROW: "throw",
    TokenType.NULL: "null",
    TokenType.ASSIGN: "=",
    TokenType.PLUS: "+",
    TokenType.MINUS: "-",
    TokenType.STAR: "*",
    TokenType.SLASH: "/",
    TokenType.MODULO: "%",
    TokenType.HASH: "#",
    TokenType.EQUAL: "==",
    TokenType.NOT_EQUAL: "!=",
    TokenType.ARROW: "=>",
    TokenType.NULL_COALESCE: "??",
    TokenType.SAFE_DOT: "?.",
    TokenType.QUESTION: "?",
    TokenType.GREATER: ">",
    TokenType.LESS: "<",
    TokenType.GREATER_EQUAL: ">=",
    TokenType.LESS_EQUAL: "<=",
    TokenType.AND: "and",
    TokenType.OR: "or",
    TokenType.NOT: "not",
    TokenType.LPAREN: "(",
    TokenType.RPAREN: ")",
    TokenType.LBRACE: "{",
    TokenType.RBRACE: "}",
    TokenType.LBRACKET: "[",
    TokenType.RBRACKET: "]",
    TokenType.COMMA: ",",
    TokenType.COLON: ":",
    TokenType.DOT: ".",
}

_VALUES = {
    TokenType.IDENTIFIER,
    TokenType.NUMBER,
    TokenType.STRING,
    TokenType.INTERPOLATED_STRING,
    TokenType.BOOLEAN,
    TokenType.NULL,
    TokenType.RPAREN,
    TokenType.RBRACKET,
    TokenType.RBRACE,
}

_NO_SPACE_AFTER = {
    TokenType.LPAREN,
    TokenType.LBRACKET,
    TokenType.DOT,
    TokenType.SAFE_DOT,
    TokenType.RANGE,
    TokenType.HASH,
}

_NO_SPACE_BEFORE = {
    TokenType.COMMA,
    TokenType.COLON,
    TokenType.DOT,
    TokenType.SAFE_DOT,
    TokenType.QUESTION,
    TokenType.RANGE,
    TokenType.RPAREN,
    TokenType.RBRACKET,
}

_BINARY_OPS = {
    TokenType.ASSIGN,
    TokenType.STAR,
    TokenType.SLASH,
    TokenType.MODULO,
    TokenType.EQUAL,
    TokenType.NOT_EQUAL,
    TokenType.GREATER,
    TokenType.LESS,
    TokenType.GREATER_EQUAL,
    TokenType.LESS_EQUAL,
    TokenType.AND,
    TokenType.OR,
    TokenType.ARROW,
    TokenType.NULL_COALESCE,
}


class Formatter:

    def __init__(self, source):
        self.source = source

    def format(self):
        trailing, full, skip = self._scan_comments()

        code_by_line = {}

        for token in Lexer(self.source).tokenize():

            if token.type in (TokenType.NEWLINE, TokenType.EOF):
                continue

            code_by_line.setdefault(token.line, []).append(token)

        out = []

        for index, raw in enumerate(self.source.splitlines(), start=1):

            tokens = code_by_line.get(index)

            if tokens:

                text = "".join(self._spaced(tokens))

                if index in trailing:
                    text = text.rstrip() + "  " + trailing[index]

                out.append({
                    "kind": "code",
                    "text": text,
                    "types": [token.type for token in tokens]
                })

            elif index in skip:
                continue

            elif index in full:
                out.append({"kind": "comment", "text": full[index]})

            else:
                stripped = raw.strip()

                if stripped:
                    out.append({"kind": "comment", "text": raw})
                else:
                    out.append({"kind": "blank"})

        out = self._clean(out)

        return self._render(out)

    # ------------------------------------------------------------------
    # Token spacing
    # ------------------------------------------------------------------

    def _token_text(self, token):

        token_type = token.type

        if token_type == TokenType.IDENTIFIER:
            return token.value

        if token_type == TokenType.NUMBER:
            return str(token.value)

        if token_type == TokenType.STRING:
            return '"' + token.value + '"'

        if token_type == TokenType.INTERPOLATED_STRING:
            return '$"' + token.value + '"'

        if token_type == TokenType.BOOLEAN:
            return "true" if token.value else "false"

        return _TOKEN_TEXT.get(token_type, token_type.name.lower())

    def _needs_space(self, previous, current, previous_was_unary):

        previous_type = previous.type
        current_type = current.type

        if previous_was_unary:
            return False

        if current_type in _NO_SPACE_BEFORE:
            return False

        if current_type == TokenType.LPAREN:
            return not (
                previous_type in _VALUES
                or previous_type == TokenType.FUNC
            )

        if current_type == TokenType.LBRACKET:
            return not (previous_type in _VALUES)

        if current_type == TokenType.LBRACE:
            return not (
                previous_type in (
                    TokenType.LPAREN,
                    TokenType.LBRACKET,
                    TokenType.DOT,
                    TokenType.SAFE_DOT,
                    TokenType.RANGE,
                    TokenType.HASH,
                )
            )

        if previous_type in _NO_SPACE_AFTER:
            return False

        if current_type in (TokenType.PLUS, TokenType.MINUS):
            return not (
                previous_type in (
                    TokenType.LPAREN,
                    TokenType.LBRACKET,
                    TokenType.DOT,
                    TokenType.SAFE_DOT,
                    TokenType.RANGE,
                    TokenType.HASH,
                )
            )

        if current_type in _BINARY_OPS:
            return True

        return True

    def _spaced(self, tokens):

        segments = []
        previous = None
        previous_was_unary = False

        for token in tokens:

            text = self._token_text(token)

            if previous is not None:
                if self._needs_space(previous, token, previous_was_unary):
                    segments.append(" " + text)
                else:
                    segments.append(text)
            else:
                segments.append(text)

            previous_was_unary = (
                token.type in (TokenType.PLUS, TokenType.MINUS)
                and not (
                    previous is not None
                    and previous.type in _VALUES
                )
            )

            previous = token

        return segments

    # ------------------------------------------------------------------
    # Comment detection
    # ------------------------------------------------------------------

    def _find_comment_start(self, line):

        in_string = False

        index = 0

        while index < len(line) - 1:

            char = line[index]

            if in_string:

                if char == '"':
                    in_string = False

                index += 1
                continue

            if char == '"':
                in_string = True
                index += 1
                continue

            if char == "/" and line[index + 1] in ("/", "*"):
                return index

            index += 1

        return None

    def _scan_comments(self):

        lines = self.source.splitlines()

        trailing = {}
        full = {}
        skip = set()

        index = 0
        count = len(lines)

        while index < count:

            line = lines[index]

            start = self._find_comment_start(line)

            if start is None:
                index += 1
                continue

            before = line[:start]

            if line[start:start + 2] == "//":

                if before.strip() == "":
                    full[index + 1] = line[start:]
                else:
                    trailing[index + 1] = line[start:]

                index += 1
                continue

            start_line = index + 1

            block = line[start:]
            end = line.find("*/", start + 2)

            while end == -1:

                index += 1

                if index >= count:
                    break

                skip.add(index + 1)
                block += "\n" + lines[index]
                end = lines[index].find("*/")

            if before.strip() == "":
                full[start_line] = block
            else:
                trailing[start_line] = block

            index += 1

        return trailing, full, skip

    # ------------------------------------------------------------------
    # Line cleanup and indentation
    # ------------------------------------------------------------------

    def _clean(self, out):

        collapsed = []

        for item in out:

            if item["kind"] == "blank":

                if collapsed and collapsed[-1]["kind"] != "blank":
                    collapsed.append(item)

            else:
                collapsed.append(item)

        while collapsed and collapsed[0]["kind"] == "blank":
            collapsed.pop(0)

        while collapsed and collapsed[-1]["kind"] == "blank":
            collapsed.pop()

        result = []

        for item in collapsed:

            if (
                item["kind"] == "blank"
                and result
                and result[-1]["kind"] == "code"
                and result[-1]["text"].rstrip().endswith("{")
            ):
                continue

            result.append(item)

        filtered = []

        for item in result:

            if (
                item["kind"] == "blank"
                and filtered
                and filtered[-1]["kind"] == "code"
                and filtered[-1]["text"].lstrip().startswith("}")
            ):
                continue

            filtered.append(item)

        return filtered

    def _render(self, out):

        lines = []
        indent = 0

        for item in out:

            if item["kind"] == "blank":
                lines.append("")
                continue

            if item["kind"] == "comment":

                first, _, rest = item["text"].partition("\n")

                lines.append("    " * indent + first)

                if rest:
                    lines.extend(rest.split("\n"))

                continue

            text = item["text"]
            types = item["types"]

            leading = 0

            for token_type in types:

                if token_type == TokenType.RBRACE:
                    leading += 1
                else:
                    break

            line_indent = max(0, indent - leading)

            opens = sum(
                1 for token_type in types
                if token_type == TokenType.LBRACE
            )

            closes = sum(
                1 for token_type in types
                if token_type == TokenType.RBRACE
            )

            lines.append("    " * line_indent + text)

            indent = max(0, indent + opens - closes)

        return "\n".join(lines) + ("\n" if lines else "")
