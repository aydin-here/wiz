import subprocess


class ProcessModule:

    def __init__(self):
        self.functions = {
            "run": self.run,
            "call": self.call,
            "open": self.open,
            "kill": self.kill,
            "wait": self.wait,
            "pid": self.pid,
            "alive": self.alive,
            "stdin": self.stdin,
            "stdout": self.stdout,
            "stderr": self.stderr,
        }

    def run(self, command, shell=True):
        result = subprocess.run(
            command,
            shell=shell,
            capture_output=True,
            text=True
        )

        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "code": result.returncode
        }

    def call(self, command, shell=True):
        return subprocess.call(command, shell=shell)

    def open(self, command, shell=True):
        return subprocess.Popen(
            command,
            shell=shell,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

    def kill(self, process):
        process.kill()
        return True

    def wait(self, process):
        return process.wait()

    def pid(self, process):
        return process.pid

    def alive(self, process):
        return process.poll() is None

    def stdin(self, process, data):
        process.stdin.write(str(data))
        process.stdin.flush()
        return True

    def stdout(self, process):
        return process.stdout.read()

    def stderr(self, process):
        return process.stderr.read()