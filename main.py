import logging
import os
from dateutil.parser import parse

import contact_creator
from googlepaths import *
from immo24 import *
from notion_api import *
from contact_creator import *

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
    print("publishing")
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
        extra=o.extra,
        internet=parse_int(o.internet)
    )


def main():
    for filename in os.listdir(base):
        chrome = Chrome()
        if filename.endswith(".html"):
            try:
                info = parse_full(filename)
                print("Parsed full", info)
                new_info = info.copy()
                try:
                    print("Parsing OME Time")
                    new_info.ome = int(chrome.find_work(info.address))
                except Exception as e:
                    logging.error("error ome", e)
                try:
                    print("Parsing HTWK Time")
                    new_info.htwk = int(chrome.find_htwk(info.address))
                except Exception as e:
                    logging.error("error htwk", e)

                try:
                    print("Parsing Internet Speed")
                    new_info.internet = int(chrome.check_internet(info.address, info.zip))
                except Exception as e:
                    logging.error("error internet", e)

                print(new_info)
                publish(new_info)

                if new_info.mobile:
                    contact_creator.send_contact(new_info.mobile, new_info.name, new_info.company, new_info.address)
                elif new_info.phone:
                    contact_creator.send_contact(new_info.phone, new_info.name, new_info.company, new_info.address)

                chrome.quit()
                Chrome(True).open_markets(new_info.address)
            except Exception as e:
                logging.error("error", e)


def check_manual(addr, plz):
    Chrome(True).open_markets(addr)

def check_manual_full(addr, plz):
    chrom = Chrome(True)
    try:
        print("ome", int(chrom.find_work(addr)))
    except:
        pass
    try:
        print("htwk", int(chrom.find_htwk(addr)))
    except:
        pass
    try:
        print("internet", int(chrom.check_internet(addr, plz)))
    except:
        pass
    check_manual(addr, plz)

main()
#
# check_manual("Karl-Liebknecht-Str. 102", "04275")