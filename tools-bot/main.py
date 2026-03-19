import argparse
import datetime
import logging

from core_bots import add_cfg_argument, Cfg, TelegramBot

p = argparse.ArgumentParser(description="Topic Message Forwarder Bot")
add_cfg_argument(p)
cfg = Cfg.from_file(p.parse_args().config)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

bot = TelegramBot(cfg.token)


@bot.message_handler(commands=['start'])
def start_message(message):
    log.info(f"User started: {message.chat.id}")
    bot.reply(message,
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
def calculate_savings(message):
    # Extract interval from the message
    parts = message.text.split()
    if len(parts) != 3 or not (parts[1].replace(".", "").isdigit()) or not (parts[2].replace(".", "").isdigit()):
        bot.reply(message, "Usage: /savings <amount in eur> <per_week>")
        return

    sum = float(parts[1])
    per_week = float(parts[2])
    income_date, wednesdays, needed_expenses, investment, savings = calc_savings(sum, per_week)
    plan = '\n'.join([str(w) + ': ' + str(per_week) + ' EUR' for w in wednesdays])
    bot.reply(message, f"Your total current sum: `{sum}` EUR"
                       f"\nYour savings left: `{round(savings, 2)}` EUR\n"
                       f"\nNext income date: `{income_date}` "
                       f"\nWednesdays until new income: `{len(wednesdays)}` "
                       f"\nNeeded total weekly allowance: `{per_week}` EUR x `{len(wednesdays)}` = `{needed_expenses}` EUR"
                       f"\nNeed still to invest: `{round(investment, 2)}` EUR"
                       f"\n\nPlan:\n{plan}", parse_mode='Markdown')


if __name__ == '__main__':
    bot.start_blocking()
