import telebot

bot = telebot.TeleBot("5829646579:AAHsXrD-BFxQp9p5rHz5MqBBzGBlmcWJyz4", parse_mode=None)

def send_contact(phone, name, surname, company, address):
    bot.send_contact(283382228, phone_number=phone, first_name=address+f"-{name} {surname}", last_name=company)


send_contact("+491573722", "Uwe", "Schömburg", "Blabla AG", "Linkelstr. 18")