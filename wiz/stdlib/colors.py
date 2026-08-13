RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
ITALIC = "\033[3m"
UNDERLINE = "\033[4m"
BLINK = "\033[5m"
REVERSE = "\033[7m"

COLORS = {
    "black": "\033[30m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[37m",
    "gray": "\033[90m",
}

BACKGROUNDS = {
    "black": "\033[40m",
    "red": "\033[41m",
    "green": "\033[42m",
    "yellow": "\033[43m",
    "blue": "\033[44m",
    "magenta": "\033[45m",
    "cyan": "\033[46m",
    "white": "\033[47m",
}


class ColorsModule:

    def __init__(self):

        styles = {}

        for name, code in COLORS.items():
            styles[name] = self._make_style(code)

        styles["bold"] = self._make_style(BOLD)
        styles["dim"] = self._make_style(DIM)
        styles["italic"] = self._make_style(ITALIC)
        styles["underline"] = self._make_style(UNDERLINE)
        styles["blink"] = self._make_style(BLINK)
        styles["reverse"] = self._make_style(REVERSE)

        styles["paint"] = self.paint
        styles["strip"] = self.strip
        styles["rainbow"] = self.rainbow
        styles["palette"] = self.palette

        self.functions = styles

    def _make_style(self, code):

        def style(text):
            return code + str(text) + RESET

        return style

    def paint(self, text, color="white", bg=None):

        code = COLORS.get(str(color).lower())

        if code is None:
            code = COLORS["white"]

        background = BACKGROUNDS.get((bg or "").lower(), "")

        return background + code + str(text) + RESET

    def strip(self, text):
        import re
        return re.sub(r"\033\[[0-9;]*m", "", str(text))

    def rainbow(self, text):
        order = ["red", "yellow", "green", "cyan", "blue", "magenta"]
        return "".join(
            COLORS[order[i % len(order)]] + char
            for i, char in enumerate(str(text))
        ) + RESET

    def palette(self):
        return list(COLORS.keys())