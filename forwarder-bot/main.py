import re

import datetime
import pytz
import telebot

import configparser

parser = configparser.RawConfigParser()
parser.read("bot.ini")
cfg = parser["main"]
BOT_TOKEN = cfg["token"]
CHAT_ID = cfg["chat"]
TZ = pytz.timezone("Europe/Berlin")


class TelegramUI:
    def __init__(self, chat_id, token):
        self.chat_id = chat_id
        self.bot = telebot.TeleBot(token)

    def start_blocking(self):
        # Polling for Telegram bot commands
        print("Bot is running...")
        self.bot.infinity_polling()

    def delete(self, message):
        try:
            self.bot.delete_message(message.chat.id, message.message_id)
        except Exception as e:
            self.error("Could not delete a message", e)

    def send(self, text, **kwargs):
        try:
            return self.bot.send_message(self.chat_id, text, **kwargs)
        except Exception as e:
            self.error("Could not send a message", e)

    def edit(self, id, text, **kwargs):
        try:
            self.bot.edit_message_text(text, self.chat_id, id, **kwargs)
        except Exception as e:
            self.error("Could not send a message", e)

    def reply(self, message, text, **kwargs):
        try:
            self.bot.send_message(self.chat_id, text, **kwargs)
        except Exception as e:
            self.error(f"Could not reply to a message {message.text}", e)

    def error(self, message, error):
        print(f"Error! {message}: {error}")
        self.bot.send_message(self.chat_id, f"Error! {message}:\n{error}")


ui = TelegramUI(CHAT_ID, BOT_TOKEN)
bot = ui.bot
tag_to_id = {
    "test": 3
}

@bot.message_handler(commands=['start'])
def start_message(message):
    print(f"User started: {message.chat.id}")
    ui.reply(message,
             f"Hello! I'll help you with stuff\nYour chat: `{message.chat.id}`", parse_mode="Markdown")
    ui.delete(message)

@bot.message_handler(commands=["pin"])
def pin(message):
    pin_or_edit(message, message.text.removeprefix("/pin").strip(), message_thread_id=message.message_thread_id)
    ui.delete(message)

tag_regex = r'^\s*#(\w+)\s+.*|.*\s+#(\w+)\s*$'
def extract_tag(text):
    if not (match:= re.match(tag_regex, text)): return None
    return next(g for g in match.groups() if g)

is_general = lambda message: message.message_thread_id is None or (message.text and re.match(tag_regex, message.text))
@bot.edited_message_handler(func=is_general)
@bot.message_handler(func=is_general)
def forward(message):
    try:
        if not (tag:=extract_tag(message.text)): return
        new, topic_id = get_or_create_topic(tag, message)

        msg = ui.send(re.sub(fr"\s?#{tag}\s?", "", message.text), message_thread_id=topic_id)
        ui.delete(message)
        if new:
            bot.unpin_chat_message(message.chat.id, msg.message_id)
    except Exception as e:
        ui.error(f"Forwarding failed", e)


is_topic = lambda message: message.message_thread_id is not None and message.reply_to_message is not None and message.reply_to_message.forum_topic_created is not None
@bot.message_handler(commands=["update"], func=is_topic)
def upd_topics_id(message):
    created = message.reply_to_message
    id = created.message_thread_id
    append_topic(message.text.removeprefix("/update").strip(), id, message)
    ui.delete(message)

@bot.message_handler(commands=["remove"], func=is_topic)
def remove_topics_id(message):
    created = message.reply_to_message
    id = created.message_thread_id
    rm_topic(id, message)
    ui.delete(message)

@bot.message_handler(commands=["id"], func=is_topic)
def get_id(message):
    id = message.reply_to_message.message_thread_id
    ui.send(str(id), message_thread_id=id)
    ui.delete(message)

@bot.message_handler(func=is_topic)
def upd_topic(message):
    created = message.reply_to_message
    id = created.message_thread_id
    if created.chat.title != created.forum_topic_created.name:
        append_topic(created.forum_topic_created.name, id, message)
        ui.send(message.text, message_thread_id=id)
        ui.delete(message)

def rm_topic(id, message):
    topics, compiled = get_topics(message)
    if id not in topics.values(): return

    compiled = list(filter(lambda s: not s.endswith(str(id)), compiled))
    pin_or_edit(message, "\n".join(compiled))

def append_topic(name, id, message):
    if not name: return
    topics, compiled = get_topics(message)
    if (name, id) in topics.items():
        return

    compiled = list(filter(lambda s: not s.endswith(str(id)), compiled))
    compiled = compiled + [f"{name} -> {id}"]
    pin_or_edit(message, "\n".join(compiled))

def pin_or_edit(message, text, **kwargs):
    chat = bot.get_chat(message.chat.id)
    if not chat.pinned_message:
        new = ui.send(text)
        bot.pin_chat_message(chat.id, new.message_id, **kwargs)
    else:
        ui.edit(chat.pinned_message.message_id, text)


def get_topics(message):
    chat = bot.get_chat(message.chat.id)
    if not chat.pinned_message: return {},[]
    if " -> " not in chat.pinned_message.text:
        bot.unpin_chat_message(message.chat.id, chat.pinned_message.message_id)
        return get_topics(message)
    compiled = chat.pinned_message.text.split("\n")
    return dict({(topic.split(" -> ")[0], int(topic.split(" -> ")[1])) for topic in compiled}), compiled


def get_or_create_topic(tag, message):
    topics, _ = get_topics(message)
    if tag not in topics.keys():
        topic = bot.create_forum_topic(message.chat.id, tag)
        append_topic(tag, topic.message_thread_id, message)
        return True, topic.message_thread_id
    return False, topics[tag]




ui.start_blocking()
