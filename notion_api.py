import requests
import json
import logging as log

class NotionAPI:
    def __init__(self, token, databaseId):
        self.headers = {
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json",
            "Notion-Version": "2021-05-13"
        }
        self.databaseId = databaseId

    def update_page(self, month, description):

        url = 'https://api.notion.com/v1/pages'

        data = {
            "parent": {
                "database_id": self.databaseId
            },
            "properties": {

                "Month": {
                    "title": [{"text": {"content": month}}]
                },
                "Description": {
                    "rich_text": [{"text": {"content": description}}]
                }

            }
        }
        (status, _) = self.post(url, data)
        if (status != 200):
            raise Exception(f"Failed to insert Reminder")

    def post(self, url, data):
        res = requests.request("POST", url, headers=self.headers, data=json.dumps(data))
        (status, body) = response = res.status_code, json.loads(res.text)
        log.info(f"Status: {status}")
        log.info(f"Response: {body}")
        return response

    def get_last_entry(self):
        url = f"https://api.notion.com/v1/databases/{self.databaseId}/query"


        data = {
            "sorts": [{
                "property": "Month",
                "direction": "descending" 
            }],
            "page_size": 1
        }

        (status, res) = self.post(url, data)
        if (status != 200): raise Exception(f"Failed to get last entry")

        properties = res["results"][0]["properties"]
        desc = properties["Description"]["rich_text"][0]["text"]["content"]
        month = properties["Month"]["title"][0]["text"]["content"]
        return (month, desc)