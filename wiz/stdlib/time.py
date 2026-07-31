import time
from datetime import datetime


class TimeModule:

    def __init__(self):
        self.functions = {
            "now": self.now,
            "sleep": self.sleep,
            "sleep_ms": self.sleep_ms,
            "timestamp": self.timestamp,
            "format": self.format,
            "year": self.year,
            "month": self.month,
            "day": self.day,
            "hour": self.hour,
            "minute": self.minute,
            "second": self.second,
        }

    def now(self):
        return time.time()

    def sleep(self, seconds):
        time.sleep(seconds)
        return True

    def sleep_ms(self, milliseconds):
        time.sleep(milliseconds / 1000)
        return True

    def timestamp(self):
        return int(time.time())

    def format(self, pattern="%Y-%m-%d %H:%M:%S"):
        return datetime.now().strftime(pattern)

    def year(self):
        return datetime.now().year

    def month(self):
        return datetime.now().month

    def day(self):
        return datetime.now().day

    def hour(self):
        return datetime.now().hour

    def minute(self):
        return datetime.now().minute

    def second(self):
        return datetime.now().second