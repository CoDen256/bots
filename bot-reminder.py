import telebot
from db import ReminderDatabase
# from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime

from util import read_token

id = 283382228
bot = telebot.TeleBot(
    read_token(), threaded=True)
bot.send_message(id, "Starting Dairy Reminder")

db = "db"



def check_month():
    (last_date_str, last_text) = get_last_reminder(db)
    current_date = datetime.today()
    last_date = datetime.strptime(last_date_str, "%Y-%m-%d")
    return (current_date - last_date).days >= 60


def check_and_send_reminder():
    print("Checking")
    if(check_month()):
        bot.send_message(
            id,
            text="It's time to send an entry to your diary:",
            parse_mode='markdown'
        )


@bot.message_handler(commands=['start', 'help'])
def start(message):
    try:
        bot.send_message(
            message.chat.id,
            text="Hello, I'll send you reminder every month to fill in the diary",
            parse_mode='markdown'
        )

    except Exception as e:
        bot.send_message(message.chat.id, e)
        log(str(e))


@bot.message_handler(content_types=["text"])
def text(message):
    try:
        if check_month():
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

    except Exception as e:
        bot.send_message(message.chat.id, e)
        log(str(e))

""" DEBUG """
def log(text):
    bot.send_message(id, text=f"{text}")


# schedule.every().day.at("16:31").do(check_and_send_reminder)


bot.polling()
