import logging as log
import traceback
import telebot
from time import sleep

class ReminderBot:
    BOT_TIMEOUT = 10
    START_MESSAGE = "Starting Dairy Monthly Reminder"

    def __init__(self, id, token):
        self.id = id
        self.bot = telebot.TeleBot(token, threaded=False)
        self.log(ReminderBot.START_MESSAGE)
        self.alive = True

    def start_polling(self):
        log.info("Starting bot polling...")
        while self.alive:
            try:
                log.info("-"*90)
                log.info("New bot instance started!")
                self.bot.polling(
                    none_stop=True, timeout=ReminderBot.BOT_TIMEOUT)
            except Exception as ex:
                self.log_error("Bot polling failed, restarting in {}sec. Error:\n{}"
                               .format(ReminderBot.BOT_TIMEOUT, ex))
                log.error(traceback.format_exc())
                self.bot.stop_polling()
                sleep(ReminderBot.BOT_TIMEOUT)
            else:
                self.bot.stop_polling()
                log.info("Bot polling loop finished")
                self.alive = False

    def send(self, id, text):
        self.bot.send_message(id, text=text, parse_mode='markdown')
        log.info(f"Message sent to {id}: {text}")

    def log(self, message):
        self.bot.send_message(self.id, text=message, parse_mode='markdown')
        log.info(message)

    def log_error(self, error):
        message = f"Error: {error}"
        self.bot.send_message(self.id, text=message, parse_mode='markdown')
        log.error(message)
