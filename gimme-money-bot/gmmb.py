import telebot
import uuid

bot = telebot.TeleBot("", threaded=False)
bot.send_message(283382228, "Starting GMMB")


class Reminder:
    def __init__(self, description, date, users) -> None:
        self.users = users
        self.id = uuid.uuid4() 
        self.description = description
        self.period = None
        self.date = date

    def prettify(self):
        return f"{self.description}\n{self.prettify_users(self.users)}\n{self.date}"

    def prettify_users(self, users):
        pretty = ""
        for user in users:
            pretty += user.tag
class User:
    def __init__(self, tag) -> None:
        self.tag = tag;
        self.done = False

reminders = {
    # group: reminder
}

@bot.message_handler(commands=['start', 'help'])
def start(message):
    try:
        bot.send_message(
            message.chat.id,
            text="Hello, I need your money",
            parse_mode='markdown'
        )

    except Exception as e:
        bot.send_message(message.chat.id, e)
        log(str(e))

@bot.message_handler(commands=['add'])
def add(message):
    try:
        args = extract(message)
        description, participants, date = args.split("\n")
        reminders[message.chat.id] = Reminder(description ,date, list([User(tag) for tag in participants.split()]))

        bot.send_message(message.chat.id, "Reminder created")
    except Exception as e:
        bot.send_message(message.chat.id, e)
        log(str(e))

@bot.message_handler(commands=['all'])
def add(message):
    try:
        all = ""
        if message.chat.id not in reminders: 
            bot.send_message(message.chat.id, "No reminders added.")
            return

        for rem in reminders[message.chat.id]:
            all += rem.prettify()
        bot.send_message(message.chat.id, all)
    except Exception as e:
        bot.send_message(message.chat.id, e)
        log(str(e))

""" DEBUG """
def log(text):
    bot.send_message(283382228, text=f"{text}")

def extract(command, message):
    split = message.text.split("/"+command)
    if not split[1] or split[1].isspace():
        bot.send_message(message.chat.id, "Wrong format for "+command)
        return
    return split[1]

bot.polling()