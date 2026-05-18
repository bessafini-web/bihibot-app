"""memory/weekly.py — Weekly Report Auto V4"""
from datetime import datetime, timedelta
from db import append_row, get_all_records
from memory.ilm import get_active_rules

SHEET = "WEEKLY_REPORTS"

def generate_weekly(lang="french"):
    now = datetime.utcnow()
    week_start = (now - timedelta(days=7)).strftime("%Y-%m-%d")
    week_str = f"{week_start} -> {now.strftime('%Y-%m-%d')}"
    try: all_ops = get_all_records("OPPORTUNITIES")
    except: all_ops = []
    try: alerts = [a for a in get_all_records("Alerts") if a.get("Status")=="Pending"]
    except: alerts = []
    rules = get_active_rules()
    recent_ops = [o for o in all_ops if o.get("Date","") >= week_start]
    high_ops = [o for o in recent_ops if o.get("Priority")=="High"]
    new_rules = [r for r in rules if r.get("Date","") >= week_start]
    top_opp = high_ops[0].get("Title","Aucune") if high_ops else "Aucune high priority"
    try:
        append_row(SHEET,[week_str, now.strftime("%Y-%m-%d %H:%M"),
                          len(recent_ops), len(recent_ops), len(new_rules),
                          top_opp, len(alerts), ""])
    except: pass
    report = (
        f"VIRESTA · Weekly Report\n"
        f"Semaine: {week_str}\n\n"
        f"{len(recent_ops)} opportunites · {len(high_ops)} High priority · {len(alerts)} alertes · {len(new_rules)} regles apprises\n\n"
        f"Top opportunite: {top_opp}\n"
    )
    if new_rules:
        report += "\nAppris cette semaine:\n"
        for r in new_rules[:3]:
            report += f"{r.get('Command','?')} → {r.get('Action','?')}\n"
    return report
