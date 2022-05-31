import logging as log
from datetime import datetime, timedelta
from db import ReminderDatabase


class Reminder:
    def __init__(self, config, notify):
        self.config = config
        self.notify = notify

    def check_month(self, db):
        (last_date_str, last_text) = db.get_last_reminder()
        current_date = datetime.today()
        last_date = datetime.strptime(last_date_str, "%Y/%m")
        log.info(f"Checking: {current_date} > {last_date} + 62 days ?",)
        return (current_date - last_date).days >= 62

    def check_and_send_reminder(self):
        log.info("Checking reminder...")
        with ReminderDatabase(self.config) as db:
            if(self.check_month(db)):
                log.info("Check successful, sending the reminder...")
                self.notify("It's time to send an entry to your diary:")
            else:
                log.info("Check failed, skipping...")

    def process_entry(self, entry):
        new = False
        log.info(f"Processing entry: {entry}")
        with ReminderDatabase(self.config) as db:
            new = self.check_month(db)
            if new:
                date = self.get_previous_month()
                log.info(f"Check successful, inserting for previous month: {date}")
                
                self.publish(db, date, entry)
            return (new, " -> ".join(list(db.get_last_reminder())))

    def get_previous_month(self):
        today = datetime.today()
        first = today.replace(day=1)
        lastMonth = first - timedelta(days=1)
        return lastMonth.strftime("%Y/%m")

    def publish(self, db, date, text):
        db.insert_reminder(date, text)