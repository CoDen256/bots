import io
import json
import time
from datetime import datetime

import argparse
import logging

from core_bots import add_cfg_argument, Cfg, TelegramBot, pretty_datetime, pretty_time, pretty_precise_time
from arztdir import ArztApi, Appointment, Opening
from service import ArztService, format_appointments

p = argparse.ArgumentParser(description="Topic Message Forwarder Bot")
add_cfg_argument(p)
cfg = Cfg.from_file(p.parse_args().config)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

bot = TelegramBot(cfg.token)
api = ArztApi()
service = ArztService(api, bot, cfg.check_pattern, cfg.check_interval)


@bot.message_handler(commands=['start'])
def start(message):
    log.info(f"User started: {message.chat.id}")
    bot.reply(message,
              f"Hello! I'll notify you if there are available openings for Arzt-Direkt\nYour chat: `{message.chat.id}`",
              parse_mode='Markdown')


@bot.message_handler(commands=['subscribe'])
def subscribe(message):
    log.info(f"Chat subscribed: {message.chat.id}")
    service.subscribers.add(message.chat.id)
    bot.reply(message,
              f"🔔 Your chat was subscribed for Arzt-Direkt notifications: `{message.chat.id}`", parse_mode='Markdown')


@bot.message_handler(commands=['unsubscribe'])
def unsubscribe(message):
    log.info(f"Chat unsubscribed: {message.chat.id}")
    service.subscribers.remove(message.chat.id)
    bot.reply(message,
              f"🔕 Your chat was unsubscribed from Arzt-Direkt notifications: `{message.chat.id}`",
              parse_mode='Markdown')


@bot.message_handler(commands=['trigger'])
def trigger(message):
    log.info(f"Triggered by: {message.chat.id}")
    service.poll_and_check(message)


@bot.message_handler(commands=['check'])
def check(message):
    log.info(f"Check all by: {message.chat.id}")
    service.check_all(message)


@bot.message_handler(commands=['check_raw'])
def check_raw(message):
    log.info(f"Check raw by: {message.chat.id}")

    raw_data = api.get_raw_categories()
    file = io.BytesIO(json.dumps(raw_data).encode("utf-8"))
    file.name = "response.json"  # Set a filename for the file
    bot.send_document(message, file)


@bot.message_handler(commands=['latest'])
def latest(message):
    log.info(f"Get latest raw by: {message.chat.id}")

    last = service.latest[:20]
    bot.reply(message, format_appointments(last, True), parse_mode="HTML")


@bot.message_handler(commands=['interval'])
def interval(message):
    log.info(f"Set interval by: {message.chat.id}: {message.text}")

    # Extract interval from the message
    parts = message.text.split()
    if len(parts) != 2 or not parts[1].isdigit():
        bot.reply(message, "Usage: /interval <minutes>")
        return

    new_interval = int(parts[1])
    old_interval = service.get_and_set_interval(new_interval)
    bot.reply(message, f"Interval set from `{old_interval}` -> `{new_interval}` minutes", parse_mode='Markdown')


@bot.message_handler(commands=['filter'])
def filter(message):
    log.info(f"Set filter by: {message.chat.id}: {message.text}")

    parts = message.text.split(sep=' ', maxsplit=1)
    if len(parts) != 2:
        bot.reply(message, "Usage: /filter <regex_pattern>")
        return

    pattern = parts[1]
    previous = service.get_and_set_filter(pattern)
    bot.reply(message, f"Filter set from `{previous}` -> `{pattern}`", parse_mode='Markdown')

@bot.message_handler(commands=['patients'])
def patients(message):
    log.info(f"Set patients by: {message.chat.id}: {message.text}")

    parts = message.text.split(sep=' ', maxsplit=1)
    if len(parts) != 2 or parts[1] not in ["both", "new", "known"]:
        bot.reply(message, "Usage: /patients both|new|known")
        return

    type = parts[1]
    previous = service.get_and_set_patient(type)
    bot.reply(message, f"Patient type filter set from `{previous}` -> `{type}`", parse_mode='Markdown')


@bot.callback_query_handler(func=lambda call: call.data.startswith("a;"))
def callback_select_for_reserve(call):
    bot.answer_callback_query(call.id)
    _, id, patient, has_openings, name = tuple(call.data.split(";"))
    if name.endswith("."): name = name + ".."
    patienttypes = {"k": "known", "b": "both", "n": "new", "u": "N/A"}
    appointment = Appointment(name, bool(int(has_openings)), "", patient, datetime.now(), id, datetime.now())
    service.select_for_reserve(call.message, appointment,
                               f"<i><b>{appointment.name} ({patienttypes[appointment.patient]} patients)</b></i>",
                               "")


@bot.callback_query_handler(func=lambda call: call.data.startswith("o;"))
def callback_reserve_opening(call):
    bot.answer_callback_query(call.id)
    _, search_id, ids, duration, date = tuple(call.data.split(";"))
    date += ":00.000Z"
    duration = int(duration) * 5
    ids = ids.split(",")
    service.reserve(call.message, search_id, ids, duration, date)


@bot.callback_query_handler(func=lambda call: call.data.startswith("r;"))
def callback_reserved_slot_selected(call):
    bot.answer_callback_query(call.id)


service.start()
time.sleep(0.1)
bot.start_blocking()
