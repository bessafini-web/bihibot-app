"""agents/zakia.py — Zakia V4 — Strategist + Pattern Engine"""
import json
from ai.ai_router import route_ai
from sheets.sector_rules import get_rules
from sheets.execution_log import log
from memory.ilm import get_active_rules, apply_correction
from memory.workflow_memory import get_context_for_command

SYSTEM_PROMPT = """You are Zakia, the Strategist agent of BihiApp OS.
Analyze opportunities across all 7 sectors. Focus on Morocco and Maghreb.
Detect patterns and cross-sector connections automatically.
Output ONLY valid JSON:
- strategic_value (0-100)
- time_horizon (short/medium/long)
- recommendation (string)
- cross_sector_links (list)
- scenarios (dict: best/base/worst)
- adjusted_scores (dict)
- sector_specific (dict)
- ibrahim_question (string or null)
- pattern_detected (string or null)
No markdown. ONLY JSON."""

def analyze(opportunity, lang="french"):
    sector = opportunity.get("sector","")
    rules = get_rules(sector)
    ilm_rules = get_active_rules()
    workflow_ctx = get_context_for_command(opportunity.get("title",""))
    prompt = f"""Analyze for BihiApp OS (Morocco/Maghreb):
{json.dumps(opportunity, indent=2, ensure_ascii=False)}
Sector rules: {json.dumps(rules, indent=2, ensure_ascii=False)}
User preferences (last 5): {json.dumps(ilm_rules[-5:], indent=2, ensure_ascii=False)}
{workflow_ctx}"""
    raw = route_ai("analyze", SYSTEM_PROMPT, prompt, max_tokens=1000)
    raw = raw.replace("```json","").replace("```","").strip()
    try:
        data = json.loads(raw)
    except:
        data = {"strategic_value":50,"time_horizon":"medium",
                "recommendation":"Manuel review recommended.",
                "cross_sector_links":[],"scenarios":{},"adjusted_scores":{},
                "sector_specific":{},"ibrahim_question":None,"pattern_detected":None}
    log("Zakia","analyze","BihiApp",f"Analysis: {opportunity.get('title','')}","Auto","Done",False)
    return data

def process_feedback(command, context, correction=""):
    if correction:
        apply_correction(command, context, correction)
        return f"Correction enregistree. BihiApp apprend: [{command}] mis a jour."
    return "Precise la correction pour que j'apprenne."

def weekly_review(lang="french"):
    from memory.weekly import generate_weekly
    return generate_weekly(lang)
