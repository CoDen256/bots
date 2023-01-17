from notion_api import  *
from immo24 import *
import os
import logging

TOKEN = "secret_LZjYnWZZXpiQ0KUgT8vg6ph3afXj2j59yxRoZyw7k7I"
DB = "3ca81a17-1dfe-4457-a5ea-3b3d6d687dd0"

api = NotionAPI(TOKEN, DB)


def publish(o):
    api.update_page({
        "address": f"{o['obj_street']} {o['obj_houseNumber']}",
        "company": o["Company"],
        # "phone": o["Number"],
        "url": "https://",
        "email": "email@bla",
        "space": float(o["obj_livingSpace"]),
        "kitchen": "No" if o["obj_hasKitchen"] == "n" else "Yes",
        "animal": {"negotiable":"VB", "n":" No", "y": "Yes"}[o['obj_petsAllowed']],
        "free": f"{o['frei_ab'].replace('.', '-')}T00:00:00.000+01:00" if "." in o['frei_ab'] else "2023-01-01T00:00:00.000+01:00"
    })

def main():
    for filename in os.listdir(base):
        if filename.endswith(".html"):
            try:
                info = parse_full(filename)
                print(info)
                # publish(info)
            except Exception as e:
                logging.error("error", e)

main()