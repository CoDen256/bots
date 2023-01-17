import json
from bs4 import BeautifulSoup

base = "C:\\Users\\denbl\\Downloads\\whs"
keyword = "var keyValues ="
keyword_contact = "contactData:"

def read(file):
    with open(base+"\\"+file, "r", encoding='utf-8') as f:
        return f.read(20_000)

def parse_info(contents):
    for line in contents.split("\n"):
        if keyword in line:
            return json.loads(line.split("keyValues = ")[1][:-1])

def parse_contact(contents):
    for line in contents.split("\n"):
        if keyword_contact in line:
            return json.loads(line.split("contactData:")[1][:-1])

def get_info(c):
    fields = [
        "obj_hasKitchen", "obj_livingSpace", "obj_zipCode", "obj_petsAllowed", "obj_street",
        "obj_houseNumber", "obj_totalRent",
    ]
    res = {}
    for field in fields:
        try:
            res[field] = c[field]
        except:
            pass
    return res

def get_contact_info(c):

    return {
        "Name": f"{c['contactPerson']['salutationAndTitle']} {c['contactPerson']['firstName']} {c['contactPerson']['lastName']}",
        # "Number": c["phoneNumbers"]["phoneNumber"]["contactNumber"],
        # "Cell": c["phoneNumbers"]["cellPhoneNumber"]["contactNumber"],
        "Company": c["realtorInformation"]["companyName"]
    }

def additional_info(file):
    soup = BeautifulSoup(open(base+"\\"+file, encoding="utf8"), 'html.parser')
    frei = soup.findAll("dd", class_="is24qa-bezugsfrei-ab")[0].text.strip()
    heiz = soup.findAll("dd", class_="is24qa-heizkosten")[0].text.strip()
    totalrent = soup.findAll("dd", class_="is24qa-gesamtmiete")[0].text.strip().split(" ")[0]
    return {
        "frei_ab": frei,
        "extra": "nicht" in heiz,
        "obj_totalRent": totalrent
    }

def parse_full(file):
    file_contents = read(file)
    res = get_info(parse_info(file_contents))
    contact = get_contact_info(parse_contact(file_contents))
    add = additional_info(file)
    return res | contact | add

def main():
    print(parse_full("4.html"))