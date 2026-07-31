import os


class ConsoleModule:

    def __init__(self):
        self.functions = {
            "clear": self.clear,
            "size": self.size,
            "title": self.title,
        }

    def clear(self):
        os.system("cls" if os.name == "nt" else "clear")
        return True

    def size(self):
        size = os.get_terminal_size()

        return {
            "columns": size.columns,
            "rows": size.lines
        }

    def title(self, text):

        if os.name == "nt":
            os.system(f"title {text}")
        else:
            print(f"\33]0;{text}\a", end="", flush=True)

        return True