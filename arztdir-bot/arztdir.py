import itertools
import logging
from datetime import datetime, timedelta

import pytz
import requests

log = logging.getLogger(__name__)

class ArztApi:
    LOCALITIES = ["74402510195392513","94418895887138817","94418856297627649","94418877937614849","136244910254196738","94418986358276097","94418836904738817","94418872331403265","94418864488054785","94418868363591681","74402499549724673","94418891544985601","136244761438717954","94418842869563393","94418992644489217","157028186179241986","178813507504441344","178813538199930880","179051503938439168","179082468013377536","179082479826110464","179685372400240640","180175908148611072","180303831238707200","185434567097190400"]
    INSTANCE = "5e8d5ff3a6abce001906ae07"

    API_HOST = "https://onlinetermine.arzt-direkt.com"
    CATEGORY_ENDPOINT = "/api/appointment-category"
    RESERVE_ENDPOINT = "/api/reservation/reserve"
    OPENINGS_ENDPOINT = ("/api/opening?"
                         f"localityIds={','.join(LOCALITIES)}"
                         f"&instance={INSTANCE}"
                         "&terminSucheIdent={ident}"
                         "&forerunTime=0")

    HEADERS = {
        "accept": 'application/json, text/plain, */*',
        "content-type": 'application/json',
        'sec-ch-ua': '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "sec-ch-ua-mobile": '?0',
        "sec-ch-ua-platform": 'Windows"',
        "user-agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 '
                      'Safari/537.36 Edg/131.0.0.0'
    }

    CATEGORY_PAYLOAD = {"birthDate": None,
                        "localityIds": LOCALITIES,
                        "instance": INSTANCE,
                        "catId": "",
                        "insuranceType": "gkv"}

    def get_raw_categories(self):
        url = ArztApi.API_HOST + ArztApi.CATEGORY_ENDPOINT
        log.info(f"Running {url}")
        response = requests.post(url, headers=ArztApi.HEADERS, json=ArztApi.CATEGORY_PAYLOAD)
        response.raise_for_status()
        return response.json()

    def get_categories(self):
        try:
            raw = self.get_raw_categories()["categories"]
            data = [(app for app in x["appointmentTypes"]) for x in raw]
            data= list(itertools.chain(*data))
            return self.unique_id(list(map(lambda x: Appointment(
                x["name"]["de"],
                x["hasOpenings"],
                x["_id"],
                x.get("patientTargetDefault", "both"),
                datetime.strptime(x["lastSync"], "%Y-%m-%dT%H:%M:%S.%fZ"),
                x["terminSucheIdent"],
                datetime.now()
            ), data))
                        )
        except Exception as e:
            log.info(f"Error checking categories: {e}")
            raise e

    def unique_id(self, appointments):
        seen = set()
        result = []

        for obj in appointments:
            if obj.id not in seen:
                seen.add(obj.id)
                result.append(obj)
        return result

    def get_raw_openings(self, id):
        url = ArztApi.API_HOST + ArztApi.OPENINGS_ENDPOINT.replace("{ident}", id)
        log.info(f"Running {url}")
        response = requests.get(url, headers=ArztApi.HEADERS)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()

    def get_openings(self, id):
        try:
            data = self.get_raw_openings(id)["openings"]
            return list(map(lambda x:
                            Opening(
                                x["displayStringNames"],
                                datetime.strptime(x["date"], "%Y-%m-%dT%H:%M:%S.%fZ"),
                                x["duration"],
                                list(map(lambda s: s["kid"], x["kdSet"])),
                                id
                            ),
                            data)
                        )
        except Exception as e:
            log.info(f"Error checking openings: {e}")
            raise e

    def reserve(self, doctors, id, date, duration):
        url = ArztApi.API_HOST + ArztApi.RESERVE_ENDPOINT
        log.info(f"Running {url}")
        expires = datetime.now() + timedelta(minutes=15)
        data = {"instance": ArztApi.INSTANCE,
                "terminSucheIdent": id,
                "dateAppointment": date,
                "duration": int(duration),
                "dateExpiry": inutc(expires),
                "doctorIds": doctors}
        response = requests.post(url, headers=ArztApi.HEADERS, json=data)
        if response.status_code == 200:
            try:
                expires = datetime.strptime(response.json()["reservation"]["dateExpiry"], "%Y-%m-%dT%H:%M:%S.%fZ")
                expires = pytz.utc.localize(expires)
                return True, expires, response.json()
            except Exception as e:
                log.info(f"Cant parse expiry date {e}")
                return False, expires, response.json()
        return False, expires, response.json()




class Appointment:
    def __init__(self, name, has_openings, id, patient, sync: datetime, search_id, updated: datetime):
        self.name = (name
                     .replace("Neurologie", "Neuro")
                     .replace("Psychiatrie", "Psych")
                     .replace("Dr.", "")
                     .replace("med.","")
                     .replace(", LL.M.", "")
                     .replace(", MSc", "")
                     .replace("Bestandspatient", "Bestand")
                     .replace("Neupatient", "Neu")
                     .replace("   ", " ")
                     ).strip()
        self.full_name = name
        self.has_openings = has_openings
        self.id = id
        self.patient = patient
        self.sync: datetime = pytz.utc.localize(sync)
        self.updated = updated
        self.search_id = search_id

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()


class Opening:
    def __init__(self, name, date: datetime, duration, doctor_ids, search_id):
        self.name = name
        self.date = pytz.utc.localize(date)
        self.duration = duration
        self.doctor_ids = doctor_ids
        self.search_id = search_id

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()

def inutc(datetime):
    return datetime.astimezone(pytz.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
