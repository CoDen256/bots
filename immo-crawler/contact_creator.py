import telebot

bot = telebot.TeleBot("5829646579:AAHsXrD-BFxQp9p5rHz5MqBBzGBlmcWJyz4", parse_mode=None)


def send_contact(phone, name, company, address):
    bot.send_contact(283382228, phone_number=phone, first_name=address + f"-{name}", last_name=company)