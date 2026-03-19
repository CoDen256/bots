import telebot
import configparser
import random
from models import *

config = configparser.ConfigParser()
config.read("application.cfg", encoding="UTF-8")

triggers = config['BOT']['triggers'].split(",")
token = config['BOT']['token']
wolf_error = config['BOT']['error']
bot = telebot.TeleBot(token, threaded=False)
debug_id = 283382228


@bot.message_handler(commands=['start', 'help'])
def start(message):
    try:
        bot.send_message(
            message.chat.id,
            text="Добро пожаловать в *волкобота*\nЭто базовые комманды для управления волком.",
            parse_mode='markdown'
        )

        bot.send_message(
            message.chat.id,
            text="/add {quote} - Добавляет цитату для триггера.\n" + \
                 "/remove {i} - Удаляет цитату по индексу.(i=0 - удалить все цитаты)\n" + \
                 "/list - Все цитаты и их индексы.\n"
        )
    except Exception as e:
        bot.send_message(message.chat.id, wolf_error)
        log(str(e))


@bot.message_handler(commands=['add'])
def add(message):
    try:
        separated = message.text.replace("@volk_ne_lev_bot", "").split("/add")
        if not separated[1] or separated[1].isspace():
            bot.send_message(message.chat.id,
                             "Неверное значение для /add")
            return
        quote = Quote(value=separated[1].strip())
        quote.save()

        bot.send_message(message.chat.id, f"Выражение *{quote.value}* было успешно добавлено в лексикон волка",
                         parse_mode='markdown')
    except Exception as e:
        bot.send_message(message.chat.id, wolf_error)
        log(str(e))


@bot.message_handler(commands=['remove'])
def remove(message):
    try:
        separated = message.text.split("/remove")
        if not separated[1] or separated[1].isspace() or not separated[1].strip().isnumeric():
            bot.send_message(message.chat.id,
                             "Неверное значение для /remove")
            return

        quotes = sorted(Quote.all(), key=lambda x: x.value)
        n = int(separated[1].strip()) - 1
        if not (-1 <= n < len(quotes)):
            bot.send_message(message.chat.id,
                             "Неверный индекс цитаты.")
            return

        if n == -1:
            for quote in Quote.all():quote.delete()
            bot.send_message(message.chat.id, f"Все выражения волка были удалены.")
            return

        quote = quotes[n]
        quote.delete()

        bot.send_message(message.chat.id, f"Выражение *{quote.value}* было успешно забыто волком.",
                         parse_mode='markdown')
    except Exception as e:
        bot.send_message(message.chat.id, wolf_error)
        log(str(e))


@bot.message_handler(commands=['list'])
def quotes_list(message):
    try:
        quotes = ""
        lists = sorted(Quote.all(), key=lambda x: x.value)
        if not lists:
            bot.send_message(message.chat.id, "Список цитат волка пуст. Волк молчит, а значит перебивать его не стоит.")
            return

        for i, quote in enumerate(lists):
            quotes += f"{i + 1}. {quote.value}\n"
        bot.send_message(message.chat.id, text=quotes)
    except Exception as e:
        bot.send_message(message.chat.id, wolf_error)
        log(str(e))


""" ANALYSERS """


@bot.message_handler(content_types=["text"])
def text_analyser(message):
    try:
        for trigger in triggers:
            if trigger in message.text.lower():
                generate_quote(message)
                return
    except Exception as e:
        bot.send_message(message.chat.id, wolf_error)
        log(str(e))


@bot.message_handler(content_types=["sticker"])
def sticker_analyser(message):
    try:
        if message.sticker.set_name == 'strong_isnot_who' or message.sticker.emoji == '🐺':
            generate_quote(message)
    except Exception as e:
        bot.send_message(message.chat.id, wolf_error)
        log(str(e))


""" DEBUG """

def log(text):
    bot.send_message(debug_id, text=f"{text}")

def generate_quote(message):
    quotes = list(map(lambda x: x.value, Quote.all()))
    if quotes:
        bot.send_message(message.chat.id, random.choice(quotes))
    else:
        bot.send_message(message.chat.id, "У волка нет слов, чтобы прокомментировать данную ситуацию")

bot.polling()