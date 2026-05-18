"""intelligence/source_registry.py — Sources dynamiques + scoring Ibrahim"""
from db import get_all_records, append_row, find_row, update_cell
from datetime import datetime
from config import DEFAULT_SOURCES

SHEET = "SOURCES"
_reg = {}

def load_registry():
    global _reg
    try:
        for r in get_all_records(SHEET):
            url = r.get("URL","")
            if url: _reg[url] = {"sector":r.get("Sector",""),"score":int(r.get("Score",50)),
                                  "status":r.get("Status","Active"),"added_by":r.get("Added_By","system")}
    except: pass

def add_source(url, sector, score=70, added_by="Ibrahim"):
    _reg[url] = {"sector":sector,"score":score,"status":"Active","added_by":added_by}
    try:
        if not find_row(SHEET, url, col=1):
            append_row(SHEET,[url,sector,score,21600,datetime.utcnow().strftime("%Y-%m-%d"),"Active",added_by])
    except: pass

def update_score(url, delta):
    if url in _reg:
        _reg[url]["score"] = max(0, min(100, _reg[url]["score"] + delta))
        try:
            row = find_row(SHEET, url, col=1)
            if row: update_cell(SHEET, row, 3, _reg[url]["score"])
        except: pass

def blacklist_source(url):
    if url in _reg: _reg[url]["status"] = "Blacklisted"
    try:
        row = find_row(SHEET, url, col=1)
        if row: update_cell(SHEET, row, 6, "Blacklisted")
    except: pass

def process_feedback(text, last_url=""):
    t = text.lower()
    if any(w in t for w in ["mezyan had l source","bonne source","c'est exactement"]):
        if last_url: update_score(last_url, +10)
        return "Source notee fiable."
    if any(w in t for w in ["machi mlih","donnees fausses","makatssahch"]):
        if last_url: update_score(last_url, -20)
        return "Source penalisee."
    if any(w in t for w in ["ma t9lab","blacklist had l site"]):
        if last_url: blacklist_source(last_url)
        return "Source blacklistee."
    for prefix in ["sir l site ","bdaw men ","dkhul l "]:
        if prefix in t:
            url = t.split(prefix)[-1].strip().split(" ")[0]
            if "." in url:
                add_source(url, "default", score=70, added_by="Ibrahim")
                return f"Source ajoutee: {url}"
    return None

def get_sources_for_sector(sector):
    load_registry()
    sources = [(url,info) for url,info in _reg.items()
               if info.get("sector","").lower()==sector.lower() and info.get("status")=="Active"]
    for url in DEFAULT_SOURCES.get(sector,[]):
        if url not in _reg:
            _reg[url] = {"sector":sector,"score":60,"status":"Active"}
            sources.append((url,_reg[url]))
    sources.sort(key=lambda x: x[1].get("score",0), reverse=True)
    return [u for u,_ in sources[:8]]
