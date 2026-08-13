import re


class ReModule:

    def __init__(self):
        self.functions = {
            "match": self.match,
            "search": self.search,
            "find": self.find,
            "findall": self.findall,
            "split": self.split,
            "replace": self.replace,
            "test": self.test,
            "escape": self.escape,
            "groups": self.groups,
        }

    def match(self, pattern, text, flags=""):
        result = re.search(pattern, str(text), self._flags(flags))
        if result is None:
            return None
        return {
            "value": result.group(0),
            "start": result.start(),
            "end": result.end(),
            "groups": list(result.groups()),
        }

    def search(self, pattern, text, flags=""):
        return self.match(pattern, text, flags)

    def find(self, pattern, text, flags=""):
        return self.findall(pattern, text, flags)

    def findall(self, pattern, text, flags="", groups=None):
        result = re.findall(pattern, str(text), self._flags(flags))
        if groups is not None and result and isinstance(result[0], tuple):
            return [item[int(groups)] for item in result]
        return result

    def split(self, pattern, text, flags=""):
        return re.split(pattern, str(text), flags=self._flags(flags))

    def replace(self, pattern, text, replacement, count=None):
        if count is None:
            return re.sub(pattern, replacement, str(text),
                          flags=self._flags())
        return re.sub(pattern, replacement, str(text),
                      count=int(count), flags=self._flags())

    def test(self, pattern, text, flags=""):
        return re.search(pattern, str(text), self._flags(flags)) is not None

    def escape(self, text):
        return re.escape(str(text))

    def groups(self, pattern, text, flags=""):
        result = re.search(pattern, str(text), self._flags(flags))
        if result is None:
            return None
        return list(result.groups())

    def _flags(self, flags=""):
        value = 0
        if flags:
            for flag in flags:
                if flag == "i":
                    value |= re.IGNORECASE
                elif flag == "m":
                    value |= re.MULTILINE
                elif flag == "s":
                    value |= re.DOTALL
                elif flag == "x":
                    value |= re.VERBOSE
        return value