"""sheets/investors.py"""
from db import append_row, get_all_records, find_row, update_cell
from datetime import datetime
SHEET = "INVESTORS_CRM"

def add_investor(name, country, sector, source, trust_score=0, notes=""):
    from models import Investor
    inv = Investor(name=name, country=country, sector_interest=[sector],
                   source=source, trust_score=trust_score, notes=notes)
    append_row(SHEET, inv.to_crm_row())

def blacklist_investor(name):
    row = find_row(SHEET, name, col=3)
    if row: update_cell(SHEET, row, 16, "Blacklisted"); return True
    return False

def get_active_investors():
    try: return [i for i in get_all_records(SHEET) if i.get("CRM_Status")=="Active"]
    except: return []
