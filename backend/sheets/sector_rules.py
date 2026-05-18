"""sheets/sector_rules.py"""
from db import get_all_records
SHEET = "Sector_Rules"

def get_rules(sector):
    try: return [r for r in get_all_records(SHEET) if r.get("Sector","").lower()==sector.lower()]
    except: return []
