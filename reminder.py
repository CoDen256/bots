import logging as log
from datetime import datetime, timedelta
from db import ReminderDatabase


class Reminder:
    def __init__(self, config, notify):
        self.config = config
        self.notify = notify

    def check_month(self, db):
        (last_date_str, _) = db.get_last_reminder()
        current_date = datetime.today()
        last_date = datetime.strptime(last_date_str, "%Y/%m")
        log.info(f"Checking: {current_date} > {last_date} + 62 days ?")
        return ((current_date - last_date).days >= 62, last_date)

    def check_and_send_reminder(self):
        log.info("Checking reminder...")
        with ReminderDatabase(self.config) as db:
            (too_old, last_month) = self.check_month(db)
            if too_old:
                next_month = self.get_next_month(last_month)
                log.info("Check successful, sending the reminder...")
                self.notify(
                    f"It's time to send an entry to your diary for {next_month}")
            else:
                log.info("Check failed, skipping...")

    def process_entry(self, entry):
        log.info(f"Processing entry: {entry}")
        with ReminderDatabase(self.config) as db:
            (too_old, last_month) = self.check_month(db)
            if too_old:
                next_month = self.get_next_month(last_month)
                log.info(
                    f"Check successful, inserting for next not filled month: {next_month}")

                self.publish(db, next_month, entry)
            else:
                log.info("Check failed, skipping...")
            return (too_old, " -> ".join(list(db.get_last_reminder())))

    def get_next_month(self, month):
        return (month + timedelta(days=32)).replace(day=1).strftime("%Y/%m")

    def publish(self, db, date, text):
        db.insert_reminder(date, text)
