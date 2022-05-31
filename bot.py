import telebot
import threading
from db import ReminderDatabase
from bot
from util import read_token

id = 283382228
db = "db"

bot = telebot.TeleBot(read_token(), threaded=True)
bot.send_message(id, "Starting Dairy Monthly Reminder")


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


    except Exception as e:
        bot.send_message(message.chat.id, e)
        log(str(e))

""" DEBUG """
def log(text):
    bot.send_message(id, text=f"{text}")


# schedule.every().day.at("16:31").do(check_and_send_reminder)


polling_thread = threading.Thread(target=lambda: bot.polling())
polling_thread.daemon = True
polling_thread.start()


