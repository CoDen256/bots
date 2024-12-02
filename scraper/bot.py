import io
import json
import pprint
from datetime import datetime
from idlelib.parenmatch import CHECK_DELAY

import telebot
import requests
import time
from threading import Thread

BOT_TOKEN = "7763823252:AAHRToFwss4-dqbB-f-rzo9fEACefFNnPd8"
# Time interval for periodic checks (in seconds)
CHECK_INTERVAL = 160  # god forgive me for editing this global var, im so sorry
# User ID to notify (replace with the actual user ID or chat ID)
CHAT_ID = 283382228


class Appointment:
    def __init__(self, name, hasOpenings, id):
        self.name = name
        self.hasOpenings = hasOpenings
        self.id = id

    def __str__(self):
        pre = "✅" if self.hasOpenings else "❌"
        avail = "available" if self.hasOpenings else "not available"
        return f"{pre} {self.name} -> *{avail}*"

    def __repr__(self):
        return self.__str__()


class HyApi:
    # The URL to check
    API_HOST = "https://onlinetermine.arzt-direkt.com"
    CATEGORY_ENDPOINT = "/api/appointment-category"
    HEADERS = {
        "accept": 'application/json, text/plain, */*',
        "content-type": 'application/json',
        "referer": 'sec-ch-ua: "Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "sec-ch-ua-mobile": '?0',
        "sec-ch-ua-platform": 'Windows"',
        "user-agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 '
                      'Safari/537.36 Edg/131.0.0.0'
    }

    CATEGORY_PAYLOAD = {"birthDate":None,
                        "localityIds":["136244789462435842","106154130175164417","106154141269098497"],
                        "instance":"5e8d5ff3a6abce001906ae07","catId":"","insuranceType":"gkv"}


    def __init__(self):
        pass

    def get_raw_categories(self):
        response = requests.post(HyApi.API_HOST + HyApi.CATEGORY_ENDPOINT, headers=HyApi.HEADERS,json = HyApi.CATEGORY_PAYLOAD)
        response.raise_for_status()  # Raise an exception for HTTP errors
        json = response.json()
        print(f"Got response: {json}")
        return json

    def get_appointments(self):
        try:
            data = self.get_raw_categories()["categories"][0]["appointmentTypes"]
            return list(map(lambda x: Appointment(x["name"]["de"], x["hasOpenings"], x["_id"]), data))
        except Exception as e:
            print(f"Error checking URL: {e}")
            raise e


# Telegram Bot Token
bot = telebot.TeleBot(BOT_TOKEN)
api = HyApi()


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.reply_to(message, "Hello! I'll notify you if there are available openings for Hygieia")


@bot.message_handler(commands=['check'])
def start_message(message):
    try:
        data = api.get_appointments()
        if data:
            joined = "\n".join(map(lambda x: str(x), data))
            bot.reply_to(message, f"These are all the openings:\n{joined}", parse_mode='Markdown')
        else:
            bot.reply_to(message, "No openings available at the moment.")
    except Exception as e:
        bot.reply_to(message, f"Error while checking: {e}")


@bot.message_handler(commands=['check_raw'])
def start_message(message):
    try:
        raw_data = api.get_raw_categories()
        file = io.BytesIO(json.dumps(raw_data).encode("utf-8"))
        file.name = "response.json"  # Set a filename for the file
        bot.send_document(message.chat.id, file)
    except Exception as e:
        bot.reply_to(message, f"Error while fetching raw data: {e}")


@bot.message_handler(commands=['set_interval'])
def start_message(message):
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


def find_target(appointments, name):
    for a in appointments:
        if name in a.name:
            yield a


def poll_and_check():
    result = api.get_appointments()
    print(f"Got appointments {result}")
    for a in find_target(result, "Psychiatrie: E. Müller"):
        if (not a.hasOpenings):
            bot.send_message(CHAT_ID, f"📅 There is an available opening !\n\n {a}", parse_mode='Markdown')


# Function to check the URL
def check_for_openings():
    while True:
        print(f"Checking at {datetime.now()}")
        poll_and_check()
        print(f"Next check in {CHECK_DELAY}s")
        time.sleep(CHECK_INTERVAL)


# Start the periodic check in a separate thread
Thread(target=check_for_openings, daemon=True).start()
# Polling for Telegram bot commands
print("Bot is running...")
bot.infinity_polling()
