import requests
import sqlite3

URL_ANTONYMS = "https://antonymonline.ru/antonyms.json?word="
URL_SYNONYMS = "https://synonymonline.ru/assets/json/synonyms.json"
filename = "templates.cfg"
templates = {}

connection = sqlite3.connect("demotivator.db")



def write_to_template(key, value):
    cursor = connection.cursor()
    cursor.execute('''INSERT INTO antonyms VALUES (?,?)''', (key, value))
    connection.commit()

def getAntonym(word):
    cursor = connection.cursor()
    return cursor.execute('''SELECT * FROM antonyms WHERE "key"=? OR "value"=?''', (word, word)).fetchone()

def get_antonym_for_word(word):
    antonym = getAntonym(word)
    if antonym != None:
        return [antonym[1] if antonym[0] == word else antonym[0]]
    return requests.get(URL_ANTONYMS + word).json()["antonyms"]


def get_synonym_for_word(word):
    payload = {"word": word}
    return requests.post(URL_SYNONYMS, data=payload).json()["synonyms"]

def demotivate_sentence(words):
    negative = []
    for word in words:
        try:
            negative.append(try_find_antonyms_and_synonyms(word.strip()))
        except Exception as e:
            raise Exception("Unable to find antonyms or synonyms for " + word)
    return " ".join(negative)


def try_find_antonyms_and_synonyms(word):
    try:
        return get_antonym_for_word(word)[0]
    except Exception as e:
        print("Trying to find synonym for " + word)
        return get_synonym_for_word(word)[0]

def create_db():
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE antonyms (key text, value text)")
    connection.commit()
# create_db()