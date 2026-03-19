import argparse
import logging
import re

from core_bots import Cfg, add_cfg_argument
from core_bots import TelegramBot

p = argparse.ArgumentParser(description="Topic Message Forwarder Bot")
add_cfg_argument(p)
cfg = Cfg.from_file(p.parse_args().config)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

bot = TelegramBot(cfg.token)
inner = bot.delegate


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


@inner.edited_message_handler(commands=['start'])
@inner.message_handler(commands=['start'])
def start_message(message):
    log.info(f"User started: {message.chat.id}")
    bot.send(message, f"Hello! I'll forward messages\nYour chat: `{message.chat.id}`",
             parse_mode="Markdown")
    bot.delete(message)


@inner.edited_message_handler(commands=["id"])
@inner.message_handler(commands=["id"])
def get_id(message):
    topic_id = None if not message.reply_to_message else message.reply_to_message.message_thread_id
    bot.send(message, f"`{str(topic_id)}`", message_thread_id=topic_id, parse_mode="Markdown")
    bot.delete(message)


@inner.edited_message_handler(commands=["pin"])
@inner.message_handler(commands=["pin"])
def pin(message):
    pin_or_edit(message, message.text.removeprefix("/pin").strip())
    bot.delete(message)


all_content = ['audio', 'photo', 'voice', 'video', 'document',
               'text', 'location', 'contact', 'sticker']

@inner.edited_message_handler(func=has_tag_to_forward, content_types=all_content)
@inner.message_handler(func=has_tag_to_forward, content_types=all_content)
def forward(message):
    if not (tag := extract_tag(message.text)): return
    is_new_topic, topic_id = get_or_create_topic(message, tag)

    if message.reply_to_message:
        forwarded = bot.copy(message.reply_to_message, message_thread_id=topic_id) # copy 1to1 reply message
        bot.delete(message.reply_to_message)
    else:
        new_text = re.sub(fr"\s*#{tag}\s*", "", message.text, re.RegexFlag.DOTALL) # remove tag from original
        forwarded = bot.copy(message, message_thread_id=topic_id)
        bot.edit(forwarded, new_text)

    if is_new_topic: bot.unpin(forwarded)
    bot.delete(message)

@inner.edited_message_handler(commands=["update"], func=is_topic)
@inner.message_handler(commands=["update"], func=is_topic)
def update_topic_id(message):
    topic_message = message.reply_to_message
    topic_id = topic_message.message_thread_id

    append_topic(message, message.text.removeprefix("/update").strip(), topic_id)
    bot.delete(message)


@inner.edited_message_handler(commands=["remove"], func=is_topic)
@inner.message_handler(commands=["remove"], func=is_topic)
def remove_current_topic_id(message):
    topic_message = message.reply_to_message
    topic_id = topic_message.message_thread_id

    rm_topic(message, topic_id)
    bot.delete(message)


@inner.edited_message_handler(func=is_topic, content_types=all_content)
@inner.message_handler(func=is_topic, content_types=all_content)
def sync_topic_mirror_message(message):
    topic_message = message.reply_to_message
    topic_id = topic_message.message_thread_id

    if topic_message.chat.title != topic_message.forum_topic_created.name:
        append_topic(message, topic_message.forum_topic_created.name, topic_id)

    if not message.forward_from_message_id:
        bot.send(message, message.text, message_thread_id=topic_id)
        bot.delete(message)


@inner.edited_message_handler(func=is_non_topic_reply_to_bot, content_types=all_content)
@inner.message_handler(func=is_non_topic_reply_to_bot, content_types=all_content)
def edit_on_reply(message):
    bot.edit(message.reply_to_message, message.text)
    bot.delete(message)


@inner.message_handler(func=lambda msg: True, content_types=all_content)
def debug(message):
    log.info(message.__dict__())


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
    chat = bot.get_chat(message)
    if not chat.pinned_message:
        new = bot.send(message, text)
        bot.pin(new)
    else:
        bot.edit(chat.pinned_message, text)


def get_topics(message):
    chat = bot.get_chat(message)
    if not chat: return {}, []

    pinned = chat.pinned_message
    if not pinned: return {}, []

    if " -> " not in pinned.text:
        bot.unpin(pinned)
        return get_topics(message)

    compiled = pinned.text.split("\n")
    return dict({(topic.split(" -> ")[0], int(topic.split(" -> ")[1])) for topic in compiled}), compiled


def get_or_create_topic(message, topic_name):
    if topic_name.lower() == message.chat.title.lower(): return False, None
    topics, _ = get_topics(message)
    if topic_name not in topics.keys():
        topic = bot.create_topic(message, topic_name)
        topic_id = topic.message_thread_id
        append_topic(message, topic_name, topic_id)
        return True, topic_id

    return False, topics[topic_name]


if __name__ == "__main__":
    bot.start_blocking()