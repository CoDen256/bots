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

    def update_page(self,
                    address,
                    name,
                    company,
                    obj_url,
                    phone,
                    mobile,
                    space,
                    total,
                    ome,
                    htwk,
                    kitchen,
                    pets,
                    move,
                    extra,
                    internet,
                    zip,
                    rooms
                    ):
        url = 'https://api.notion.com/v1/pages'

        data = {
            "parent": {
                "database_id": self.databaseId
            },
            "properties": {

                "Address": {
                    "title": [{"text": {"content": address}}]
                },
                "Vermieter": {
                    "rich_text": [{"text": {"content": name}}]
                },
                "ZIP": {
                    "rich_text": [{"text": {"content": zip}}]
                },
                "Company": {
                    "rich_text": [{"text": {"content": company}}]
                },
                "Phone": {
                    "phone_number": phone
                },
                "Mobile": {
                    "phone_number": mobile
                },
                "URL": {
                    "url": obj_url
                },
                "Fläche": {
                    "number": space
                },
                "Warm": {
                    "number": total
                },
                "Internet": {
                    "number": internet
                },
                "OME": {
                    "number": ome
                },
                "HTWK": {
                    "number": htwk
                },
                "EBK": {
                    "select": {"name" : kitchen}
                },
                "Tier": {
                    "select": {"name": pets}
                },
                "Bezug": {
                    "date" : {"start": move}
                },
                "Zimmer" : {
                    "number": rooms
                },

                "Extra": {
                    "checkbox": extra
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

