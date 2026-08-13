import os as _os
import platform as _platform
import getpass


class OsModule:

    def __init__(self):
        self.functions = {
            "name": self.name,
            "platform": self.platform,
            "arch": self.arch,
            "user": self.user,
            "home": self.home,
            "cwd": self.cwd,
            "chdir": self.chdir,
            "env": self.env,
            "getenv": self.getenv,
            "setenv": self.setenv,
            "unsetenv": self.unsetenv,
            "listdir": self.listdir,
            "abspath": self.abspath,
            "basename": self.basename,
            "dirname": self.dirname,
            "join": self.join,
            "split": self.split,
            "exists": self.exists,
            "isfile": self.isfile,
            "isdir": self.isdir,
            "sep": self.sep,
            "linesep": self.linesep,
            "remove": self.remove,
            "mkdir": self.mkdir,
            "rmdir": self.rmdir,
            "rename": self.rename,
            "walk": self.walk,
        }

    def name(self):
        return _os.name

    def platform(self):
        return _platform.system()

    def arch(self):
        return _platform.machine()

    def user(self):
        try:
            return getpass.getuser()
        except Exception:
            return _os.environ.get("USER", "")

    def home(self):
        return _os.path.expanduser("~")

    def cwd(self):
        return _os.getcwd()

    def chdir(self, path):
        _os.chdir(path)
        return True

    def env(self):
        return dict(_os.environ)

    def getenv(self, key, default=None):
        return _os.environ.get(str(key), default)

    def setenv(self, key, value):
        _os.environ[str(key)] = str(value)
        return True

    def unsetenv(self, key):
        _os.environ.pop(str(key), None)
        return True

    def listdir(self, path="."):
        return _os.listdir(str(path))

    def abspath(self, path):
        return _os.path.abspath(str(path))

    def basename(self, path):
        return _os.path.basename(str(path))

    def dirname(self, path):
        return _os.path.dirname(str(path))

    def join(self, *parts):
        return _os.path.join(*[str(part) for part in parts])

    def split(self, path):
        return list(_os.path.split(str(path)))

    def exists(self, path):
        return _os.path.exists(str(path))

    def isfile(self, path):
        return _os.path.isfile(str(path))

    def isdir(self, path):
        return _os.path.isdir(str(path))

    def sep(self):
        return _os.sep

    def linesep(self):
        return _os.linesep

    def remove(self, path):
        _os.remove(str(path))
        return True

    def mkdir(self, path, recursive=True):
        if recursive:
            _os.makedirs(str(path), exist_ok=True)
        else:
            _os.mkdir(str(path))
        return True

    def rmdir(self, path, recursive=False):
        if recursive:
            import shutil
            shutil.rmtree(str(path))
        else:
            _os.rmdir(str(path))
        return True

    def rename(self, old, new):
        _os.rename(str(old), str(new))
        return True

    def walk(self, path="."):
        return [
            {
                "root": root,
                "dirs": dirs,
                "files": files
            }
            for root, dirs, files in _os.walk(str(path))
        ]
