import sqlite3


def create_table():
    try:
        cursor = connection.cursor()
        cursor.execute("CREATE TABLE quotes (quote text)")
        connection.commit()
    except:pass


connection = sqlite3.connect("demotivator.db")
create_table()


class Quote:
    def __init__(self, value):
        self.value = value

    def save(self):
        cursor = connection.cursor()
        cursor.execute('''INSERT INTO quotes VALUES (?)''', (self.value, ))
        connection.commit()

    def delete(self):
        cursor = connection.cursor()
        cursor.execute('''DELETE FROM quotes WHERE quote=?''', (self.value, ))
        connection.commit()

    @staticmethod
    def all():
        cursor = connection.cursor()
        entries = cursor.execute('''SELECT * FROM quotes''').fetchall()
        return list(map(lambda x: Quote(x[0]), entries))

