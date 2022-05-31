import logging as log
from util import read_token

log.basicConfig(level=log.INFO)
id = 283382228
db_name = "db"
time = "11:58"
token = read_token("token")
notion_token = read_token("notion_token")
notion_database_id = "c14f4828-2090-4e5b-aa64-e290a18a181d"