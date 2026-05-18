"""security/financial_gate.py — Double password + 3-fail lock"""
import os, hashlib
from datetime import datetime
from config import FINANCIAL_PASSWORD_HASH

_fail = 0
_locked = False
_lock_time = None

FINANCIAL_OPS = ["transfer","payment","ad_spend","subscription","purchase",
                  "trading_live","budget_approve","invoice","send money","virer"]

def _hash(pw): return hashlib.sha256(pw.encode()).hexdigest()

def requires_financial_auth(command: str) -> bool:
    return any(op in command.lower() for op in FINANCIAL_OPS)

def verify_financial(password: str, operation: str) -> dict:
    global _fail, _locked, _lock_time
    if _locked:
        return {"authorized":False,"reason":"LOCKED — 3 echecs. Admin doit deverrouiller."}
    if _hash(password) == FINANCIAL_PASSWORD_HASH:
        _fail = 0
        try:
            from sheets.decisions_log import log_decision
            log_decision("FINANCIAL_AUTH", operation, "FinancialGate", "AUTHORIZED", "Approved", "")
        except: pass
        return {"authorized":True}
    _fail += 1
    if _fail >= 3:
        _locked = True
        _lock_time = datetime.utcnow().isoformat()
        try:
            from sheets.alerts import create_alert
            create_alert("Urgent","FINANCIAL GATE LOCKED",
                        f"3 echecs sur: {operation}","FinancialGate")
        except: pass
        return {"authorized":False,"reason":"LOCKED — Admin alerte."}
    return {"authorized":False,"reason":f"Mot de passe incorrect. {3-_fail} essai(s) restant(s)."}

def unlock_gate():
    global _fail, _locked
    _fail = 0; _locked = False
    return "Financial gate deverrouille."

def is_locked(): return _locked
