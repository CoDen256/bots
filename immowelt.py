import json
from collections import defaultdict

from bs4 import BeautifulSoup

base = "C:\\Users\\denbl\\Downloads\\whs"


def find_json(file):
    soup = BeautifulSoup(open(base + "\\" + file, encoding="utf8"), 'html.parser')
    resl = soup.findAll("script", id="serverApp-state")
    return json.loads(resl[0].text.replace("&q;", "\""))

def find_name(s):
    for n in s:
        if n.startswith("expose"):
            return n
def find_total_and_extra(s):
    total = ""
    extra = "No"
    for entry in s:
        if entry["Key"] == "PRICE_RENT_WARM":
            total =  entry["NumberValue"]
        if entry["Key"] == "PRICE_HEATINGCOSTS":
            if "StringValue" in entry:
                if "nicht " in entry["StringValue"]:
                    extra = "Yes"
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


def get_info(s):
    name = find_name(s)
    obj = s[name]
    url = f"https://www.immowelt.de/{name}"
    space = obj["General"]["LivingSpace"]

    contact = defaultdict(lambda: "N/A")
    contact |= obj["Offerer"]["contactData"]

    company = contact["companyName"]
    name = f"{contact['firstName']} {contact['lastName']}"
    mobile = contact["mobile"]
    phone = contact["phone"]

    address = obj["EstateAddress"]["Street"]
    zip = obj["EstateAddress"]["ZipCode"]

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
        "total_rent": total_rent,
        "extra": extra,
        "kitchen": kitchen,
        "frei": frei,
        "url": url,
        "space": space,
    }

def main():
    json_str = find_json("9.html")
    print(json.dumps(json_str))
    print(get_info(json_str))


if __name__ == '__main__':
    main()