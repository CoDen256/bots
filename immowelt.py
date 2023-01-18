import json
from collections import defaultdict
from model import Wohnung
from bs4 import BeautifulSoup

immowelt_base = "C:\\Users\\denbl\\Downloads\\whs"


def find_json(file):
    soup = BeautifulSoup(open(immowelt_base + "\\" + file, encoding="utf8"), 'html.parser')
    resl = soup.findAll("script", id="serverApp-state")
    return json.loads(resl[0].text.replace("&q;", "\""))

def find_name(s):
    for n in s:
        if n.startswith("expose"):
            return n
def find_total_and_extra(s):
    total = ""
    extra = False
    for entry in s:
        if entry["Key"] == "PRICE_RENT_WARM":
            total =  entry["NumberValue"]
        if entry["Key"] == "PRICE_HEATINGCOSTS":
            if "StringValue" in entry:
                if "nicht " in entry["StringValue"]:
                    extra = True
    return (total, extra)
def find_eq(s):
    for e in s:
        if e["Key"] == "APARTMENT":
            return e["Equipments"]

def find_kitchen_frei(s):
    kitchen = "No"
    frei = "N/A"
    for e in s:
        if e["Key"] == "KITCHEN":
            kitchen = "Yes"
        if e["Key"] == "VACANCY":
            frei = e["Value"]

    return kitchen, frei
def key(map, key):
    if key in map:
        return map[key]
    return None
def none_to_empty(map, key):
    if key not in map: return ''
    if map[key] is None: return ''
    return map[key]


def get_info(s):
    name = find_name(s)
    obj = s[name]
    url = f"https://www.immowelt.de/{name}"
    space = obj["General"]["LivingSpace"]
    rooms = key(obj["General"], "Rooms")

    contact = defaultdict(lambda: None)
    contact |= obj["Offerer"]["contactData"]

    company = key(contact,"companyName")
    name = f"{none_to_empty(contact, 'salutation')} {none_to_empty(contact, 'firstName')} {none_to_empty(contact,'lastName')}"
    mobile = key(contact, "mobile")
    phone = key(contact, "phone")

    estate_address = obj["EstateAddress"]
    address = key(estate_address, "Street")
    regio = key(estate_address, "District")
    zip = key(estate_address, "ZipCode")

    total_rent, extra = find_total_and_extra(obj["Price"]["DataTable"])
    equipment = find_eq(obj["EquipmentAreas"])
    kitchen,frei = find_kitchen_frei(equipment)
    # pets no info
    # floor ignore
    return {
        "company": company,
        "name": name,
        "mobile": mobile,
        "phone": phone,
        "address": address,
        "zip": zip,
        "regio": regio,
        "total_rent": total_rent,
        "extra": extra,
        "kitchen": kitchen,
        "frei": frei,
        "url": url,
        "space": space,
        "rooms": rooms
    }

def parse_immowelt_full(file):
    json_str = find_json(file)
    print(json.dumps(json_str))
    o = get_info(json_str)
    if 'address' not in o or 'zip' not in o: return
    addr = o['address']
    if addr is None:
        if o["regio"]:
            addr = o["regio"]
        else:
            addr = 'N/A'
    else:
        addr_parts = addr.split(" ")
        addr = " ".join(addr_parts[:-1]) + "." + addr_parts[-1]
    addr = addr.replace("..", ".").replace("_", " ") # REMOVE UNDERLINE

    return Wohnung(
        address=addr,
        zip=o['zip'],
        url=o['url'],
        total_rent=str(o['total_rent']),
        space=str(o['space']),
        kitchen=o['kitchen'],
        name=o['name'],
        company=o['company'],
        mobile=o['mobile'],
        phone=o['phone'],
        move=o['frei'],
        extra=o["extra"],
        rooms=o["rooms"]
    )

