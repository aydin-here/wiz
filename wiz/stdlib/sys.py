import sys as _sys
import os as _os


class SysModule:

    def __init__(self):
        self.functions = {
            "args": self.args,
            "exit": self.exit,
            "platform": self.platform,
            "python": self.python,
            "pid": self.pid,
            "version": self.version,
            "executable": self.executable,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "stdin": self.stdin,
            "path": self.path,
            "modules": self.modules,
            "gc": self.gc,
        }

    def args(self):
        return list(_sys.argv)

    def exit(self, code=0):
        _sys.exit(int(code))

    def platform(self):
        return _sys.platform

    def python(self):
        return _sys.version.split()[0]

    def pid(self):
        return _os.getpid()

    def version(self):
        return _sys.version

    def executable(self):
        return _sys.executable

    def stdout(self, text, end="\n"):
        _sys.stdout.write(str(text) + end)
        _sys.stdout.flush()
        return True

    def stderr(self, text, end="\n"):
        _sys.stderr.write(str(text) + end)
        _sys.stderr.flush()
        return True

    def stdin(self, prompt="", end="\n"):
        if end == "":
            return input(str(prompt))
        return input(str(prompt) + end)

    def path(self):
        return list(_sys.path)

    def modules(self):
        return sorted(_sys.modules)

    def gc(self):
        import gc
        return gc.collect()
