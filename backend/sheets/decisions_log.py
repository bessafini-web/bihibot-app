"""sheets/decisions_log.py"""
from db import append_row, get_all_records
from datetime import datetime
SHEET = "DECISIONS_LOG"

def log_decision(dossier_id, command, agent, result, status, learning_note):
    append_row(SHEET,[datetime.utcnow().strftime("%Y-%m-%d %H:%M"),
                      dossier_id, command, agent,
                      str(result)[:300] if result else "-", status, learning_note])

def get_recent(n=20):
    try:
        all_d = get_all_records(SHEET)
        return all_d[-n:] if len(all_d)>=n else all_d
    except: return []
