"""sheets/alerts.py"""
from db import append_row, get_all_records, update_cell, find_row
from datetime import datetime
SHEET = "Alerts"

def create_alert(level, title, summary, agent):
    append_row(SHEET,[datetime.utcnow().strftime("%Y-%m-%d %H:%M"),
                      level, title, summary[:300], agent, "Pending"])

def get_pending_alerts():
    try: return [a for a in get_all_records(SHEET) if a.get("Status")=="Pending"]
    except: return []

def resolve_alert(title):
    try:
        row = find_row(SHEET, title, col=3)
        if row: update_cell(SHEET, row, 6, "Resolved")
    except: pass
