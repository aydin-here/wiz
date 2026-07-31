import threading


class ThreadModule:

    def __init__(self):
        self.functions = {
            "start": self.start,
            "sleep": self.sleep,
            "join": self.join,
            "alive": self.alive,
        }

    def start(self, target, *args):

        thread = threading.Thread(
            target=target,
            args=args
        )

        thread.start()

        return thread

    def join(self, thread):
        thread.join()
        return True

    def alive(self, thread):
        return thread.is_alive()

    def sleep(self, seconds):
        import time
        time.sleep(seconds)