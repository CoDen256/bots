import pytz

CET = pytz.timezone("Europe/Berlin")


def pretty_precise_time(datetime):
    return str(datetime.astimezone(CET).strftime("%d.%m.%y at %H:%M:%S"))

def pretty_time(datetime):
    return str(datetime.astimezone(CET).strftime("%H:%M:%S"))

def pretty_datetime(datetime):
    return str(datetime.astimezone(CET).strftime("🗓️ %b %d, %Y 🕒 %H:%M"))