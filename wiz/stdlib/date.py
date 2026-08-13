from datetime import date as _date
from datetime import datetime, timedelta


class DateModule:

    def __init__(self):
        self.functions = {
            "today": self.today,
            "now": self.now,
            "iso": self.iso,
            "unix": self.unix,
            "from_unix": self.from_unix,
            "format": self.format,
            "parse": self.parse,
            "weekday": self.weekday,
            "weekday_name": self.weekday_name,
            "month_name": self.month_name,
            "is_leap": self.is_leap,
            "days_in_month": self.days_in_month,
            "add_days": self.add_days,
            "add_seconds": self.add_seconds,
            "diff": self.diff,
            "component": self.component,
            "age": self.age,
        }

    def today(self):
        today = _date.today()
        return {
            "year": today.year,
            "month": today.month,
            "day": today.day,
        }

    def now(self):
        now = datetime.now()
        return {
            "year": now.year,
            "month": now.month,
            "day": now.day,
            "hour": now.hour,
            "minute": now.minute,
            "second": now.second,
            "microsecond": now.microsecond,
        }

    def iso(self):
        return datetime.now().isoformat()

    def unix(self):
        import time
        return int(time.time())

    def from_unix(self, timestamp):
        dt = datetime.fromtimestamp(int(timestamp))
        return {
            "year": dt.year,
            "month": dt.month,
            "day": dt.day,
            "hour": dt.hour,
            "minute": dt.minute,
            "second": dt.second,
        }

    def format(self, pattern="%Y-%m-%d %H:%M:%S"):
        return datetime.now().strftime(pattern)

    def parse(self, text, pattern="%Y-%m-%d"):
        return {
            "date": datetime.strptime(str(text), pattern).date().isoformat()
        }

    def weekday(self, year, month, day):
        return _date(year, month, day).weekday()

    def weekday_name(self, year, month, day):
        return _date(year, month, day).strftime("%A")

    def month_name(self, month):
        return _date(2000, month, 1).strftime("%B")

    def is_leap(self, year):
        import calendar
        return calendar.isleap(int(year))

    def days_in_month(self, year, month):
        import calendar
        return calendar.monthrange(int(year), int(month))[1]

    def add_days(self, year, month, day, days):
        result = _date(year, month, day) + timedelta(days=int(days))
        return {
            "year": result.year,
            "month": result.month,
            "day": result.day,
        }

    def add_seconds(self, seconds):
        return (datetime.now() + timedelta(seconds=int(seconds))).isoformat()

    def diff(self, a, b):
        first = datetime.fromisoformat(str(a))
        second = datetime.fromisoformat(str(b))
        delta = second - first
        return {
            "seconds": delta.total_seconds(),
            "days": delta.days,
        }

    def component(self, name):
        now = datetime.now()
        components = {
            "year": now.year,
            "month": now.month,
            "day": now.day,
            "hour": now.hour,
            "minute": now.minute,
            "second": now.second,
        }
        return components.get(name)

    def age(self, year, month, day):
        now = _date.today()
        birth = _date(int(year), int(month), int(day))
        return now.year - birth.year - (
            (now.month, now.day) < (birth.month, birth.day)
        )
