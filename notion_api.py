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
        return self.post(url, data)

    def post(self, url, data):
        res = requests.request("POST", url, headers=self.headers, data=json.dumps(data))
        return (res.status_code, json.loads(res.text)) 

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
        if (status == 200):
            properties = res["results"][0]["properties"]
            desc = properties["Description"]["rich_text"][0]["text"]["content"]
            month = properties["Month"]["title"][0]["text"]["content"]
            return (month, desc)
        else:
            return None