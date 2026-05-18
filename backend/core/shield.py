"""core/shield.py — Shield Mode + Kill Switch + Full Freeze"""
from datetime import datetime
from sheets.execution_log import log
from sheets.alerts import create_alert

SHIELD_STATE = {"active":False,"reason":None,"activated_at":None,"cooldown_minutes":60}

def activate(reason="Manual"):
    SHIELD_STATE.update({"active":True,"reason":reason,"activated_at":datetime.utcnow().isoformat()})
    create_alert("Urgent","SHIELD MODE ACTIVATED",f"Reason: {reason}","Shield")
    log("Shield","activate","Trading",f"Shield ON: {reason}","Auto","Active",False)
    return f"Shield ON · {reason}\nNouvelles positions: STOP"

def kill_switch():
    SHIELD_STATE.update({"active":True,"reason":"Kill Switch","activated_at":datetime.utcnow().isoformat()})
    create_alert("Urgent","KILL SWITCH","Kill switch activated.","Shield")
    log("Shield","kill_switch","Trading","Kill switch","User","Full Stop",False)
    return "Kill Switch · Toute activite STOPPEE"

def full_freeze():
    SHIELD_STATE.update({"active":True,"reason":"Full Freeze"})
    create_alert("Urgent","FULL FREEZE","Complete system freeze.","Shield")
    return "Full Freeze · Execution ARRETEE"

def resume():
    if not SHIELD_STATE["active"]: return "Shield deja inactif."
    SHIELD_STATE.update({"active":False,"reason":None})
    log("Shield","resume","Trading","Shield off by Ibrahim","Ibrahim","Normal",False)
    return "Shield Desactive\nSysteme normal\nPost-incident review recommande."

def status():
    if SHIELD_STATE["active"]:
        return f"Shield: ACTIF\nRaison: {SHIELD_STATE.get('reason','?')}\nDepuis: {SHIELD_STATE.get('activated_at','?')}"
    return "Shield: Inactif — Systeme normal"
