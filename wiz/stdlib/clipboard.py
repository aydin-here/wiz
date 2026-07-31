import pyperclip


class ClipboardModule:

    def __init__(self):
        self.functions = {
            "get": self.get,
            "set": self.set,
            "clear": self.clear,
        }

    def get(self):
        return pyperclip.paste()

    def set(self, text):
        pyperclip.copy(str(text))
        return True

    def clear(self):
        pyperclip.copy("")
        return True