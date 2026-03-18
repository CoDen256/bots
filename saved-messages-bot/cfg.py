import os

api_id   = int(os.environ["API_ID"])
api_hash = os.environ["API_HASH"]

# Exact name of the Telegram folder containing your note chats
folder_name = "Notes"

# When moving a message from Saved Messages, leave a backlink there.
# off     — no backlink (default)
# reply   — cross-chat reply to the moved message with "Moved" + quote
# forward — plain silent forward of the moved message back to Saved Messages
backlink = "reply"

session_file = os.environ["SESSION_PATH"]