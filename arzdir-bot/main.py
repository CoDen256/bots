import io
import json
import threading
from datetime import datetime, timedelta

import pytz
import telebot
import requests
import time

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = "7763823252:AAHRToFwss4-dqbB-f-rzo9fEACefFNnPd8"
CHECK_INTERVAL = 10
CHECK_PATTERN = ""  # check any
CHAT_ID = 283382228 # -1002193480523 # 283382228 #
TZ = pytz.timezone("Europe/Berlin")



def inutc(datetime):
    return datetime.astimezone(pytz.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def readable_precise_time(datetime):
    return str(datetime.astimezone(TZ).strftime("%d.%m.%y at %H:%M:%S"))

def readable_hours(datetime):
    return str(datetime.astimezone(TZ).strftime("%H:%M:%S"))

def readable_time(datetime):
    return str(datetime.astimezone(TZ).strftime("🗓️ %b %d, %Y 🕒 %H:%M"))


def format_appointment(appointment, queried=False):
    mark = "🟢" if appointment.has_openings else "🔴"
    body = ""
    body += f"Last synced:  {readable_precise_time(appointment.sync)}"
    if queried:
        body += f"\nLast queried: {readable_precise_time(appointment.updated)}"
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
        body += f"Last sync: {readable_precise_time(appointment.sync)}"
    if not openings and not sync:
        body += "..."

    return body


def format_opening(opening):
    return f"{readable_time(opening.date)}"


class Appointment:
    def __init__(self, name, has_openings, id, patient, sync: datetime, search_id, updated: datetime):
        self.name = name
        self.has_openings = has_openings
        self.id = id
        self.patient = patient
        self.sync: datetime = pytz.utc.localize(sync)
        self.updated = pytz.utc.localize(updated)
        self.search_id = search_id

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()


class Opening:
    def __init__(self, name, date: datetime, duration, doctor_ids, search_id):
        self.name = name
        self.date = pytz.utc.localize(date)
        self.duration = duration
        self.doctor_ids = doctor_ids
        self.search_id = search_id

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()


class TelegramUI:
    def __init__(self, chat_id, token):
        self.bot = telebot.TeleBot(token)
        self.chat_id = chat_id

    def start_blocking(self):
        # Polling for Telegram bot commands
        print("Bot is running...")
        self.bot.infinity_polling()

    def send(self, text, **kwargs):
        try:
            self.bot.send_message(self.chat_id, text, **kwargs)
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


class ArztService:
    def __init__(self, ui, pattern, interval):
        self.ui = ui
        self.pattern = pattern
        self.interval = interval
        self.latest = []
        self.reserves = []

    def set_filter(self, pattern):
        prev = self.pattern
        self.pattern = pattern
        return prev

    def start(self):
        threading.Thread(target=self.run_blocking, daemon=True).start()

    def run_blocking(self):
        while True:
            print(f"Check at {datetime.now()}")
            self.poll_and_check()
            print(f"Next check in {self.interval} min")
            time.sleep(self.interval * 60)

    def poll_and_check(self, log=False):
        result = api.get_categories()
        print(f"Got for {self.pattern if self.pattern else '*'} appointments: {result}")
        open = []
        for a in self.filter(result, self.pattern):
            self.latest.append(a)
            if a.has_openings:
                print(f"{a} has new openings")
                open.append(a)
            else:
                print(f"{a} has no openings")

        if not open:
            print("No available openings at all!")
            if log: self.ui.send("No available openings!")
            return
        self.notify_appointments(open, "📅 New available openings!",
                                 "\nhttps://www.hygieia.net/leipzig/terminvereinbarung/")

    def filter(self, appointments, pattern):
        for a in appointments:
            if pattern in a.name:
                yield a

    def get_openings_or_empty(self, appointment):
        try:
            print(f"Querying {appointment.name} openings")
            return api.get_openings(appointment.search_id)
        except Exception as e:
            print(f"Failed to get {appointment.name} openings")
            ui.error(f"Failed to get openings for {appointment.name}", e)
            return []

    def notify_appointments(self, appointments, header, footer, sync=False):
        body = ""
        markup = InlineKeyboardMarkup()
        markup.row_width = 1

        for appoint in appointments:
            body += "\n"
            body += format_openings(self.get_openings_or_empty(appoint), appoint, sync)
            if appoint.has_openings:
                if not appoint.patient: appoint.patient = "u"
                data = f"a;{appoint.search_id};{appoint.patient[0]};{int(appoint.has_openings)};{appoint.name}"
                if len(data) > 63:
                    data = data.replace("Dr. ", "").replace("med. ", "")[:62] + "."
                markup.add(InlineKeyboardButton(f"📒 ({appoint.patient[0].upper()}) {appoint.name}",callback_data=data))

        self.ui.send(
            f"{header}\n{body}\n{footer}",
            parse_mode='HTML',
            reply_markup=markup)

    def select_for_reserve(self, appointment, header, footer):
        markup = InlineKeyboardMarkup()
        markup.row_width = 1
        openings = self.get_openings_or_empty(appointment)
        for (search_id, date, expiry) in self.reserves:
            if search_id != appointment.search_id: continue
            if expiry < TZ.localize(datetime.now()): continue
            data = f"r;"
            markup.add(InlineKeyboardButton(f"{readable_hours(expiry)} 🔒 {readable_time(date)}",
                                            callback_data=data))

        for opening in openings:
            data = f"o;{opening.search_id};{','.join(opening.doctor_ids)};{int(int(opening.duration) / 5)};{inutc(opening.date)}"
            markup.add(InlineKeyboardButton(f"{readable_time(opening.date)}",
                                            callback_data=data[:-8]))  # ':00.000Z'

        self.ui.send(
            f"{header}\n\n{footer}",
            parse_mode='HTML',
            reply_markup=markup)

    def reserve(self, data):
        _, search_id, ids, duration, date = tuple(data.split(";"))
        date += ":00.000Z"
        duration = int(duration) * 5
        ids = ids.split(",")
        # ui.send(f"Opening {call.data}: \n {ids}, {search_id}, {duration}, {date}")
        status, expiry, json = api.reserve(ids, search_id, date, duration)# True, TZ.localize(datetime.now() + timedelta(minutes=1)), {}  # api.reserve(ids, search_id, date, duration) #
        date = pytz.utc.localize(datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ"))
        if status: self.reserves.append((search_id, date, expiry))

        return status, date, expiry, json

class ArztApi:
    LOCALITIES = ["94418895887138817", "94418856297627649", "94418877937614849", "136244910254196738",
                  "94418986358276097", "94418836904738817", "94418872331403265", "94418864488054785",
                  "94418868363591681", "94418891544985601", "136244761438717954", "94418842869563393",
                  "94418992644489217", "157028186179241986"]
    INSTANCE = "5e8d5ff3a6abce001906ae07"

    API_HOST = "https://onlinetermine.arzt-direkt.com"
    CATEGORY_ENDPOINT = "/api/appointment-category"
    RESERVE_ENDPOINT = "/api/reservation/reserve"
    OPENINGS_ENDPOINT = ("/api/opening?"
                         f"localityIds={','.join(LOCALITIES)}"
                         f"&instance={INSTANCE}"
                         "&terminSucheIdent={ident}"
                         "&forerunTime=0")

    HEADERS = {
        "accept": 'application/json, text/plain, */*',
        "content-type": 'application/json',
        'sec-ch-ua': '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "sec-ch-ua-mobile": '?0',
        "sec-ch-ua-platform": 'Windows"',
        "user-agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 '
                      'Safari/537.36 Edg/131.0.0.0'
    }

    CATEGORY_PAYLOAD = {"birthDate": None,
                        "localityIds": LOCALITIES,
                        "instance": INSTANCE,
                        "catId": "",
                        "insuranceType": "gkv"}

    def get_raw_categories(self):
        url = ArztApi.API_HOST + ArztApi.CATEGORY_ENDPOINT
        print(f"Running {url}")
        response = requests.post(url, headers=ArztApi.HEADERS, json=ArztApi.CATEGORY_PAYLOAD)
        response.raise_for_status()
        return response.json()

    def get_categories(self):
        try:
            data = self.get_raw_categories()["categories"][0]["appointmentTypes"]
            return list(map(lambda x: Appointment(
                x["name"]["de"],
                x["hasOpenings"],
                x["_id"],
                x["patientTargetDefault"],
                datetime.strptime(x["lastSync"], "%Y-%m-%dT%H:%M:%S.%fZ"),
                x["terminSucheIdent"],
                datetime.now()
            ), data)
                        )
        except Exception as e:
            print(f"Error checking categories: {e}")
            raise e

    def get_raw_openings(self, id):
        url = ArztApi.API_HOST + ArztApi.OPENINGS_ENDPOINT.replace("{ident}", id)
        print(f"Running {url}")
        response = requests.get(url, headers=ArztApi.HEADERS)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()

    def get_openings(self, id):
        try:
            data = self.get_raw_openings(id)["openings"]
            return list(map(lambda x:
                            Opening(
                                x["displayStringNames"],
                                datetime.strptime(x["date"], "%Y-%m-%dT%H:%M:%S.%fZ"),
                                x["duration"],
                                list(map(lambda s: s["kid"], x["kdSet"])),
                                id
                            ),
                            data)
                        )
        except Exception as e:
            print(f"Error checking openings: {e}")
            raise e

    def reserve(self, doctors, id, date, duration):
        url = ArztApi.API_HOST + ArztApi.RESERVE_ENDPOINT
        print(f"Running {url}")
        expires = datetime.now() + timedelta(minutes=15)
        data = {"instance": ArztApi.INSTANCE,
                "terminSucheIdent": id,
                "dateAppointment": date,
                "duration": int(duration),
                "dateExpiry": inutc(expires),
                "doctorIds": doctors}
        response = requests.post(url, headers=ArztApi.HEADERS, json=data)
        if response.status_code == 200:
            try:
                expires = datetime.strptime(response.json()["reservation"]["dateExpiry"], "%Y-%m-%dT%H:%M:%S.%fZ")
                expires = pytz.utc.localize(expires)
                return True, expires, response.json()
            except Exception as e:
                print(f"Cant parse expiry date {e}")
                return False, expires, response.json()
        return False, expires, response.json()


# Telegram Bot Token
ui = TelegramUI(CHAT_ID, BOT_TOKEN)
bot = ui.bot
api = ArztApi()
service = ArztService(ui, CHECK_PATTERN, CHECK_INTERVAL)


@bot.message_handler(commands=['start'])
def start_message(message):
    print(f"User started: {message.chat.id}")
    ui.reply(message,
             f"Hello! I'll notify you if there are available openings for ArztDirect\nYour chat: {message.chat.id}")


@bot.message_handler(commands=['trigger'])
def trigger(message):
    try:
        service.poll_and_check(True)
    except Exception as e:
        ui.error(f"Triggering failed", e)


@bot.message_handler(commands=['check'])
def check_message(message):
    try:
        data = api.get_categories()
        if not data:
            ui.reply(message, "No appointment categories available at the moment. 😟")
            return

        service.notify_appointments(data, "", "", True)
    except Exception as e:
        ui.error(f"Checking failed", e)


@bot.message_handler(commands=['check_raw'])
def check_raw_message(message):
    try:
        raw_data = api.get_raw_categories()
        file = io.BytesIO(json.dumps(raw_data).encode("utf-8"))
        file.name = "response.json"  # Set a filename for the file
        bot.send_document(message.chat.id, file)
    except Exception as e:
        ui.error(f"Fetching raw data failed", e)


@bot.message_handler(commands=['latest'])
def latest(message):
    try:
        last = service.latest[:20]
        ui.reply(message, format_appointments(last, True), parse_mode="HTML")
    except Exception as e:
        ui.error(f"Fetching latest failed", e)


@bot.message_handler(commands=['set_interval'])
def set_interval_message(message):
    try:
        # Extract interval from the message
        parts = message.text.split()
        if len(parts) != 2 or not parts[1].isdigit():
            ui.reply(message, "Usage: /set_interval <minutes>")
            return

        new_interval = int(parts[1])
        old_interval = service.interval
        service.interval = new_interval
        ui.reply(message, f"Interval set from `{old_interval}` -> `{new_interval}` minutes", parse_mode='Markdown')
    except Exception as e:
        ui.error(f"Setting interval failed", e)


@bot.message_handler(commands=['set_filter'])
def set_filter(message):
    try:
        # Extract interval from the message
        parts = message.text.split()
        if len(parts) != 2:
            ui.reply(message, "Usage: /set_filter <pattern>")
            return

        pattern = parts[1]
        if pattern == "*": pattern = ""
        previous = service.pattern
        service.pattern = pattern
        ui.reply(message, f"Filter set from `{previous}` -> `{pattern}`", parse_mode='Markdown')
    except Exception as e:
        ui.error(f"Setting pattern failed", e)


@bot.callback_query_handler(func=lambda call: True)
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
                ui.edit(call.message.message_id,
                    f"🔥 Successfully reserved!\n\n{readable_time(date)}\n\nReservation expires: {readable_precise_time(expiry)}", reply_markup=None
                )
            else:
                ui.send(
                    f"‼️ Something went wrong when reserving\n\n{readable_time(date)}\n\nTried to reserve until {readable_precise_time(expiry)}\nResponse:{body}")
        if call.data.startswith("r;"):
            bot.answer_callback_query(call.id)
    except Exception as e:
        ui.error(f"Failed to answer callback {call.data}", e)


service.start()
time.sleep(0.1)
ui.start_blocking()

