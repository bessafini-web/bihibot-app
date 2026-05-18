"""agents/chaheb.py — Chaheb V4 — Verifier + Cross-validation"""
import json
from ai.ai_router import route_ai
from sheets.execution_log import log
from sheets.investors import add_investor

SYSTEM_PROMPT = """You are Chaheb, the Verifier agent of BihiApp OS.
Verify signals based on REAL data provided. NEVER invent information.
Cross-validate: check if multiple sources confirm the same facts.
Output ONLY valid JSON:
- verified (bool)
- red_flags (list)
- source_quality (0-100)
- trust_assessment (string)
- qualification_status (Qualified/Potential/Unqualified/Needs More Data)
- block_reason (string or null)
- cross_validation_note (string)
- notes (string)
No markdown. ONLY JSON."""

def verify(signal):
    prompt = f"""Verify this signal for BihiApp OS (Morocco):
{json.dumps(signal, indent=2, ensure_ascii=False)}
Check: source credibility, data consistency, red flags, Morocco relevance."""
    raw = route_ai("verify", SYSTEM_PROMPT, prompt, max_tokens=600)
    raw = raw.replace("```json","").replace("```","").strip()
    try:
        data = json.loads(raw)
    except:
        data = {"verified":False,"red_flags":["Verification failed"],
                "source_quality":0,"trust_assessment":"Unknown",
                "qualification_status":"Needs More Data","block_reason":None,
                "cross_validation_note":"","notes":"Manual review required"}
    if data.get("qualification_status") == "Qualified":
        try:
            add_investor(name=signal.get("title","Unknown"),
                        country=signal.get("investor_country","Unknown"),
                        sector=signal.get("sector","Unknown"),
                        source=signal.get("source","Zaeer"),
                        trust_score=signal.get("trust_score",0),
                        notes=data.get("notes",""))
        except: pass
    log("Chaheb","verify","BihiApp",f"Verified: {signal.get('title','')}",
        "Auto",data.get("qualification_status","Unknown"),False)
    return data
