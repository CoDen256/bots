import datetime
import json
from collections import defaultdict

from bs4 import BeautifulSoup
from model import Wohnung

base = "C:\\Users\\denbl\\Downloads\\whs"
keyword = "var keyValues ="
keyword_contact = "contactData:"
base_url = "https://www.immobilienscout24.de/expose/"


def read(file):
    with open(base + "\\" + file, "r", encoding='utf-8') as f:
        return f.read(20_000)


def parse_info(contents):
    for line in contents.split("\n"):
        if keyword in line:
            return json.loads(line.split("keyValues = ")[1][:-1])


def parse_contact(contents):
    for line in contents.split("\n"):
        if keyword_contact in line:
            return json.loads(line.split("contactData:")[1][:-1])


def parse_url(contents):
    return base_url + contents.split(base_url)[1].split("-->")[0]


def key(map, key):
    if key in map:
        return map[key]
    return None

def floatmap(val):
    if val is None: return None
    return float(val)

def get_info(c):
    fields = [
        "obj_hasKitchen", "obj_livingSpace", "obj_zipCode", "obj_petsAllowed", "obj_streetPlain",
        "obj_houseNumber", "obj_totalRent", "obj_regio4",
    ]
    res = defaultdict(lambda: None)
    for field in fields:
        try:
            if field in c:
                res[field] = c[field]
        except:
            pass
    return res


def none_to_empty(map, key):
    if key not in map: return ''
    if map[key] is None: return ''
    return map[key]


def get_contact_info(c):
    res = defaultdict(lambda: None)

    if ('contactPerson' in c):
        person = c['contactPerson']
        res["name"] = f"{none_to_empty(person, 'salutationAndTitle')} {none_to_empty(person, 'firstName')} {none_to_empty(person, 'lastName')}"

    if ('phoneNumbers' in c):
        numbers = c['phoneNumbers']
        if "phoneNumber" in numbers:
            res["phone"] = numbers["phoneNumber"]["contactNumber"]
        if "cellPhoneNumber" in numbers:
            res["mobile"] = numbers["cellPhoneNumber"]["contactNumber"]

    if ('realtorInformation' in c):
        if ("companyName" in c['realtorInformation']):
            res["company"] = c["realtorInformation"]["companyName"]
    return res


def additional_info(file):
    soup = BeautifulSoup(open(base + "\\" + file, encoding="utf8"), 'html.parser')
    frei = soup.findAll("dd", class_="is24qa-bezugsfrei-ab")
    if not frei:
        frei = None
    else:
        frei = frei[0].text.strip()

    heiz = soup.findAll("dd", class_="is24qa-heizkosten")
    if not heiz:
        heiz = "nicht"
    else:
        heiz = heiz[0].text.strip()

    totalrent = soup.findAll("dd", class_="is24qa-gesamtmiete")
    if not totalrent:
        totalrent = None
    else:
        totalrent = totalrent[0].text.strip().split(" ")[0]
    return {
        "frei_ab": frei,
        "extra": "nicht" in heiz,
        "obj_totalRent": totalrent
    }


def parse_full(file):
    file_contents = read(file)
    res = get_info(parse_info(file_contents))
    contact = get_contact_info(parse_contact(file_contents))
    url = parse_url(file_contents)
    add = additional_info(file)
    o = res | contact | add
    if 'obj_streetPlain' not in o or 'obj_zipCode' not in o: return
    addr = o['obj_streetPlain']+"."+none_to_empty(res, 'obj_houseNumber')
    if ("information" in addr):
        addr = o["obj_regio4"]
    return Wohnung(
        address=addr,
        zip=o['obj_zipCode'],
        url = url,
        total_rent=o['obj_totalRent'],
        space=o['obj_livingSpace'],
        kitchen=o['obj_hasKitchen'],
        pets=o['obj_petsAllowed'],
        name=o['name'],
        company=o['company'],
        mobile=o['mobile'],
        phone=o['phone'],
        move=o['frei_ab'],
        extra=o["extra"]
    )
