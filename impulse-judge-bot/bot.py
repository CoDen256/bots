import io
import json
from datetime import datetime, timedelta
import pytz
import telebot
import requests
import time
from threading import Thread

BOT_TOKEN = ""
# Time interval for periodic checks (in seconds)
CHECK_INTERVAL = 60 * 60 * 4  # god forgive me for editing this global var, im so sorry
# User ID to notify (replace with the actual user ID or chat ID)
CHAT_ID = 283382228


class Verdict:
    def __init__(self, guilty, reason, evidence):
        self.guilty = guilty
        self.reason = reason
        self.evidence = evidence
        self.latest = self.get_latest(evidence)
        self.next_change = None if not self.latest else self.latest + timedelta(days=5)

    def get_latest(self, evidence):
        checkIns = evidence["checkIns"]
        latest = None
        for c in checkIns:
            datetime = parse_datetime(c["checkInDate"])
            if not latest or datetime > latest:
                latest = datetime
        return latest

    def __str__(self):
        pre = "Not guilty ✅" if not self.guilty else "Guilty ❌"
        return f"Status: {pre}\nReason: *{self.reason}*\nNext lockdown: *{format_datetime(self.next_change)}*\n\nLast evidence:\n{format_datetime(self.latest)}"

    def __repr__(self):
        return self.__str__()


class JudgeApi:
    # The URL to check
    API_HOST = "https://impulse-judge-service.onrender.com"
    CHECK_ENDPOINT = "/check"

    def __init__(self):
        pass

    def get_raw_check(self):
        response = requests.get(JudgeApi.API_HOST + JudgeApi.CHECK_ENDPOINT, timeout=600)
        response.raise_for_status()  # Raise an exception for HTTP errors
        json = response.json()
        print(f"Got response: {json}")
        return json

    def get_check(self):
        try:
            data = self.get_raw_check()
            return Verdict(data["guilty"], data["reason"], data["evidence"])
        except Exception as e:
            print(f"Error checking URL: {e}")
            raise e


# Telegram Bot Token
bot = telebot.TeleBot(BOT_TOKEN)
api = JudgeApi()


def parse_datetime(datetime_str):  # Define the format of the input string
    format_str = "%Y-%m-%dT%H:%M:%S"  # Parse the string into a datetime object
    parsed_datetime = datetime.strptime(datetime_str, format_str)
    return pytz.utc.localize(parsed_datetime)


@bot.message_handler(commands=['start'])
def start_message(message):
    print(message.chat.id)
    bot.reply_to(message, "Hello! I'll check the judge for you")


@bot.message_handler(commands=['check'])
def check_message(message):
    try:
        data = api.get_check()
        bot.reply_to(message, f"{data}", parse_mode='Markdown')
    except Exception as e:
        bot.reply_to(message, f"Error while checking: {e}")


@bot.message_handler(commands=['check_raw'])
def check_raw_message(message):
    try:
        raw_data = api.get_raw_check()
        file = io.BytesIO(json.dumps(raw_data).encode("utf-8"))
        file.name = "response.json"  # Set a filename for the file
        bot.send_document(message.chat.id, file)
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


@bot.message_handler(commands=['notify'])
def check_raw_message(message):
    try:
        notify_if_needed(api.get_check())
    except Exception as e:
        bot.reply_to(message, f"Error while fetching raw data: {e}")

# Function to format datetime string
def format_datetime(datetime):
    cet = pytz.timezone('Europe/Berlin')
    cet_datetime = datetime.astimezone(cet)
    # Format the datetime object into the desired string format
    formatted_datetime = cet_datetime.strftime("on %a %d. %B %Y at %H:%M:%S")
    # Replace month name to German
    return formatted_datetime


def readable_delta(delta):
    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes = remainder // 60 # Format the result as a readable string
    return (days, hours, minutes)

def is_now_between(start_time_str, end_time_str): # Parse the start and end times
    start_time = datetime.strptime(start_time_str, "%H:%M").time()
    end_time = datetime.strptime(end_time_str, "%H:%M").time() # Get the current time
    now = datetime.now().time() # Check if the current time is within the specified range
    return start_time <= now <= end_time

def notify_if_needed(result):
    now = datetime.now(pytz.utc)
    if (not is_now_between("08:00", "23:55")):
        print(f"Currently: {now}, Sleepy time.")
        return
    until = result.next_change - now
    (days, hours,minutes) = readable_delta(until)
    if (not result.guilty and (days*24 + hours) <= 2.5 * 24):
        lockdown = '\nat'.join(format_datetime(result.next_change).split('at'))
        bot.send_message(CHAT_ID, f"⚠️ Warning! Next lockdown is \n\n`{lockdown}`"
                                  f"\n\nRemains: *{days} days {hours} hours {minutes} minutes*", parse_mode="Markdown")
    else:
        print("Skipping...In a lockdown and/or not enough time until lockdown")

def poll_and_check():
    result = api.get_check()
    print(f"Got verdict:\n{result}\n")
    notify_if_needed(result)



# Function to check the URL
def check_for_openings():
    global CHECK_INTERVAL
    while True:
        print("\n\n")
        print("-"*20)
        print(f"Checking at {datetime.now()}")
        poll_and_check()
        print(f"Next check in {CHECK_INTERVAL}s")
        time.sleep(CHECK_INTERVAL)


# Start the periodic check in a separate thread
Thread(target=check_for_openings, daemon=True).start()
# Polling for Telegram bot commands
print("Bot is running...")
bot.infinity_polling()
