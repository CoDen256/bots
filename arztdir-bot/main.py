import io
import json
import time
from datetime import datetime


import argparse
import datetime
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
service = ArztService(api, bot, cfg.check_pattern, cfg.check_interval, cfg.chat_id)


@bot.message_handler(commands=['start'])
def start_message(message):
    log.info(f"User started: {message.chat.id}")
    bot.reply(message,
             f"Hello! I'll notify you if there are available openings for ArztDirekt\nYour chat: `{message.chat.id}`")


@bot.message_handler(commands=['trigger'])
def trigger(message):
    service.poll_and_check(True)


@bot.message_handler(commands=['check'])
def check_message(message):
    data = api.get_categories()
    if not data:
        bot.reply(message, "No appointment categories available at the moment. 😟")
        return

    service.notify_appointments(data, "", "", True)


@bot.message_handler(commands=['check_raw'])
def fetch_raw_message(message):
    raw_data = api.get_raw_categories()
    file = io.BytesIO(json.dumps(raw_data).encode("utf-8"))
    file.name = "response.json"  # Set a filename for the file
    bot.send_document(message, file)


@bot.message_handler(commands=['latest'])
def latest(message):
    last = service.latest[:20]
    bot.reply(message, format_appointments(last, True), parse_mode="HTML")


@bot.message_handler(commands=['set_interval'])
def set_interval_message(message):
    # Extract interval from the message
    parts = message.text.split()
    if len(parts) != 2 or not parts[1].isdigit():
        bot.reply(message, "Usage: /set_interval <minutes>")
        return

    new_interval = int(parts[1])
    old_interval = service.interval
    service.interval = new_interval
    bot.reply(message, f"Interval set from `{old_interval}` -> `{new_interval}` minutes", parse_mode='Markdown')


@bot.message_handler(commands=['set_filter'])
def set_filter(message):
    parts = message.text.split()
    if len(parts) != 2:
        bot.reply(message, "Usage: /set_filter <pattern>")
        return

    pattern = parts[1]
    if pattern == "*": pattern = ""
    previous = service.pattern
    service.pattern = pattern
    bot.reply(message, f"Filter set from `{previous}` -> `{pattern}`", parse_mode='Markdown')


@bot.delegate.callback_query_handler(func=lambda call: True)
def callback_query(call):
    try:
        if call.data.startswith("a;"):
            _, id, patient, has_openings, name = tuple(call.data.split(";"))
            bot.answer_callback_query(call.id)
            #ui.send(f"{id}, {name}, {patient}, {has_openings}")
            if (name.endswith(".")): name = name + ".."
            patienttypes = {"k": "known", "b": "both", "n": "new", "u": "N/A"}
            appointment = Appointment(name, bool(int(has_openings)), "", patient, datetime.now(), id, datetime.now())
            service.select_for_reserve(appointment, f"<i><b>{appointment.name} ({patienttypes[appointment.patient]} patients)</b></i>",
                                       "")
        if call.data.startswith("o;"):
            bot.answer_callback_query(call.id)
            status, date, expiry, body = service.reserve(call.data)
            if status:
                bot.edit(call.message.message_id,
                    f"🔥 Successfully reserved!\n\n{pretty_datetime(date)}\n\nReservation expires: {pretty_precise_time(expiry)}", reply_markup=None
                         )
            else:
                bot.send(
                    f"‼️ Something went wrong when reserving\n\n{pretty_datetime(date)}\n\nTried to reserve until {pretty_precise_time(expiry)}\nResponse:{body}")
        if call.data.startswith("r;"):
            bot.answer_callback_query(call.id)
    except Exception as e:
        bot.error(f"Failed to answer callback {call.data}", e)


service.start()
time.sleep(0.1)
bot.start_blocking()

