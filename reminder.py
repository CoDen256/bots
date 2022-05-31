import logging as log
from datetime import datetime
from db import ReminderDatabase

class Reminder:
    def __init__(self, db_name, notify):
        ReminderDatabase.setup(db_name)
        self.db_name = db_name
        self.notify = notify

    def check_month(self, db):
        (last_date_str, last_text) = db.get_last_reminder()
        current_date = datetime.today()
        last_date = datetime.strptime(last_date_str, "%Y-%m-%d")
        log.info(f"Checking: {current_date} > {last_date} + 62 days ?",)
        return (current_date - last_date).days >= 62

    def check_and_send_reminder(self):
        log.info("Checking reminder...")
        with ReminderDatabase(self.db_name) as db:
            if(self.check_month(db)):
                log.info("Check successful, sending the reminder...")
                self.notify("It's time to send an entry to your diary:")
            else:
                log.info("Check failed, skipping...")

    def process_entry(self, entry):
        new = False
        log.info(f"Processing entry: {entry}")
        with ReminderDatabase(self.db_name) as db:
            new = self.check_month(db)
            if new:
                current_date = datetime.today()
                month = '0'+str(current_date.month - 1) if current_date.month - \
                    1 < 10 else str(current_date.month-1)
                date = f"{current_date.year}-{month}-01"
                log.info(f"Check successful, inserting for date {date}")

                db.insert_reminder(date, entry)
            return (new, " -> ".join(list(db.get_last_reminder())))
