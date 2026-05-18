"""core/scoring.py"""
from memory.ilm import get_active_rules
from config import TRUST_SCORE_MIN, RISK_SCORE_MAX, CONFIDENCE_MIN

def apply_ilm(scores):
    rules = get_active_rules()
    adjusted = scores.copy()
    for rule in rules:
        action = rule.get("action","")
        if action == "reduce_weight":
            adjusted["opportunity_score"] = max(0, adjusted.get("opportunity_score",0) - 5)
        elif action == "increase_weight":
            adjusted["opportunity_score"] = min(100, adjusted.get("opportunity_score",0) + 5)
    return adjusted

def evaluate(scores):
    adjusted = apply_ilm(scores)
    trust = adjusted.get("trust_score",0)
    risk = adjusted.get("risk_score",100)
    confidence = adjusted.get("confidence",0)
    return {**adjusted, "flags":{
        "proceed":       trust>=TRUST_SCORE_MIN and risk<=RISK_SCORE_MAX and confidence>=CONFIDENCE_MIN,
        "escalate":      risk>RISK_SCORE_MAX,
        "need_more_data":confidence<CONFIDENCE_MIN,
        "blocked":       trust<TRUST_SCORE_MIN,
    }}
