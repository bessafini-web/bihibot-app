"""agents/wassi.py — Wassi V4 — Diplomat + CRM + Human Takeover"""
import json
from ai.ai_router import route_ai
from sheets.execution_log import log
from sheets.alerts import create_alert

SYSTEM_PROMPT = """You are Wassi, the Diplomat agent of BihiApp OS.
Draft professional communications for Ibrahim. You NEVER send — Ibrahim decides.
Rules:
- Draft only. Ibrahim approves before any use.
- Professional tone. Arabic / French / English / Darija as needed.
- For real estate: never push, never promise, never quote prices.
- Brand: BihiApp OS.
Output ONLY valid JSON:
  draft, subject, tone, language, warning, bihibot_signature (bool)
No markdown. ONLY JSON."""

def draft_email(context, brief, language="French"):
    prompt = f"""Draft professional communication for BihiApp OS:
Context: {json.dumps(context, indent=2, ensure_ascii=False)}
Brief: {brief}
Language: {language}
Brand: BihiApp OS — short, professional, non-pushy. Operator reviews before use."""
    raw = route_ai("email", SYSTEM_PROMPT, prompt, max_tokens=900)
    raw = raw.replace("```json","").replace("```","").strip()
    try:
        data = json.loads(raw)
    except:
        data = {"draft":"Draft generation failed. Manual writing required.",
                "subject":"Opportunite — BihiApp OS","tone":"formal",
                "language":language,"warning":"Verifier avant tout envoi","bihibot_signature":True}
    data["requires_ibrahim_approval"] = True
    log("Wassi","draft_email","Email",
        f"Draft: {context.get('investor','Unknown')}","Pending Ibrahim","Draft Ready",False)
    return data

def human_takeover_notice(investor_name, reply_summary):
    create_alert("Urgent",f"Reply: {investor_name}",f"{reply_summary[:200]}","Wassi")
    log("Wassi","human_takeover","Telegram",
        f"Investor replied: {investor_name}","Auto","Ibrahim alerted",False)
    return (f"HUMAN TAKEOVER — WASSI STOPPED\n"
            f"{investor_name}\n{reply_summary[:300]}\n"
            f"Operator prend le relais. Wassi n'auto-repond JAMAIS.")
