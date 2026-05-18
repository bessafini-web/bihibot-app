"""dynamo/intent_engine.py — Intent Engine V4 — 3 modes: ASSISTANT / MANAGER / DATA"""
import json
from ai.ai_router import route_ai

INTENT_SYSTEM = """You are the Intent Classifier of Dynamo / BihiApp OS.
Classify the user message into ONE of 3 modes + action.

MODE 1 ASSISTANT: conversation, question, opinion, greeting, casual.
MODE 2 MANAGER: user wants something DONE (research, setup, create, send, analyze).
MODE 3 DATA: user wants to SEE data (list, status, alerts, dossiers).

Output ONLY valid JSON, no markdown:
{"mode":"assistant|manager|data","action_type":"scout|verify|analyze|draft|legal|report|ecommerce|export|trading|shield|status|alerts|other","sectors":[],"urgency":"normal","agent_needed":"dynamo","raw_intent":""}"""

COMMAND_MAP = {
    "salam":"other","hi":"other","hello":"other","bonjour":"other","labas":"other",
    "chno ra9i":"other","wakha":"other","mzyan":"other","chouf":"other",
    "scout":"scout","nel9a":"scout","cherche":"scout","trouve":"scout",
    "analyse":"analyze","email":"draft","draft":"draft","sifet":"draft",
    "legal":"legal","qanoun":"legal","loi":"legal",
    "shield":"shield_status","shield on":"shield_activate","shield off":"shield_resume",
    "status":"status","alerts":"alerts","weekly":"report","rapport":"report",
    "shopify":"ecommerce","etsy":"ecommerce","dropshipping":"ecommerce",
    "trading":"trading","crypto":"trading","bitcoin":"trading",
    "export":"export",
}

MODE_MAP = {
    "other":"assistant",
    "scout":"manager","analyze":"manager","draft":"manager",
    "legal":"manager","ecommerce":"manager","trading":"manager",
    "export":"manager","shield_activate":"manager","shield_resume":"manager",
    "status":"data","alerts":"data","report":"data","shield_status":"data",
}

AGENT_MAP = {
    "scout":"zaeer","analyze":"zakia","draft":"wassi",
    "ecommerce":"zaeer","trading":"zaeer","export":"zaeer",
    "legal":"zakia","other":"dynamo","status":"dynamo",
}

def detect_intent(message, lang="french"):
    m = message.strip().lower()
    for cmd, action in COMMAND_MAP.items():
        if cmd in m:
            mode = MODE_MAP.get(action, "assistant")
            return {
                "mode": mode,
                "action_type": action,
                "sectors": [],
                "financial_involved": False,
                "urgency": "normal",
                "research_needed": mode == "manager",
                "raw_intent": message,
                "agent_needed": AGENT_MAP.get(action, "dynamo"),
                "direction": None,
                "product": None,
                "target_countries": []
            }
    # AI classification pour messages complexes
    prompt = f'User says: "{message}"\nLanguage: {lang}\nClassify intent.'
    raw = route_ai("intent", INTENT_SYSTEM, prompt, max_tokens=200)
    raw = raw.replace("```json","").replace("```","").strip()
    try:
        result = json.loads(raw)
        if "mode" not in result:
            result["mode"] = MODE_MAP.get(result.get("action_type","other"), "assistant")
        if "agent_needed" not in result:
            result["agent_needed"] = AGENT_MAP.get(result.get("action_type","other"), "dynamo")
        return result
    except:
        return {
            "mode": "assistant",
            "action_type": "other",
            "sectors": [],
            "financial_involved": False,
            "urgency": "normal",
            "research_needed": False,
            "raw_intent": message,
            "agent_needed": "dynamo",
            "direction": None,
            "product": None,
            "target_countries": []
        }
