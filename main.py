from reminder_bot import ReminderBot
from reminder import Reminder
from config import token, notion_token, notion_database_id, time, id
from time import sleep
import logging as log
import threading
import schedule

reminder_bot = ReminderBot(id, token)
reminder = Reminder(
    config = {
        "token": notion_token, 
        "database": notion_database_id
    },
    notify = lambda text: reminder_bot.send(id, text))

bot = reminder_bot.bot


@bot.message_handler(commands=['start', 'help'])
def start(message):
    reminder_bot.send(
        message.chat.id,
        "Hello, I'll send you reminder every month to fill in the diary")


@bot.message_handler(content_types=["text"])
def text(message):
    (new, result) = reminder.process_entry(message.text)
    if (new):
        reminder_bot.send(
            message.chat.id, f"Diary entry was successfully saved: \n{result}")
    else:
        reminder_bot.send(
            message.chat.id, f"Diary entry already exists: \n{result}")


log.info(f"Setting up shedule to run at {time} every day...")
schedule.every().day.at(time).do(reminder.check_and_send_reminder)


polling_thread = threading.Thread(target=reminder_bot.start_polling)
polling_thread.daemon = True
polling_thread.start()


while reminder_bot.alive:
    schedule.run_pending()
    sleep(1)
