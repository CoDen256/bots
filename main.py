from notion_api import  *

TOKEN = "secret_LZjYnWZZXpiQ0KUgT8vg6ph3afXj2j59yxRoZyw7k7I"
DB = "3ca81a17-1dfe-4457-a5ea-3b3d6d687dd0"

api = NotionAPI(TOKEN, DB)

api.update_page({
    "address": "Linkelstr.19",
    "company": "Anne Sccc",
    "phone": "49",
    "url": "https://bla.com",
    "email": "email@bla",
    "space": 10,
    "kitchen": "Yes",
    "animal": "VB",
    "free": "2023-01-11T00:00:00.000+01:00"
})