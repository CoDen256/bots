import io
import json
import threading
from datetime import datetime, timedelta
from dataclasses import dataclass, field

import pytz
import telebot
import requests
import time

import configparser

parser = configparser.RawConfigParser()
parser.read("bot.ini")
cfg = parser["main"]
BOT_TOKEN = cfg["token"]
CHAT_ID = int(cfg["chat"])
CHECK_INTERVAL = 5
TZ = pytz.timezone("Europe/Berlin")



def inutc(datetime):
    return datetime.astimezone(pytz.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def readable_precise_time(datetime):
    return str(datetime.astimezone(TZ).strftime("%d.%m.%y at %H:%M:%S"))

def readable_hours(datetime):
    return str(datetime.astimezone(TZ).strftime("%H:%M:%S"))

def readable_time(datetime):
    return str(datetime.astimezone(TZ).strftime("🗓️ %b %d, %Y 🕒 %H:%M"))

def format_vouchers(vouchers):

    body = list(map(format_voucher, sorted(vouchers,key=lambda x: x.price)))
    b = "\n".join(body)
    return f'{b}'

def format_voucher(opening):
    return f"{opening.price} Euro - [{opening.name}]({opening.url})"

@dataclass(unsafe_hash=True)
class Voucher:
    name: str = field(hash=True)
    id: str = field(hash=True)
    price: str = field(hash=True)
    brand: str = field(hash=True)
    url: str = field(hash=True)
    created: datetime = field(hash=True)
    updated: datetime = field(hash=True)
    queried: datetime = field(hash=False,compare=False)



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


class VoucherService:
    def __init__(self, ui, interval):
        self.ui = ui
        self.interval = interval
        self.checked = []

    def start(self):
        threading.Thread(target=self.run_blocking, daemon=True).start()

    def run_blocking(self):
        while True:
            print(f"Check at {datetime.now()}")
            self.poll_and_check()
            print(f"Next check in {self.interval} min")
            time.sleep(self.interval * 60)

    def is_same(self, a, b):
        return a == b

    def poll_and_check(self, force=False):
        targets = api.get_best_targets()
        products = hapi.get_products()
        total = targets + products
        print(f"Got {len(total)} vouchers: {total}")
        prev = self.checked
        same = self.is_same(total, prev)
        if same and not force:
            print("All the same, skip")
            return # self.is_same(total, list(map(lambda x: Voucher(name=x.name,id=x.id,price=x.price,brand=x.brand,url=x.url,created=x.created,updated=x.updated,queried=x.queried),total))+[])
        self.checked = total
        print("Got new ones!")
        res = format_vouchers(total)

        self.ui.send(
            f"{'Same old' if same else 'New'} vouchers:\n\n{res}",
            parse_mode='Markdown')


class OaHostelsApi:

    API_HOST = "https://www.aohostels.com"
    ONLINESHOP_ENDPOINT = '/en/shop-data/products/'
    PAYLOAD =  {"category": "all"}

    HEADERS = {
        "accept": 'application/json, text/plain, */*',
        "content-type": 'application/json',
        'sec-ch-ua': '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "sec-ch-ua-mobile": '?0',
        "sec-ch-ua-platform": 'Windows"',
        "user-agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 '
                      'Safari/537.36 Edg/131.0.0.0'
    }


    def get_raw_products(self):
        url = OaHostelsApi.API_HOST + OaHostelsApi.ONLINESHOP_ENDPOINT
        print(f"Running {url}")
        response = requests.post(url, headers=OaHostelsApi.HEADERS, json=OaHostelsApi.PAYLOAD)
        response.raise_for_status()
        return response.json()

    def get_products(self):
        response = None
        try:
            obj = self.get_raw_products()
            obj = obj["products"]
            query = TZ.localize(datetime.now())
            return list(map(lambda o:
                            Voucher(
                                name = o["language"]["title"],
                                brand =  o["name"],
                                id = o["id"],
                                price = o["price"],
                                url = f"https://www.aohostels.com/en/shop/detail/{o['language']['url']}",
                                updated = TZ.localize(datetime.strptime(o["created_at"], "%Y-%m-%d %H:%M:%S")),
                                created = TZ.localize(datetime.strptime(o["updated_at"], "%Y-%m-%d %H:%M:%S")),
                                queried = query
                            ), obj
                            ))
        except Exception as e:
            print(f"Error checking targets: {e},\n {response}")
            return []

class WonderlandApi:

    API_HOST = "https://www.voucherwonderland.com"
    BEST_TARGETS_ENDPOINT = "/beliebte-reiseziele?p=1&o=3&n=24&max=115.00&max-filter-2=3"

    HEADERS = {
        "accept": 'application/json, text/plain, */*',
        "content-type": 'application/json',
        'sec-ch-ua': '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "sec-ch-ua-mobile": '?0',
        "sec-ch-ua-platform": 'Windows"',
        "user-agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 '
                      'Safari/537.36 Edg/131.0.0.0'
    }


    def get_raw_best_targets(self):
        url = WonderlandApi.API_HOST + WonderlandApi.BEST_TARGETS_ENDPOINT
        print(f"Running {url}")
        response = requests.get(url, headers=WonderlandApi.HEADERS)
        response.raise_for_status()
        return response.text

    def get_best_targets(self):
        response = None
        try:
            targets = api.get_raw_best_targets()
            filtered = list(filter(lambda x: "\"ecommerce\"" in x, targets.split("\n")))
            obj = json.loads(filtered[0])
            obj = obj["ecommerce"]["impressions"]
            query = TZ.localize(datetime.now())
            return list(map(lambda o:
                            Voucher(
                                name = o["name"],
                                brand =  o["brand"],
                                id = o["id"],
                                price = o["price"],
                                url = f"https://www.voucherwonderland.com/note/add/ordernumber/{o['id']}",
                                updated = None,
                                created = None,
                                queried = query
                            ), obj
                        ))
        except Exception as e:
            print(f"Error checking targets: {e},\n {response}")
            return []


# Telegram Bot Token
ui = TelegramUI(CHAT_ID, BOT_TOKEN)
bot = ui.bot
api = WonderlandApi()
hapi = OaHostelsApi()
service = VoucherService(ui, CHECK_INTERVAL)


@bot.message_handler(commands=['start'])
def start_message(message):
    print(f"User started: {message.chat.id}")
    ui.reply(message,
             f"Hello! I'll notify you if there are available vouchers\nYour chat: `{message.chat.id}`", parse_mode="Markdown")


@bot.message_handler(commands=['trigger'])
def trigger(message):
    try:
        service.poll_and_check(True)
    except Exception as e:
        ui.error(f"Triggering failed", e)


@bot.message_handler(commands=['check'])
def check_message(message):
    try:
        ui.reply(message, "not supported")
    except Exception as e:
        ui.error(f"Checking failed", e)


@bot.message_handler(commands=['check_raw_products'])
def check_raw_products(message):
    try:
        raw_data = hapi.get_raw_products()
        file = io.BytesIO(json.dumps(raw_data).encode("utf-8"))
        file.name = "products.json"  # Set a filename for the file
        bot.send_document(message.chat.id, file)
    except Exception as e:
        ui.error(f"Fetching raw data failed", e)

@bot.message_handler(commands=['check_raw_targets'])
def check_raw_targets(message):
    try:
        raw_data = api.get_raw_best_targets()
        file = io.BytesIO(raw_data.encode("utf-8"))
        file.name = "targets.json"  # Set a filename for the file
        bot.send_document(message.chat.id, file)
    except Exception as e:
        ui.error(f"Fetching raw data failed", e)

@bot.message_handler(commands=['set_interval'])
def set_interval(message):
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


service.start()
time.sleep(0.1)
ui.start_blocking()
