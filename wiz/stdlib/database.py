import sqlite3


class DatabaseModule:

    def __init__(self):
        self.functions = {
            "open": self.open,
            "close": self.close,
            "execute": self.execute,
            "query": self.query,
            "commit": self.commit,
        }

    def open(self, filename):
        return sqlite3.connect(filename)

    def close(self, db):
        db.close()
        return True

    def execute(self, db, sql, params=None):

        cursor = db.cursor()

        cursor.execute(sql, params or ())

        return cursor

    def query(self, db, sql, params=None):

        cursor = db.cursor()

        cursor.execute(sql, params or ())

        return cursor.fetchall()

    def commit(self, db):
        db.commit()
        return True