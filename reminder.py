import logging as log
from datetime import datetime

log.basicConfig(level=log.DEBUG)

class Reminder:
    def __init__(self, db, notify):
          self.db = db
          self.notify = notify
  
    def check_month(self):
        (last_date_str, last_text) = self.db.get_last_reminder()
        current_date = datetime.today()
        last_date = datetime.strptime(last_date_str, "%Y-%m-%d")
        return (current_date - last_date).days >= 60


    def check_and_send_reminder(self):
        log.info("Checking...")
        if(self.check_month()):
            self.notify("It's time to send an entry to your diary:")

    def process_entry(self, entry):
        if self.check_month():
            current_date = datetime.today()
            month = '0'+str(current_date.month - 1) if current_date.month-1 < 10 else str(current_date.month-1 )
            date = f"{current_date.year}-{month}-01"

            insert_reminder(db, date, message.text)

            bot.send_message(
            message.chat.id,
            text=f"Diary entry saved for {date}",
            parse_mode='markdown'
            )
        else:
            bot.send_message(
            message.chat.id,
            text=f"Diary entry already saved {get_last_reminder(db)}",
            parse_mode='markdown'
            )