import sqlite3

class ReminderDatabase:

    def __init__(self, db):
        self.db = db
        self.con = None

    def __enter__(self):
        self.con = sqlite3.connect(f"{self.db}.db")
        return self.con
  
    def __exit__(self):
        self.con.close()

    def insert_reminder(self, date, text):
        cur = self.con.cursor()
        cur.execute("INSERT INTO reminders VALUES (?, ?)", (date, text))
        self.con.commit()


    def get_last_reminder(self):
        cur = self.con.cursor()
        cur.execute("SELECT * FROM reminders ORDER BY date DESC LIMIT 1")
        value = cur.fetchone()
        return value


    def create_db(self):
        cur = self.con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS reminders(date text, message text)")
        self.con.commit()


    def drop_db(self):
        cur = self.con.cursor()
        cur.execute("DROP TABLE IF EXISTS reminders")
        self.con.commit()

    def setup(self):
        self.drop_db()
        self.create_db()

        self.insert_reminder("2022-03-01", "Text message for 2022-04-01")
