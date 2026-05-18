"""sheets/execution_log.py"""
from db import append_row
from datetime import datetime
SHEET = "Execution_Log"

def log(agent, operation, platform, what_changed, approval_source, result, rollback=False):
    append_row(SHEET,[datetime.utcnow().strftime("%Y-%m-%d %H:%M"),
                      agent, operation, platform, what_changed,
                      approval_source, result, "Yes" if rollback else "No"])
