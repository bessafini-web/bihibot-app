"""memory/ilm.py — Ibrahim Logic Memory V4 — Auto learning depuis feedback naturel"""
from db import append_row, get_all_records, update_cell, find_row, get_setting
from datetime import datetime
import json

SHEET = "ILM"

# ── User Profile — persiste dans SETTINGS sheet ─────────────────
USER_PROFILE = {
    "decision_style": "fast",
    "preferred_lang": "darija",
    "response_preference": "short",
    "humor_level": "medium",
    "focus_sectors": [],
    "patterns": [],
    "last_mood": "neutral",
    "conversation_count": 0,
}

def _load_profile():
    """Load profile from SETTINGS sheet at startup"""
    global USER_PROFILE
    try:
        raw = get_setting("USER_PROFILE")
        if raw:
            saved = json.loads(raw)
            USER_PROFILE.update(saved)
    except: pass

def _save_profile():
    """Save profile to SETTINGS sheet"""
    try:
        from db import get_sheet
        ws = get_sheet("SETTINGS")
        rows = ws.get_all_records()
        profile_json = json.dumps({
            k: USER_PROFILE[k] for k in 
            ["decision_style","preferred_lang","humor_level",
             "focus_sectors","conversation_count","last_mood"]
        })
        for i, r in enumerate(rows):
            if r.get("Key") == "USER_PROFILE":
                ws.update_cell(i + 2, 2, profile_json)
                return
        ws.append_row(["USER_PROFILE", profile_json, "Dynamo user profile", ""])
    except: pass

# Load on import
_load_profile()

def update_profile(message, response):
    """Update user profile and persist every 5 conversations"""
    global USER_PROFILE
    USER_PROFILE["conversation_count"] += 1
    # Detect language preference
    darija_words = ["wah","labas","mzyan","wakha","safi","bghit","kayn","daba","3ndi"]
    french_words = ["oui","non","merci","bonjour","parfait","ok","voila"]
    darija_count = sum(1 for w in darija_words if w in message.lower())
    french_count = sum(1 for w in french_words if w in message.lower())
    if darija_count > french_count: USER_PROFILE["preferred_lang"] = "darija"
    elif french_count > darija_count: USER_PROFILE["preferred_lang"] = "francais"
    else: USER_PROFILE["preferred_lang"] = "mix"
    # Detect decision speed
    fast_words = ["daba","maintenant","vite","urgent","go","yalla"]
    if any(w in message.lower() for w in fast_words):
        USER_PROFILE["decision_style"] = "fast"
    # Detect humor
    humor_words = ["hhhh","lol","haha","😂","mzyan bezaf"]
    if any(w in message.lower() for w in humor_words):
        USER_PROFILE["humor_level"] = "high"
    # Track sectors mentioned
    sectors = ["immo","trading","crypto","export","agro","tourisme","industriel","ecommerce"]
    for s in sectors:
        if s in message.lower() and s not in USER_PROFILE["focus_sectors"]:
            USER_PROFILE["focus_sectors"].append(s)
    # Persist every 5 conversations
    if USER_PROFILE["conversation_count"] % 5 == 0:
        _save_profile()

def get_profile_context():
    """Returns a short context string for Dynamo's system prompt"""
    p = USER_PROFILE
    ctx = f"User profile: lang={p['preferred_lang']}, style={p['decision_style']}, humor={p['humor_level']}"
    if p["focus_sectors"]:
        ctx += f", focus={','.join(p['focus_sectors'][-3:])}"
    if p["conversation_count"] > 10:
        ctx += f", {p['conversation_count']} conversations — Dynamo knows him well."
    return ctx

def add_rule(command, action, context, source="Ibrahim"):
    append_row(SHEET,[datetime.utcnow().strftime("%Y-%m-%d %H:%M"),
                      command, action, context, "Active", 0, 0.0, source])

def apply_correction(command, context, correction):
    t = correction.lower()
    if any(w in t for w in ["pas bon","wrong","faux","reject","non","machi"]):
        action = "reduce_weight"
    elif any(w in t for w in ["toujours","always","jamais","never","dima"]):
        action = "enforce_rule"
    elif any(w in t for w in ["bon","good","correct","zid","plus","mezyan"]):
        action = "increase_weight"
    else:
        action = "reinforce"
    add_rule(command=command, action=action,
             context=f"{context} | Correction: {correction[:200]}", source="User_Auto")

def get_active_rules():
    try: return [r for r in get_all_records(SHEET) if r.get("Status")=="Active"]
    except: return []

def get_rules_for_sector(sector):
    return [r for r in get_active_rules() if sector.lower() in r.get("Context","").lower()]

def increment_applied(command):
    try:
        row_num = find_row(SHEET, command, col=2)
        if row_num:
            rules = get_all_records(SHEET)
            if len(rules) >= row_num - 1:
                current = int(rules[row_num-2].get("Applied_Count",0) or 0)
                update_cell(SHEET, row_num, 6, current + 1)
    except: pass
