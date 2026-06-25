import json
import os
from datetime import datetime

DB_FILE = "database.json"

DEFAULT_DB = {
    "owner_id": 5855151459,
    "admins": {"admin1": None, "admin2": None, "admin3": None},
    "groups": {"group1": None, "group2": None},
    "welcome_messages": {"w1": None, "w2": None, "w3": None},
    "rules": "",
    "mutes": {},
    "users": {},
    "daily_stats": {
        "group1": {"new_members": 0, "left_members": 0, "messages": 0, "links_deleted": 0},
        "group2": {"new_members": 0, "left_members": 0, "messages": 0, "links_deleted": 0}
    },
    "join_counts": {}
}

def load_db():
    if not os.path.exists(DB_FILE):
        save_db(DEFAULT_DB)
        return DEFAULT_DB
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_db():
    return load_db()