"""sheets/opportunities.py"""
from db import append_row, get_all_records
from datetime import datetime
from models import generate_dossier_id
SHEET = "OPPORTUNITIES"

def create_opportunity(title, sector, source, summary, trust, risk, opportunity, confidence,
                       priority="Medium", legal_context="", basil_idea=""):
    bb_id = generate_dossier_id(sector)
    append_row(SHEET,[bb_id, datetime.utcnow().strftime("%Y-%m-%d %H:%M"),
                      title, sector, "Qualified", source, summary[:400],
                      trust, risk, opportunity, confidence, priority, "New",
                      legal_context[:200], basil_idea[:200]])
    return bb_id

def get_all_opportunities():
    try: return get_all_records(SHEET)
    except: return []

def get_by_sector(sector):
    return [o for o in get_all_opportunities() if o.get("Sector","").lower()==sector.lower()]
