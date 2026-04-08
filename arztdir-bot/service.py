import logging
import re
import threading
from typing import List

import pytz
import time

from datetime import datetime
from core_bots import pretty_time, pretty_precise_time, pretty_datetime, CET
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, LinkPreviewOptions

from arztdir import OpeningRequest, Appointment

log = logging.getLogger(__name__)


class ArztService:
    def __init__(self, api, bot, pattern, interval):
        self.api = api
        self.bot = bot
        self.pattern = pattern
        self.interval = interval
        self.subscribers = set()
        self.categories = set()
        self.latest = []
        self.reserves = []

    def start(self):
        threading.Thread(target=self.run_blocking, daemon=True).start()

    def run_blocking(self):
        while True:
            log.info(f"Check at {datetime.now()}")
            if self.subscribers:
                self.poll_and_check()
            else:
                log.warning("No subscribers, skipping")
            log.info(f"Next check in {self.interval} min")
            time.sleep(self.interval * 60)

    def get_and_set_filter(self, pattern):
        prev = self.pattern
        self.pattern = pattern
        return prev

    def get_and_set_interval(self, interval):
        prev = self.interval
        self.interval = interval
        return prev

    def select_categories(self, message, selected=None):
        if selected and selected not in self.categories:
            log.info(f"Added category {selected}")
            self.categories.add(selected)
        elif selected and selected in self.categories:
            log.info(f"Removed category {selected}")
            self.categories.remove(selected)

        markup = InlineKeyboardMarkup()
        markup.row_width = 1
        categories = self.api.get_categories()

        body = "🗂️ Select categories to monitor"

        for category in categories:
            data = f"c;{category.name}"[:63]
            cat_present = category.name[:61] in self.categories
            tag = "✅" if cat_present else "◻"
            log.info(f"Category: {category.name} is in {self.categories} - {cat_present}")
            markup.add(InlineKeyboardButton(f"{tag} {category.name}", callback_data=data))

        if not selected:
            self.bot.send(message, body, parse_mode="Markdown", reply_markup=markup)
            return

        self.bot.edit(message, body, reply_markup=markup)

    def poll_and_check(self, message=None):
        categories = self.api.get_categories()
        log.info(f"Filtering with for {self.pattern} following appointments: {categories}")
        open = []
        filtered = list(self.filter(categories))
        self.latest = filtered + self.latest
        for a in filtered:
            if a.has_openings:
                log.info(f"{a} has new openings")
                open.append(a)
            else:
                log.info(f"{a} has no openings")

        if not open:
            log.warning("No available openings at all!")
            if message: self.notify_empty(message, filtered)
            return
        self.notify_appointments(message, filtered, "📅 New available openings!",
                                 "\nhttps://app.arzt-direkt.de/hygieia-leipzig/booking")

    def notify_empty(self, message, filtered):
        body = format_appointments_plain(filtered)
        self.bot.send(message, f"😔 No available openings for appointments matching `{self.pattern}` in {[c for c in self.categories]}: \n\n" + body)

    def filter(self, categories):
        for c in categories:
            if c.name not in self.categories: continue
            for a in c.appointments:
                if re.match(self.pattern, a.full_name):
                    yield a

    def get_openings_or_empty(self, message, opening_request: OpeningRequest):
        try:
            log.info(f"Querying {opening_request.appointment_name} openings")
            return self.api.get_openings(opening_request.search_id)
        except Exception as e:
            log.error(f"Failed to get {opening_request.appointment_name} openings")
            self.bot.error(message, f"Failed to get openings for {opening_request.appointment_name}", e)
            return []

    def check_all(self, message):
        data = self.api.get_categories()
        if not data:
            self.bot.reply(message, "No appointment categories available at the moment. 😟")
            return

        for category in data:
            self.notify_appointments(message, category.appointments, category.name, "", True)

    def notify_appointments(self, message, appointments: List[Appointment], header, footer, include_sync_time=False):
        body = ""
        markup = InlineKeyboardMarkup()
        markup.row_width = 1

        for appoint in appointments:
            body += "\n"
            openings = self.get_openings_or_empty(message, appoint.create_opening_request())[:10]
            body += format_openings(openings, appoint, include_sync_time)
            if appoint.has_openings:
                data = f"a;{appoint.search_id};{int(appoint.has_openings)};{appoint.full_name}"
                if len(data) > 63: data = data[:62] + "."
                markup.add(InlineKeyboardButton(f"🧑‍⚕️ {appoint.name}", callback_data=data))

        text = f"{header}\n{body}\n{footer}"
        if message:
            self.bot.send(message, text, parse_mode='HTML', reply_markup=markup, link_preview_options=LinkPreviewOptions(is_disabled=True))
            return

        for chat in self.subscribers:
            self.bot.send_to_chat(chat, text, parse_mode='HTML', reply_markup=markup, link_preview_options=LinkPreviewOptions(is_disabled=True))

    def select_for_reserve(self, message, opening_request: OpeningRequest, header, footer):
        markup = InlineKeyboardMarkup()
        markup.row_width = 1
        openings = self.get_openings_or_empty(message, opening_request)
        for (search_id, date, expiry) in self.reserves:
            if search_id != opening_request.search_id: continue
            if expiry < CET.localize(datetime.now()): continue
            data = f"r;"
            markup.add(InlineKeyboardButton(f"{pretty_time(expiry)} 🔒 {pretty_datetime(date)}",
                                            callback_data=data))

        for opening in openings[:15]:
            data = f"o;{opening.search_id};{','.join(opening.doctor_ids)};{int(int(opening.duration) / 5)};{inutc(opening.date)}"
            markup.add(InlineKeyboardButton(f"{pretty_datetime(opening.date)}", callback_data=data[:-8]))  # ':00.000Z'

        self.bot.send(message, f"{header}\n\n{footer}", parse_mode='HTML', reply_markup=markup)

    def reserve(self, message, search_id, ids, duration, date):
        status, expiry, json = self.api.reserve(ids, search_id, date, duration)
        date = pytz.utc.localize(datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ"))
        if status: self.reserves.append((search_id, date, expiry))

        if status:
            self.bot.edit(message,
                          f"🔥 Successfully reserved!\n\n"
                          f"{pretty_datetime(date)}\n\n"
                          f"Reservation expires: {pretty_precise_time(expiry)}",
                          reply_markup=None
                          )
        else:
            self.bot.send(message,
                          f"‼️ Something went wrong when reserving\n\n"
                          f"{pretty_datetime(date)}\n\n"
                          f"Tried to reserve until {pretty_precise_time(expiry)}\n"
                          f"Response:{json}")


def format_appointment(appointment, queried=False):
    mark = appointment_tag(appointment)
    body = ""
    body += f"Last synced:  {pretty_precise_time(appointment.sync)}"
    if queried:
        body += f"\nLast queried: {pretty_precise_time(appointment.updated)}"
    return f'<pre><code class="language-{mark} {appointment.full_name}">{body}</code></pre>'


def format_appointments(appointments, queried=False):
    return "\n".join(map(lambda x: format_appointment(x, queried), appointments))

def format_appointment_plain(appointment):
    mark = appointment_tag(appointment)
    return f'{mark} {appointment.full_name}'

def format_appointments_plain(appointments):
    return "\n".join(map(lambda x: format_appointment_plain(x), appointments))

def format_openings(openings, appointment, sync=False):
    mark = appointment_tag(appointment)

    body = format_openings_if_present(openings, appointment, sync)
    return f'<pre><code class="language-{mark} {appointment.full_name}">{body}</code></pre>'

def format_openings_if_present(openings, appointment, sync):
    body = ""

    if not openings and appointment.has_openings:
        body += "--😮 no openings found --"
    if openings:
        body += "\n".join(list(map(format_opening, openings)))
    if sync:
        if openings:
            body += "\n\n"
        body += f"Last sync: {pretty_precise_time(appointment.sync)}"
    if not openings and not sync:
        body += "..."

    return body


def appointment_tag(appointment):
    return "🟢" if appointment.has_openings else "🔴"

def format_opening(opening):
    return f"{pretty_datetime(opening.date)}"


def inutc(datetime):
    return datetime.astimezone(pytz.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
