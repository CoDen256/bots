import io
import json
from datetime import datetime

import pytz
import telebot
import requests
import time
from threading import Thread

BOT_TOKEN = "7763823252:AAHRToFwss4-dqbB-f-rzo9fEACefFNnPd8"
# Time interval for periodic checks (in seconds)
CHECK_INTERVAL = 600  # god forgive me for editing this global var, im so sorry
CHECK_PATTERN = "Psychiatrie: E. Müller"  # god forgive me for editing this global var, im so sorry
# User ID to notify (replace with the actual user ID or chat ID)
CHAT_ID = 283382228  #
LATEST = []


class Appointment:
    def __init__(self, name, hasOpenings, id, patient, sync: datetime, searchId):
        self.name = name
        self.hasOpenings = hasOpenings
        self.id = id
        self.patient = patient
        self.sync: datetime = sync
        self.searchId = searchId

    def __str__(self):
        pre = "✅" if self.hasOpenings else "❌"
        avail = "available" if self.hasOpenings else "not available"
        tz = pytz.timezone("Europe/Berlin")
        return f"{pre} {self.name} ({self.patient} patients) -> *{avail}* | as of {self.sync.astimezone(tz)}"

    def __repr__(self):
        return self.__str__()


class Opening:
    def __init__(self, name, date: datetime):
        self.name = name
        self.date = date

    def __str__(self):
        tz = pytz.timezone("Europe/Berlin")
        return f"{self.date.astimezone(tz)} - {self.name}"

    def __repr__(self):
        return self.__str__()


class HyApi:
    LOCALITIES = ["136244789462435842", "106154130175164417", "106154141269098497"]
    INSTANCE = "5e8d5ff3a6abce001906ae07"
    # The URL to check
    API_HOST = "https://onlinetermine.arzt-direkt.com"
    CATEGORY_ENDPOINT = "/api/appointment-category"
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
                        "catId": "", "insuranceType": "gkv"}

    def __init__(self):
        pass

    def get_raw_categories(self):
        e = HyApi.API_HOST + HyApi.CATEGORY_ENDPOINT
        print(f"Running {e}")
        response = requests.post(e, headers=HyApi.HEADERS,
                                 json=HyApi.CATEGORY_PAYLOAD)
        response.raise_for_status()  # Raise an exception for HTTP errors
        json = response.json()
        print(f"Got response: {json}")
        return json

    def get_appointments(self):
        try:
            data = self.get_raw_categories()["categories"][0]["appointmentTypes"]
            return list(
                map(lambda x: Appointment(x["name"]["de"], x["hasOpenings"], x["_id"], x["patientTargetDefault"],
                                          datetime.strptime(x["lastSync"], "%Y-%m-%dT%H:%M:%S.%fZ"),
                                          x["terminSucheIdent"]), data))
        except Exception as e:
            print(f"Error checking URL: {e}")
            raise e

    def get_raw_openings(self, id):
        e = HyApi.API_HOST + HyApi.OPENINGS_ENDPOINT.replace("{ident}", id)
        print(f"Running {e}")
        response = requests.get(e, headers=HyApi.HEADERS)
        response.raise_for_status()  # Raise an exception for HTTP errors
        json = response.json()
        print(f"Got response: {json}")
        return json

    def get_openings(self, id):
        try:
            data = self.get_raw_openings(id)["openings"]
            return list(map(lambda x: Opening(x["displayStringNames"],
                                              datetime.strptime(x["date"], "%Y-%m-%dT%H:%M:%S.%fZ"),
                                              ), data))
        except Exception as e:
            print(f"Error checking URL: {e}")
            raise e


# Telegram Bot Token
bot = telebot.TeleBot(BOT_TOKEN)
api = HyApi()


@bot.message_handler(commands=['start'])
def start_message(message):
    print(message.chat.id)
    bot.reply_to(message, "Hello! I'll notify you if there are available openings for Hygieia")


@bot.message_handler(commands=['check'])
def check_message(message):
    try:
        data = api.get_appointments()
        if data:
            joined = "\n".join(map(lambda x: str(x), data))
            bot.reply_to(message, f"These are all the openings:\n{joined}", parse_mode='Markdown')
            for d in data:
                try:
                    ops = api.get_openings(d.searchId)
                    bot.reply_to(message, f"These are all the openings for {d.name}:\n" + "\n".join(map(lambda x: str(x), ops)))
                except Exception as e:
                    bot.reply_to(message, f"Error while getting openings: {e}")
        else:
            bot.reply_to(message, "No openings available at the moment.")
    except Exception as e:
        bot.reply_to(message, f"Error while checking: {e}")


@bot.message_handler(commands=['check_raw'])
def check_raw_message(message):
    try:
        raw_data = api.get_raw_categories()
        file = io.BytesIO(json.dumps(raw_data).encode("utf-8"))
        file.name = "response.json"  # Set a filename for the file
        bot.send_document(message.chat.id, file)
    except Exception as e:
        bot.reply_to(message, f"Error while fetching raw data: {e}")


@bot.message_handler(commands=['latest'])
def latest(message):
    global LATEST
    try:
        last = LATEST[:10]
        joined = "\n".join(map(lambda x: str(x), last))
        bot.reply_to(message, joined)
    except Exception as e:
        bot.reply_to(message, f"Error while fetching raw data: {e}")


@bot.message_handler(commands=['trigger'])
def trigger(message):
    try:
        poll_and_check()
    except Exception as e:
        bot.reply_to(message, f"Error while fetching raw data: {e}")


@bot.message_handler(commands=['set_interval'])
def set_interval_message(message):
    global CHECK_INTERVAL
    try:
        # Extract interval from the message
        parts = message.text.split()
        if len(parts) != 2 or not parts[1].isdigit():
            bot.reply_to(message, "Usage: /set_interval <seconds>")
            return

        CHECK_INTERVAL = int(parts[1])
        bot.reply_to(message, f"Interval set to {CHECK_INTERVAL} seconds.")
    except Exception as e:
        bot.reply_to(message, f"Error while setting interval: {e}")


@bot.message_handler(commands=['set_filter'])
def set_filter(message):
    global CHECK_PATTERN
    try:
        # Extract interval from the message
        parts = message.text.split()
        if len(parts) != 2:
            bot.reply_to(message, "Usage: /set_filter <pattern>")
            return

        CHECK_PATTERN = parts[1]
        if CHECK_PATTERN == "*":
            CHECK_PATTERN = ""
        bot.reply_to(message, f"Filter set to `{CHECK_PATTERN}`.", parse_mode='Markdown')
    except Exception as e:
        bot.reply_to(message, f"Error while setting pattern: {e}")


def find_target(appointments, name):
    for a in appointments:
        if name in a.name:
            yield a


def poll_and_check():
    global CHECK_PATTERN, LATEST
    result = api.get_appointments()
    print(f"Got appointments {result} for {CHECK_PATTERN}")
    for a in find_target(result, CHECK_PATTERN):
        LATEST.append(a)
        if (a.hasOpenings):
            s = str(a).replace("_", "\\_")
            bot.send_message(CHAT_ID,
                             f"📅 There is an available opening !\n\n {s}\n\nhttps://www.hygieia.net/leipzig/terminvereinbarung/",
                             parse_mode='Markdown')
            ops = api.get_raw_openings(a.searchId)
            bot.send_message(CHAT_ID, "Openings:\n" + "\n".join(map(lambda x: str(x), ops)))


# Function to check the URL
def check_for_openings():
    global CHECK_INTERVAL
    while True:
        print(f"Checking at {datetime.now()}")
        poll_and_check()
        print(f"Next check in {CHECK_INTERVAL}s")
        time.sleep(CHECK_INTERVAL)


# Start the periodic check in a separate thread
Thread(target=check_for_openings, daemon=True).start()
# Polling for Telegram bot commands
print("Bot is running...")
bot.infinity_polling()
