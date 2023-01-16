import requests
import json
import logging as log


class NotionAPI:
    def __init__(self, token, databaseId):
        self.headers = {
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        self.databaseId = databaseId

    @staticmethod
    def search(token):
        headers = {
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        return requests.post("https://api.notion.com/v1/search", headers=headers).json()

    def update_page(self, card):
        url = 'https://api.notion.com/v1/pages'

        data = {
            "parent": {
                "database_id": self.databaseId
            },
            "properties": {

                "Address": {
                    "title": [{"text": {"content": card["address"]}}]
                },
                "Vermieter": {
                    "rich_text": [{"text": {"content": card["company"]}}]
                },
                # "Phone": {
                #     "phone_number": card["phone"]
                # },
                "URL": {
                    "url": card["url"]
                },
                "Email": {
                    "email": card["email"]
                },
                "Fläche": {
                    "number": card["space"]
                },
                "EBK": {
                    "select": {"name" : card["kitchen"]}
                },
                "Tier": {
                    "select": {"name": card["animal"]}
                },
                "Bezug": {
                    "date" : {"start": card["free"]}
                }
            }
        }
        (status, res) = self.post(url, data)
        if status != 200:
            print(res)
            raise Exception(f"Failed to insert a page")

    def post(self, url, data):
        res = requests.request("POST", url, headers=self.headers, data=json.dumps(data))
        (status, body) = response = res.status_code, json.loads(res.text)
        log.info(f"Status: {status}")
        log.info(f"Response: {body}")
        return response
