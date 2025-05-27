import datetime
import pytz
import telebot

BOT_TOKEN = "8182900541:AAGLbCWAsKeB3-jVLDtdSCw-0KdxSj4rOzc"
CHAT_ID = 283382228
TZ = pytz.timezone("Europe/Berlin")


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


ui = TelegramUI(CHAT_ID, BOT_TOKEN)
bot = ui.bot


@bot.message_handler(commands=['start'])
def start_message(message):
    print(f"User started: {message.chat.id}")
    ui.reply(message,
             f"Hello! I'll help you with stuff\nYour chat: `{message.chat.id}`", parse_mode="Markdown")


def calc_savings(current, per_week, investment=216, investment_day=2, income_day=27, dayOfWeek=2):
    today = datetime.date.today()
    year = today.year
    month = today.month

    # Determine the next income date (27th of this month or next month)
    if today.day < income_day or (today.day == income_day and datetime.datetime.now().hour <= 15):
        next_income_date = datetime.date(year, month, income_day)
    else:
        if month == 12:
            next_income_date = datetime.date(year + 1, 1, income_day)
        else:
            next_income_date = datetime.date(year, month + 1, income_day)

    # Calculate the number of Wednesdays (dayOfWeek) from today (inclusive) to next_income_date (exclusive)
    wednesdays = []
    current_date = today
    while current_date < next_income_date:
        if current_date.weekday() == dayOfWeek:
            wednesdays.append(current_date)
        current_date += datetime.timedelta(days=1)

    # Check if investment day for this month has passed
    if investment_day < today.day < income_day:
        investment_cost = 0
    else:
        investment_cost = investment

    total_weekly_left = len(wednesdays) * per_week
    remaining_savings = current - (investment_cost + total_weekly_left)

    return next_income_date, wednesdays, total_weekly_left, investment_cost, remaining_savings

@bot.message_handler(commands=['savings'])
def set_interval(message):
    try:
        # Extract interval from the message
        parts = message.text.split()
        if len(parts) != 3 or not (parts[1].replace(".","").isdigit()) or not (parts[2].replace(".","").isdigit()):
            ui.reply(message, "Usage: /savings <amount in eur> <per_week>")
            return

        sum = float(parts[1])
        per_week = float(parts[2])
        income_date, wednesdays, needed_expenses, investment, savings = calc_savings(sum, per_week)
        plan = '\n'.join([str(w) + ': '+str(per_week)+' EUR' for w in wednesdays])
        ui.reply(message, f"Your total current sum: `{sum}` EUR"
                          f"\nYour savings left: `{round(savings, 2)}` EUR\n"
                          f"\nNext income date: `{income_date}` "
                          f"\nWednesdays until new income: `{len(wednesdays)}` "
                          f"\nNeeded total weekly allowance: `{per_week}` EUR x `{len(wednesdays)}` = `{needed_expenses}` EUR"
                          f"\nNeed still to invest: `{round(investment, 2)}` EUR"
                          f"\n\nPlan:\n{plan}", parse_mode='Markdown')
    except Exception as e:
        ui.error(f"Calculating savings failed", e)


ui.start_blocking()