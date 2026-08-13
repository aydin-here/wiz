import re


class TextModule:

    def __init__(self):
        self.functions = {
            "upper": self.upper,
            "lower": self.lower,
            "title": self.title,
            "cap": self.cap,
            "casefold": self.casefold,
            "swapcase": self.swapcase,
            "trim": self.trim,
            "ltrim": self.ltrim,
            "rtrim": self.rtrim,
            "strip": self.trim,
            "split": self.split,
            "lines": self.lines,
            "words": self.words,
            "chars": self.chars,
            "join": self.join,
            "replace": self.replace,
            "count": self.count,
            "index": self.index,
            "contains": self.contains,
            "starts_with": self.starts_with,
            "ends_with": self.ends_with,
            "slice": self.slice,
            "reverse": self.reverse,
            "repeat": self.repeat,
            "pad": self.pad,
            "lpad": self.lpad,
            "rpad": self.rpad,
            "length": self.length,
            "is_alpha": self.is_alpha,
            "is_digit": self.is_digit,
            "is_space": self.is_space,
            "is_upper": self.is_upper,
            "is_lower": self.is_lower,
            "title_case": self.title,
            "snake_case": self.snake_case,
            "camel_case": self.camel_case,
            "kebab_case": self.kebab_case,
            "wrap": self.wrap,
            "truncate": self.truncate,
            "tabulate": self.tabulate,
        }

    def _string(self, value):
        return str(value)

    def upper(self, text):
        return self._string(text).upper()

    def lower(self, text):
        return self._string(text).lower()

    def title(self, text):
        return self._string(text).title()

    def cap(self, text):
        value = self._string(text)
        return value[:1].upper() + value[1:].lower()

    def casefold(self, text):
        return self._string(text).casefold()

    def swapcase(self, text):
        return self._string(text).swapcase()

    def trim(self, text, chars=None):
        return self._string(text).strip(chars)

    def ltrim(self, text, chars=None):
        return self._string(text).lstrip(chars)

    def rtrim(self, text, chars=None):
        return self._string(text).rstrip(chars)

    def split(self, text, separator=None, limit=None):
        value = self._string(text)
        if separator is None:
            return value.split()
        if limit is None:
            return value.split(separator)
        return value.split(separator, int(limit))

    def lines(self, text):
        return self._string(text).splitlines()

    def words(self, text):
        return re.findall(r"\w+", self._string(text))

    def chars(self, text):
        return list(self._string(text))

    def join(self, items, separator=""):
        return separator.join(str(item) for item in items)

    def replace(self, text, old, new, count=None):
        value = self._string(text)
        if count is None:
            return value.replace(old, new)
        return value.replace(old, new, int(count))

    def count(self, text, sub):
        return self._string(text).count(sub)

    def index(self, text, sub):
        try:
            return self._string(text).index(sub)
        except ValueError:
            return -1

    def contains(self, text, sub):
        return sub in self._string(text)

    def starts_with(self, text, prefix):
        return self._string(text).startswith(prefix)

    def ends_with(self, text, suffix):
        return self._string(text).endswith(suffix)

    def slice(self, text, start=0, end=None, step=1):
        value = self._string(text)
        if end is None:
            return value[int(start)::int(step)]
        return value[int(start):int(end):int(step)]

    def reverse(self, text):
        return self._string(text)[::-1]

    def repeat(self, text, times):
        return self._string(text) * int(times)

    def pad(self, text, width, fill=" "):
        return self._string(text).center(int(width), str(fill))

    def lpad(self, text, width, fill=" "):
        return self._string(text).rjust(int(width), str(fill))

    def rpad(self, text, width, fill=" "):
        return self._string(text).ljust(int(width), str(fill))

    def length(self, text):
        return len(self._string(text))

    def is_alpha(self, text):
        return self._string(text).isalpha()

    def is_digit(self, text):
        return self._string(text).isdigit()

    def is_space(self, text):
        return self._string(text).isspace()

    def is_upper(self, text):
        return self._string(text).isupper()

    def is_lower(self, text):
        return self._string(text).islower()

    def snake_case(self, text):
        value = re.sub(r"([A-Z])", r"_\1", self._string(text))
        value = re.sub(r"[-\s]+", "_", value)
        return value.strip("_").lower()

    def camel_case(self, text):
        words = re.findall(r"[A-Za-z0-9]+", self._string(text))
        return words[0].lower() + "".join(
            word[:1].upper() + word[1:].lower()
            for word in words[1:]
        )

    def kebab_case(self, text):
        return self.snake_case(text).replace("_", "-")

    def wrap(self, text, width=80):
        import textwrap
        return textwrap.wrap(self._string(text), int(width))

    def truncate(self, text, length, suffix="..."):
        value = self._string(text)
        if len(value) <= int(length):
            return value
        return value[: int(length) - len(suffix)] + suffix

    def tabulate(self, rows, separator="\t"):
        return "\n".join(
            separator.join(str(cell) for cell in row)
            for row in rows
        )
