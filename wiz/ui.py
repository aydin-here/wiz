import os
import sys
import threading
import time
import urllib.request

if os.name == "nt":
    os.system("")

ENABLED = sys.stdout.isatty() and not os.environ.get("NO_COLOR")

CHUNK = 64 * 1024


class Color:
    RESET = "\x1b[0m"
    BOLD = "\x1b[1m"
    DIM = "\x1b[2m"
    RED = "\x1b[31m"
    GREEN = "\x1b[32m"
    YELLOW = "\x1b[33m"
    BLUE = "\x1b[34m"
    MAGENTA = "\x1b[35m"
    CYAN = "\x1b[36m"


def paint(text, *codes):
    if not ENABLED:
        return str(text)
    return "".join(codes) + str(text) + Color.RESET


def success(text):
    print(paint(text, Color.GREEN))


def info(text):
    print(paint(text, Color.CYAN))


def warn(text):
    print(paint(text, Color.YELLOW))


def error(text):
    print(paint(text, Color.RED))


class Spinner:
    FRAMES = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"

    def __init__(self, message):
        self._message = message
        self._stop = threading.Event()
        self._thread = None
        self._last_len = 0

    def _run(self):
        index = 0

        while not self._stop.wait(0.1):
            frame = paint(self.FRAMES[index % len(self.FRAMES)], Color.CYAN)
            self._render(f"{frame} {self._message}")
            index += 1

        self._clear()

    def _render(self, line):
        pad = max(0, self._last_len - len(line))
        sys.stdout.write("\r" + line + " " * pad)
        self._last_len = len(line)
        sys.stdout.flush()

    def _clear(self):
        sys.stdout.write("\r" + " " * self._last_len + "\r")
        self._last_len = 0
        sys.stdout.flush()

    def __enter__(self):
        if not ENABLED:
            print(f"  {self._message} ...")
            return self

        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        return self

    def __exit__(self, exc_type, exc, traceback):
        if self._thread is not None:
            self._stop.set()
            self._thread.join()


class ProgressBar:
    WIDTH = 28

    def __init__(self, label, total=0):
        self.label = label
        self.total = max(0, total)
        self.done = 0
        self._start = time.monotonic()
        self._last_len = 0

    @staticmethod
    def _fmt(size):
        value = float(size)

        for unit in ("B", "KB", "MB", "GB", "TB"):
            if value < 1024 or unit == "TB":
                if unit == "B":
                    return f"{value:.0f}B"
                return f"{value:.1f}{unit}"
            value /= 1024

        return "0B"

    @staticmethod
    def _fmt_time(seconds):
        seconds = max(0, int(seconds))
        minutes, secs = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)

        if hours:
            return f"{hours}:{minutes:02d}:{secs:02d}"

        return f"{minutes:02d}:{secs:02d}"

    def _line(self):
        elapsed = time.monotonic() - self._start
        speed = self.done / elapsed if elapsed > 0 else 0

        if self.total:
            ratio = min(1.0, self.done / self.total)
            eta = (self.total - self.done) / speed if speed > 0 else 0
            size = f"{self._fmt(self.done)}/{self._fmt(self.total)}"

            filled = int(self.WIDTH * ratio)
            bar = "█" * filled + "░" * (self.WIDTH - filled)
        else:
            sweep = int((time.monotonic() % 1.0) * (self.WIDTH - 3))
            cells = ["░"] * self.WIDTH

            for index in range(3):
                cells[min(self.WIDTH - 1, sweep + index)] = "█"

            bar = "".join(cells)
            size = f"{self._fmt(self.done)}/?"
            eta = 0

        return (
            f"  {self.label} {bar} {size} "
            f"[{self._fmt_time(elapsed)}<{self._fmt_time(eta)}, "
            f"{self._fmt(speed)}/s]"
        )

    def update(self, done):
        if not ENABLED:
            return

        self.done = done
        line = self._line()
        pad = max(0, self._last_len - len(line))
        sys.stdout.write("\r" + line + " " * pad)
        self._last_len = len(line)
        sys.stdout.flush()

    def finish(self):
        if not ENABLED:
            print(f"  {self.label} done")
            return

        if not self.total:
            self.total = self.done

        self.update(self.done)
        sys.stdout.write("\r\n")
        sys.stdout.flush()

    def clear(self):
        if not ENABLED:
            return

        sys.stdout.write("\r" + " " * self._last_len + "\r")
        self._last_len = 0
        sys.stdout.flush()


def download(url, dest, label="Downloading", timeout=20, user_agent="wiz-updater"):
    request = urllib.request.Request(url, headers={"User-Agent": user_agent})
    bar = None

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.headers.get("Content-Length")
            total = int(raw) if raw else 0

            bar = ProgressBar(label, total)

            with open(dest, "wb") as file:
                done = 0

                while True:
                    chunk = response.read(CHUNK)

                    if not chunk:
                        break

                    file.write(chunk)
                    done += len(chunk)
                    bar.update(done)

            bar.finish()
    except Exception:
        if bar is not None:
            bar.clear()

        raise
