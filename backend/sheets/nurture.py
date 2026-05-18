"""sheets/nurture.py"""
from db import append_row, get_all_records
from datetime import datetime
SHEET = "NURTURE"

def add_to_nurture(investor_id, name, next_contact, channel="Email"):
    append_row(SHEET,[investor_id, name, "Active", next_contact,
                      datetime.utcnow().strftime("%Y-%m-%d"), "", channel])

def get_due_today():
    today = datetime.utcnow().strftime("%Y-%m-%d")
    try: return [n for n in get_all_records(SHEET) if n.get("Next_Contact","")<=today and n.get("Status")=="Active"]
    except: return []
