import configparser
import pytz
import re
import telebot
from telebot.types import Message

parser = configparser.RawConfigParser()
parser.read("bot.ini")
cfg = parser["main"]
BOT_TOKEN = cfg["token"]
TZ = pytz.timezone("Europe/Berlin")

class TelegramUI:
    def __init__(self, token):
        self.bot = telebot.TeleBot(token)

    def start_blocking(self):
        # Polling for Telegram bot commands
        print("Bot is running...")
        self.bot.infinity_polling()

    def pin(self, message, **kwargs):
        try:
            return self.bot.pin_chat_message(message.chat.id, message.message_id, **kwargs)
        except Exception as e:
            self.error(message, e, "Could not pin")

    def unpin(self, message, **kwargs):
        try:
            return self.bot.unpin_chat_message(message.chat.id, message.message_id, **kwargs)
        except Exception as e:
            self.error(message, e, "Could not unpin")

    def get_chat(self, message):
        try:
            return self.bot.get_chat(message.chat.id)
        except Exception as e:
            self.error(message, e, "Could not get chat: " + message.chat.id)

    def create_topic(self, message, topic, **kwargs):
        try:
            return self.bot.create_forum_topic(message.chat.id, topic, **kwargs)
        except Exception as e:
            self.error(message, e, f"Could not create forum: {topic}")

    def delete(self, message, **kwargs):
        try:
            return self.bot.delete_message(message.chat.id, message.message_id, **kwargs)
        except Exception as e:
            self.error(message, e, "Could not delete")

    def copy(self, message, **kwargs):
        try:
            id = self.bot.copy_message(message.chat.id, message.chat.id, message.message_id, **kwargs).message_id
            new = Message.de_json(message.json)
            new.id = id
            new.message_id = id
            return new
        except Exception as e:
            self.error(message, e, f"Could not copy message")

    def send(self, message, text, **kwargs):
        try:
            return self.bot.send_message(message.chat.id, text, **kwargs)
        except Exception as e:
            self.error(message, e, f"Could not send: {text}")

    def edit(self, message, text, **kwargs):
        try:
            if message.content_type != "text":
                if message.caption == text: return None
                return self.bot.edit_message_caption(text, message.chat.id, message.message_id, **kwargs)

            if message.text == text or not text: return None
            return self.bot.edit_message_text(text, message.chat.id, message.message_id, **kwargs)
        except Exception as e:
            self.error(message, e, f"Could not edit to: {text}")

    def reply(self, message, text, **kwargs):
        try:
            return self.bot.reply_to(message, text, **kwargs)
        except Exception as e:
            self.error(message, e, f"Could not reply: {text}")

    def error(self, message, error, additional_info=None):
        result = f"❌ {additional_info if additional_info else ''}\n{error}"
        print(result.replace("\n", " ") + " Message: " + str(message.text))
        self.bot.reply_to(message, result)


ui = TelegramUI(BOT_TOKEN)
bot = ui.bot


def extract_tag(text):
    text = text.strip()
    if not (match := re.match(r"^#(\w+)$|^#(\w+).+|.+#(\w+)$", text, re.RegexFlag.DOTALL)): return None
    return next(g for g in match.groups() if g)


def fix_caption_as_text(message):
    if not message.text and message.caption: message.text = message.caption
    if not message.text: message.text = ""

def has_tag_to_forward(message):
    fix_caption_as_text(message)
    return (message.text
            and extract_tag(message.text)
            and not message.forward_from_message_id)


def is_topic(message):
    fix_caption_as_text(message)
    return (message.message_thread_id
            and message.reply_to_message
            and message.reply_to_message.forum_topic_created)


def is_non_topic_reply_to_bot(message):
    fix_caption_as_text(message)
    return (message.reply_to_message
            and not message.reply_to_message.forum_topic_created
            and message.reply_to_message.from_user.is_bot
            )


@bot.edited_message_handler(commands=['start'])
@bot.message_handler(commands=['start'])
def start_message(message):
    print(f"User started: {message.chat.id}")
    ui.send(message, f"Hello! I'll forward messages\nYour chat: `{message.chat.id}`",
            parse_mode="Markdown")
    ui.delete(message)


@bot.edited_message_handler(commands=["id"])
@bot.message_handler(commands=["id"])
def get_id(message):
    topic_id = None if not message.reply_to_message else message.reply_to_message.message_thread_id
    ui.send(message, f"`{str(topic_id)}`", message_thread_id=topic_id, parse_mode="Markdown")
    ui.delete(message)


@bot.edited_message_handler(commands=["pin"])
@bot.message_handler(commands=["pin"])
def pin(message):
    pin_or_edit(message, message.text.removeprefix("/pin").strip())
    ui.delete(message)


all_content = ['audio', 'photo', 'voice', 'video', 'document',
               'text', 'location', 'contact', 'sticker']

@bot.edited_message_handler(func=has_tag_to_forward, content_types=all_content)
@bot.message_handler(func=has_tag_to_forward, content_types=all_content)
def forward(message):
    if not (tag := extract_tag(message.text)): return
    is_new_topic, topic_id = get_or_create_topic(message, tag)

    if message.reply_to_message:
        forwarded = ui.copy(message.reply_to_message, message_thread_id=topic_id) # copy 1to1 reply message
        ui.delete(message.reply_to_message)
    else:
        new_text = re.sub(fr"\s*#{tag}\s*", "", message.text, re.RegexFlag.DOTALL) # remove tag from original
        forwarded = ui.copy(message, message_thread_id=topic_id)
        ui.edit(forwarded, new_text)

    if is_new_topic: ui.unpin(forwarded)
    ui.delete(message)

@bot.edited_message_handler(commands=["update"], func=is_topic)
@bot.message_handler(commands=["update"], func=is_topic)
def update_topic_id(message):
    topic_message = message.reply_to_message
    topic_id = topic_message.message_thread_id

    append_topic(message, message.text.removeprefix("/update").strip(), topic_id)
    ui.delete(message)


@bot.edited_message_handler(commands=["remove"], func=is_topic)
@bot.message_handler(commands=["remove"], func=is_topic)
def remove_current_topic_id(message):
    topic_message = message.reply_to_message
    topic_id = topic_message.message_thread_id

    rm_topic(message, topic_id)
    ui.delete(message)


@bot.edited_message_handler(func=is_topic, content_types=all_content)
@bot.message_handler(func=is_topic, content_types=all_content)
def sync_topic_mirror_message(message):
    topic_message = message.reply_to_message
    topic_id = topic_message.message_thread_id

    if topic_message.chat.title != topic_message.forum_topic_created.name:
        append_topic(message, topic_message.forum_topic_created.name, topic_id)

    if not message.forward_from_message_id:
        ui.send(message, message.text, message_thread_id=topic_id)
        ui.delete(message)


@bot.edited_message_handler(func=is_non_topic_reply_to_bot, content_types=all_content)
@bot.message_handler(func=is_non_topic_reply_to_bot, content_types=all_content)
def edit_on_reply(message):
    ui.edit(message.reply_to_message, message.text)
    ui.delete(message)


@bot.message_handler(func=lambda msg: True, content_types=all_content)
def debug(message):
    print(message.__dict__())


def rm_topic(message, topic_id):
    topics, compiled = get_topics(message)
    if topic_id not in topics.values(): return

    compiled = list(filter(lambda s: not s.endswith(str(topic_id)), compiled))
    pin_or_edit(message, "\n".join(compiled))


def append_topic(message, topic, id):
    if not topic: return
    topics, compiled = get_topics(message)
    if (topic, id) in topics.items():
        return

    compiled = list(filter(lambda s: not s.endswith(str(id)), compiled))
    compiled = compiled + [f"{topic} -> {id}"]
    pin_or_edit(message, "\n".join(compiled))


def pin_or_edit(message, text):
    chat = ui.get_chat(message)
    if not chat.pinned_message:
        new = ui.send(message, text)
        ui.pin(new)
    else:
        ui.edit(chat.pinned_message, text)


def get_topics(message):
    chat = ui.get_chat(message)
    if not chat: return {}, []

    pinned = chat.pinned_message
    if not pinned: return {}, []

    if " -> " not in pinned.text:
        ui.unpin(pinned)
        return get_topics(message)

    compiled = pinned.text.split("\n")
    return dict({(topic.split(" -> ")[0], int(topic.split(" -> ")[1])) for topic in compiled}), compiled


def get_or_create_topic(message, topic_name):
    if topic_name.lower() == message.chat.title.lower(): return False, None
    topics, _ = get_topics(message)
    if topic_name not in topics.keys():
        topic = ui.create_topic(message, topic_name)
        topic_id = topic.message_thread_id
        append_topic(message, topic_name, topic_id)
        return True, topic_id

    return False, topics[topic_name]


ui.start_blocking()
