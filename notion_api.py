import logging as log
import requests
import json

class NotionAPI:
    def __init__(self, token, databaseId):
        self.headers = {
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json",
            "Notion-Version": "2021-05-13"
        }
        self.databaseId = databaseId

    def updatePage(self, title, month, description):

        url = 'https://api.notion.com/v1/pages'

        data = {
            "parent": {
                "database_id": self.databaseId
            },
            "properties": {
                "ID": {
                    "title": [{"text": {"content": title}}]
                },
                "Month": {
                    "date": {"start": month}
                },
                "Description": {
                    "rich_text": [{"text": {"content": description}}]
                }

            }
        }

        res = requests.request("POST", url, headers=self.headers, data=json.dumps(data))

        log.info(f"Status: {res.status_code}")
        log.info(f"Response: {res.text}")