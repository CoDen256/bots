import logging
import threading
import pytz
import time

from datetime import datetime
from core_bots import pretty_time, pretty_precise_time, pretty_datetime, CET
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

log = logging.getLogger(__name__)

class ArztService:
    def __init__(self, api, bot, pattern, interval, chat):
        self.api = api
        self.bot = bot
        self.pattern = pattern
        self.interval = interval
        self.chat = chat
        self.latest = []
        self.reserves = []

    def get_and_set_filter(self, pattern):
        prev = self.pattern
        self.pattern = pattern
        return prev

    def start(self):
        threading.Thread(target=self.run_blocking, daemon=True).start()

    def run_blocking(self):
        while True:
            log.info(f"Check at {datetime.now()}")
            self.poll_and_check()
            log.info(f"Next check in {self.interval} min")
            time.sleep(self.interval * 60)

    def poll_and_check(self, notify_empty=False):
        result = self.api.get_categories()
        log.info(f"Got for {self.pattern if self.pattern else '*'} appointments: {result}")
        open = []
        for a in self.filter(result, self.pattern):
            self.latest.append(a)
            if a.has_openings:
                log.info(f"{a} has new openings")
                open.append(a)
            else:
                log.info(f"{a} has no openings")

        if not open:
            log.warning("No available openings at all!")
            if notify_empty: self.bot.send_to_chat(self.chat, "No available openings!")
            return
        self.notify_appointments(open, "📅 New available openings!",
                                 "\nhttps://www.hygieia.net/leipzig/terminvereinbarung/")

    def filter(self, appointments, pattern):
        for a in appointments:
            if pattern in a.name:
                yield a

    def get_openings_or_empty(self, appointment):
        try:
            log.info(f"Querying {appointment.name} openings")
            return self.api.get_openings(appointment.search_id)
        except Exception as e:
            log.error(f"Failed to get {appointment.name} openings")
            self.bot.error_to_chat(self.chat, f"Failed to get openings for {appointment.name}", e)
            return []

    def notify_appointments(self, appointments, header, footer, sync=False):
        body = ""
        markup = InlineKeyboardMarkup()
        markup.row_width = 1

        for appoint in appointments:
            body += "\n"
            body += format_openings(self.get_openings_or_empty(appoint)[:5], appoint, sync)
            if appoint.has_openings:
                if not appoint.patient: appoint.patient = "u"
                data = f"a;{appoint.search_id};{appoint.patient[0]};{int(appoint.has_openings)};{appoint.name}"
                if len(data) > 63:
                    data = data.replace("Dr. ", "").replace("med. ", "")[:62] + "."
                markup.add(InlineKeyboardButton(f"📒 ({appoint.patient[0].upper()}) {appoint.name}",callback_data=data))

        self.bot.send_to_chat(
            self.chat,
            f"{header}\n{body}\n{footer}",
            parse_mode='HTML',
            reply_markup=markup)

    def select_for_reserve(self, appointment, header, footer):
        markup = InlineKeyboardMarkup()
        markup.row_width = 1
        openings = self.get_openings_or_empty(appointment)
        for (search_id, date, expiry) in self.reserves:
            if search_id != appointment.search_id: continue
            if expiry < CET.localize(datetime.now()): continue
            data = f"r;"
            markup.add(InlineKeyboardButton(f"{pretty_time(expiry)} 🔒 {pretty_datetime(date)}",
                                            callback_data=data))

        for opening in openings[:15]:
            data = f"o;{opening.search_id};{','.join(opening.doctor_ids)};{int(int(opening.duration) / 5)};{inutc(opening.date)}"
            markup.add(InlineKeyboardButton(f"{pretty_datetime(opening.date)}",
                                            callback_data=data[:-8]))  # ':00.000Z'

        self.bot.send_to_chat(
            self.chat,
            f"{header}\n\n{footer}",
            parse_mode='HTML',
            reply_markup=markup)

    def reserve(self, data):
        _, search_id, ids, duration, date = tuple(data.split(";"))
        date += ":00.000Z"
        duration = int(duration) * 5
        ids = ids.split(",")
        # self.bot.send(f"Opening {call.data}: \n {ids}, {search_id}, {duration}, {date}")
        status, expiry, json = self.api.reserve(ids, search_id, date, duration)# True, TZ.localize(datetime.now() + timedelta(minutes=1)), {}  # api.reserve(ids, search_id, date, duration) #
        date = pytz.utc.localize(datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ"))
        if status: self.reserves.append((search_id, date, expiry))

        return status, date, expiry, json


def format_appointment(appointment, queried=False):
    mark = "🟢" if appointment.has_openings else "🔴"
    body = ""
    body += f"Last synced:  {pretty_precise_time(appointment.sync)}"
    if queried:
        body += f"\nLast queried: {pretty_precise_time(appointment.updated)}"
    if not appointment.patient: appointment.patient = "u"
    return f'<pre><code class="language-{mark} ({appointment.patient[0].upper()}) {appointment.name}">{body}</code></pre>'


def format_appointments(appointments, queried=False):
    return "\n".join(map(lambda x: format_appointment(x, queried), appointments))


def format_openings(openings, appointment, sync=False):
    mark = "🟢" if appointment.has_openings else "🔴"

    body = format_openings_if_present(openings, appointment, sync)
    return f'<pre><code class="language-{mark} ({appointment.patient[0].upper()}) {appointment.name}">{body}</code></pre>'


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


def format_opening(opening):
    return f"{pretty_datetime(opening.date)}"

def inutc(datetime):
    return datetime.astimezone(pytz.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
