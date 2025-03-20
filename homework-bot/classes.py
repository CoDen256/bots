import telebot
import sqlite3

class Bot(telebot.TeleBot):
    """ Homework bot, that creates, sends and trachs homework"""
    def __init__(self, token):
        super(Bot, self).__init__(token=token)
        self.token = token
        self.markups = {}
        self.current_markup = None

        self.selection = None
        self.adding = 0

        self.new_hw = {}

        self.selected = {} # id : homework object or id : [hw1, hw2] for not selected group

        self.initial_pattern = {} # pattern for homework filling
        self.homeworks = {} # all homewokrs represented as subject short name: [hw1, (hw2)]
        # for a person should be used unique markup
    def create_markup(self, id, rows=[]):
        if id in self.markups:

            self.current_markup = self.markups[id]

        else:
            current_markup = telebot.types.ReplyKeyboardMarkup()

            for r in rows:
                current_markup.row(*r)

            self.markups[id] = current_markup
            self.current_markup = current_markup

    def delete_markup(self):
        self.current_markup = telebot.types.ReplyKeyboardRemove(selective=False)

    def send(self, message, text):

        self.send_message(message.chat.id, text, reply_markup = self.current_markup)

    def photo(self, message, photo_id):
        self.send_photo(message.chat.id, photo_id, reply_markup = self.current_markup)

    def document(self, message, document_id):
        self.send_document(message.chat.id, document_id, reply_markup = self.current_markup)


class Homework(object):
    def __init__(self, subject, topic, content, date, group=None, photo=None, additional=None):
        self.subject = subject # Name of subject
        self.topic = topic # Current topic
        self.content = content #What to do
        self.date = date #date in Datetime format
        self.group = group #-1 for nongrouped, 1,2 for grouped, 0 for not selected
        self.photo = photo #file id
        self.additional = additional #additional info

    def all_data(self):
        return(self.subject, self.topic, self.content, self.date, 
                self.group, self.photo, self.additional)



class SQLighter:

    def __init__(self, database='homework.db'):
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    def select_all(self):

        with self.connection:
            return self.cursor.execute('SELECT * FROM homework').fetchall()

    def add(self, homework):
        with self.connection:
            self.cursor.execute("INSERT INTO homework VALUES ()")

    def delete(self, homework):

        with self.connection:
            self.cursor.execute("DELETE FROM homework WHERE subject=? and sub_group=?")

    def close(self):

        self.connection.close()


