from reminder_bot import ReminderBot
from reminder import Reminder
from util import read_token
import threading
import schedule

id = 283382228
db_name = "db"
time = "11:05"
token = read_token("token")

reminder_bot = ReminderBot(id, token)
reminder = Reminder(db_name, lambda text: reminder_bot.send(id, text))
bot = reminder_bot.bot

@bot.message_handler(commands=['start', 'help'])
def start(message):
    reminder_bot.send(
        message.chat.id, 
        "Hello, I'll send you reminder every month to fill in the diary")

@bot.message_handler(content_types=["text"])
def text(message):
    reminder.process_entry(message.text)


polling_thread = threading.Thread(target=reminder_bot.start_polling)
polling_thread.daemon = True
polling_thread.start()


schedule.every().day.at(time).do(reminder.check_and_send_reminder)


while reminder_bot.alive:
    schedule.run_pending()
    time.sleep(1)