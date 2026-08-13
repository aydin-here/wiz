import sys


class BarsModule:

    def __init__(self):
        self.functions = {
            "bar": self.bar,
            "progress": self.progress,
            "track": self.track,
            "spinner": self.spinner,
            "blocks": self.blocks,
        }

    def _color(self, value, ratio):

        if not sys.stdout.isatty():
            return ""

        codes = {
            "green": "\033[32m",
            "yellow": "\033[33m",
            "red": "\033[31m",
            "reset": "\033[0m",
        }

        if ratio < 0.4:
            return codes["green"]
        if ratio < 0.8:
            return codes["yellow"]
        return codes["red"]

    def bar(self, current, total, width=30, fill="█", empty="░",
            color=True, label=None):

        total = max(1, int(total))
        current = max(0, min(int(current), total))

        ratio = current / total

        filled = int(round(ratio * width))

        chunk = fill * filled + empty * (width - filled)

        prefix = ""
        suffix = ""

        if color:
            prefix = self._color(current, ratio)
            suffix = "\033[0m\t" if prefix else ""

        if label is not None:
            prefix = f"{str(label)} {prefix}"
            suffix = "\033[0m" if prefix else ""

        return f"{prefix}[{chunk}]{suffix}"

    def progress(self, current, total, width=30, fill="█", empty="░",
                 color=True, percent=True):

        total = max(1, int(total))
        current = max(0, min(int(current), total))

        bar = self.bar(current, total, width, fill, empty, color)

        if percent:
            ratio = round(100 * current / total)
            return f"{bar} {ratio}%"

        return bar

    def track(self, current, total, width=24, fill="█", empty="░"):

        total = max(1, int(total))
        current = max(0, min(int(current), total))

        bar = self.progress(current, total, width, fill, empty, color=False)

        return f"{current}/{total} {bar}"

    def blocks(self, count, total=None, fill="█", empty="░"):

        count = int(count)
        total = int(total) if total is not None else count

        return fill * max(0, count) + empty * max(0, total - count)

    def spinner(self, frames=None, index=0):

        frames = frames or ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

        return frames[int(index) % len(frames)]