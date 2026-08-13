import zipfile
import tarfile
import os


class ArchiveModule:

    def __init__(self):
        self.functions = {
            "zip": self.zip,
            "unzip": self.unzip,
            "tar": self.tar,
            "untar": self.untar,
            "list": self.list,
            "inspect": self.inspect,
        }

    def _files(self, paths):
        result = []

        for path in paths:

            if os.path.isdir(path):

                for root, _dirs, files in os.walk(path):
                    for name in files:
                        result.append(os.path.join(root, name))

            else:
                result.append(str(path))

        return result

    def zip(self, source, dest):

        sources = self._files([source])

        with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as archive:

            for file in sources:
                archive.write(file, file)

        return True

    def unzip(self, source, dest="."):

        with zipfile.ZipFile(source, "r") as archive:
            archive.extractall(dest)

        return True

    def tar(self, source, dest, mode="xz"):

        sources = self._files([source])

        with tarfile.open(dest, f"w:{mode}") as archive:

            for file in sources:
                archive.add(file)

        return True

    def untar(self, source, dest="."):

        with tarfile.open(source, "r:*") as archive:
            archive.extractall(dest)

        return True

    def list(self, source):

        if zipfile.is_zipfile(source):

            with zipfile.ZipFile(source, "r") as archive:
                return archive.namelist()

        with tarfile.open(source, "r:*") as archive:
            return archive.getnames()

    def inspect(self, source):

        members = self.list(source)

        return {
            "path": os.path.abspath(source),
            "size": os.path.getsize(source),
            "files": len(members),
            "members": members,
        }