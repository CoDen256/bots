import telebot
import configparser
from antonyms import *
from image_generator import generate_demotivator_image

config = configparser.ConfigParser()
config.read('application.cfg')

error_message = "Ой мне поплохело..."
debug_id = 283382228

bot = telebot.TeleBot(config["BOT"]["token"], threaded=False)
bot.send_message(debug_id, "Starting Demotivator bot...")


@bot.message_handler(commands=['start', 'help'])
def start(message):
    try:
        bot.send_message(
            message.chat.id,
            text="Добро пожаловать в *Демотиватор-бота*\nЭто базовые комманды для управления ботом.",
            parse_mode='markdown'
        )

        bot.send_message(
            message.chat.id,
            text="/demotivate {quote} - Демотивирует цитату.\n" + \
                 "/synonym {word} - Находит синоним к данному слову. \n"
                 "/antonym {word} - Находит антоним к данному слову. \n"
                 "/add {key} {value} - Добавляет антоним.\n"
        )
    except Exception as e:
        bot.send_message(message.chat.id, error_message)
        log(str(e))


@bot.message_handler(commands=['demotivate'])
def demotivate(message):
    try:
        separated = message.text.split("/demotivate")
        words = separated[1].strip().split()

        original = " ".join(words)
        demotivated = "нет блять, " + demotivate_sentence(words)
        bot.send_message(message.chat.id, demotivated, parse_mode='markdown')

        filename = generate_demotivator_image(original, demotivated)

        image = open(filename, 'rb')
        bot.send_photo(message.chat.id, image)

    except Exception as e:
        bot.send_message(message.chat.id, error_message + str(e))
        log(str(e))


@bot.message_handler(commands=['add'])
def add(message):
    try:
        separated = message.text.split("/add")
        key_value = separated[1].strip().split()
        key = key_value[0].strip()
        value = key_value[1].strip()

        write_to_template(key, value)

        bot.send_message(message.chat.id, key + "=" + value + " is added", parse_mode='markdown')
    except Exception as e:
        bot.send_message(message.chat.id, error_message + str(e))
        log(str(e))


@bot.message_handler(commands=['synonym'])
def synonym(message):
    try:
        separated = message.text.split("/synonym")
        word = separated[1]

        bot.send_message(message.chat.id, "\n".join(get_synonym_for_word(word.strip())), parse_mode='markdown')
    except Exception as e:
        bot.send_message(message.chat.id, error_message + str(e))
        log(str(e))


@bot.message_handler(commands=['antonym'])
def antonym(message):
    try:
        separated = message.text.split("/antonym")
        word = separated[1]

        bot.send_message(message.chat.id, "\n".join(get_antonym_for_word(word.strip())), parse_mode='markdown')
    except Exception as e:
        bot.send_message(message.chat.id, error_message + str(e))
        log(str(e))


""" DEBUG """


def log(text):
    bot.send_message(debug_id, text=f"{text}")


bot.polling()
