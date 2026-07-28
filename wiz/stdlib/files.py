import os


class FilesModule:

    def __init__(self):
        self.functions = {
            "read": self.read,
            "write": self.write,
            "append": self.append,
            "exists": self.exists,
            "delete": self.delete,
            "mkdir": self.mkdir,
            "list": self.list,
            "rename": self.rename,
        }

    def read(self, filename, mode="r"):
        with open(filename, mode) as file:
            return file.read()

    def write(self, filename, data, mode="w"):
        with open(filename, mode) as file:
            file.write(str(data))

        return True

    def append(self, filename, data):
        with open(filename, "a") as file:
            file.write(str(data))

        return True

    def exists(self, path):
        return os.path.exists(path)

    def delete(self, path):
        os.remove(path)
        return True

    def mkdir(self, path):
        os.makedirs(path, exist_ok=True)
        return True

    def list(self, path="."):
        return os.listdir(path)

    def rename(self, old_name, new_name):
        os.rename(old_name, new_name)
        return True