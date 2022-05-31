from notion_api import NotionAPI
import logging as log

class ReminderDatabase(object):

    def __init__(self, config):
        log.info(f"Created database client instance {config}")
        self.config = config
        self.client = NotionAPI(config["token"], config["database"])

    def __enter__(self):
        log.info(f"Connected to Notion API: {self.config}")
        return self
  
    def __exit__(self, exc_type, exc_val, exc_tb):
        log.info(f"Closed connection to Notion API")

    def insert_reminder(self, date, text):
        log.info(f"Inserting {date}, {text}")
        self.client.update_page(date, text)

    def get_last_reminder(self):
        log.info(f"Querying last reminder")
        value = (date, description) = self.client.get_last_entry()
        log.info(f"Query Result:{value}")
        return (date, description)
