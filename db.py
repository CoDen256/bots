import sqlite3
import logging as log

class ReminderDatabase(object):

    def __init__(self, db):
        log.info(f"Created Database {db}")
        self.db = db
        self.con = None

    def __enter__(self):
        log.info(f"Connected to {self.db}")
        self.con = sqlite3.connect(f"{self.db}.db")
        return self
  
    def __exit__(self, exc_type, exc_val, exc_tb):
        log.info(f"Closed connection to {self.db}")
        self.con.close()

    def insert_reminder(self, date, text):
        log.info(f"Inserting {date}, {text} to {self.db}")
        cur = self.con.cursor()
        cur.execute("INSERT INTO reminders VALUES (?, ?)", (date, text))
        self.con.commit()


    def get_last_reminder(self):
        log.info(f"Querying last reminder")
        cur = self.con.cursor()
        cur.execute("SELECT * FROM reminders ORDER BY date DESC LIMIT 1")
        value = cur.fetchone()
        log.info(f"Query Result:{value}")
        return value


    def create_db(self):
        log.info(f"Creating table reminders in {self.db}")
        cur = self.con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS reminders(date text, message text)")
        self.con.commit()


    def drop_db(self):
        log.info(f"Deleting table reminders in {self.db}")
        cur = self.con.cursor()
        cur.execute("DROP TABLE IF EXISTS reminders")
        self.con.commit()

    @staticmethod
    def setup(db):
        log.info("Setupping the database")
        with ReminderDatabase(db) as database:
            database.drop_db()
            database.create_db()

            database.insert_reminder("2022-03-01", "Text message for 2022-03-01")
