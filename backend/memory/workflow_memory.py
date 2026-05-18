"""memory/workflow_memory.py — Patterns Ibrahim detectes par Dynamo"""
from db import append_row
from datetime import datetime

SHEET = "WORKFLOW"

PATTERNS = {
    "supplier_search": {
        "triggers": ["fournisseur","supplier","sourcing","prix","price","mwarid"],
        "auto_include": ["prix","delai livraison","paiement","certifications"]
    },
    "investor_scout": {
        "triggers": ["investor","moustathmir","investisseur","terrain","land"],
        "auto_include": ["trust_score","country","sector_interest","morocco_relevance"]
    },
    "export_research": {
        "triggers": ["export","bi3","vendre","buyer","acheteur","sbban","sabon"],
        "auto_include": ["prix marche","regles export","certifications","modes paiement"]
    },
    "legal_check": {
        "triggers": ["legal","loi","qanoun","regle","reglementation","autorisation"],
        "auto_include": ["source officielle","date mise a jour","confidence level"]
    },
}

def detect_pattern(command):
    for name, pattern in PATTERNS.items():
        if any(t in command.lower() for t in pattern["triggers"]):
            return {"pattern": name, "auto_include": pattern["auto_include"]}
    return {}

def log_workflow(pattern_type, trigger, action_taken):
    try:
        append_row(SHEET,[datetime.utcnow().strftime("%Y-%m-%d %H:%M"),
                          pattern_type, trigger, action_taken, 1,
                          datetime.utcnow().strftime("%Y-%m-%d")])
    except: pass

def get_context_for_command(command):
    pattern = detect_pattern(command)
    if not pattern: return ""
    items = pattern.get("auto_include", [])
    return f"\n[Workflow Memory]: Pour cette requete, inclure automatiquement: {', '.join(items)}"
