import logging as log
from util import read_token

log.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=log.INFO)
id = 283382228
time = "14:50"
token = read_token("token")
notion_token = read_token("notion_token")
notion_database_id = read_token("db_id")