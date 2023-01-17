import logging
import os
from dateutil.parser import parse
from googlepaths import *
from immo24 import *
from notion_api import *

TOKEN = "secret_LZjYnWZZXpiQ0KUgT8vg6ph3afXj2j59yxRoZyw7k7I"
DB = "3ca81a17-1dfe-4457-a5ea-3b3d6d687dd0"

api = NotionAPI(TOKEN, DB)


def parse_move(move):
    if ("sofort") in move:
        move = "01.01.2023"
    if ("frei") in move:
        move = "01.01.2023"
    return parse(move).strftime("%Y-%m-%dT00:00:00.000+01:00")


def parse_pets(pets):
    if "negoti" in pets: return "VB"
    if "n" in pets: return "No"
    if "y" in pets: return "Yes"
    return "VB"

def parse_float(space):
    return float(space.replace(",", "."))


def parse_int(ome):
    return int(ome)



def parse_kitchen(kitchen):
    if "n" in kitchen: return "No"
    if "y" in kitchen: return "Yes"
    return "No"


def publish(o: Wohnung):
    api.update_page(
        address=o.address,
        name=o.name,
        company=o.company,
        obj_url=o.url,
        phone=o.phone,
        mobile=o.mobile,
        space=parse_float(o.space),
        total=parse_float(o.total_rent),
        ome=parse_int(o.ome),
        htwk=parse_int(o.htwk),
        kitchen=parse_kitchen(o.kitchen),
        pets=parse_pets(o.pets),
        move=parse_move(o.move),
        extra=o.extra
    )


def main():
    chrome = Chrome()
    for filename in os.listdir(base):
        if filename.endswith(".html"):
            try:
                info = parse_full(filename)
                ome = int(chrome.find_work(info.address))
                htwk = int(chrome.find_htwk(info.address))
                new_info = info.copy()
                new_info.ome = ome
                new_info.htwk = htwk
                print(new_info)
                publish(new_info)
            except Exception as e:
                logging.error("error", e)


main()
