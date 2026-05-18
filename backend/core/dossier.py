"""core/dossier.py — Dossier Builder V4 — BB-2026-XX-XXXX + 7 types"""
from datetime import datetime
from models import generate_dossier_id

DOSSIER_TYPES = {
    "SignalNote":    ("signal","Signal non verifie — watch only"),
    "Qualified":     ("ok","Passe verification — peut proceder"),
    "Strategic":     ("star","Haute valeur — cross-sector ou rare"),
    "Emergency":     ("alert","Risque immediat — Shield active"),
    "Execution":     ("exec","Apres commande executee — suivi"),
    "HumanTakeover": ("human","Investor a repondu — Operator prend le relais"),
    "Weekly":        ("week","Rapport hebdomadaire auto"),
}

SECTOR_COMMANDS = {
    "Real Estate":  ["Qualify","Build Dossier","Write Email","Watchlist","Blacklist"],
    "E-Commerce":   ["Test Product","Full Analysis","Wild Card","Watchlist","Close"],
    "Trading":      ["Analyze Signal","Shield Mode","Monitor","Ignore"],
    "Export":       ["Match Buyer","Compliance Check","Outreach Draft","Watchlist"],
    "Agro":         ["Qualify Asset","Certification Check","Draft","Watchlist"],
    "Industriel":   ["Qualify Asset","ZAI Check","Draft","Watchlist"],
    "Tourisme":     ["Qualify Asset","Tourism Analysis","Draft","Watchlist"],
    "default":      ["Proceed","Dossier","Cross-Sector","Watchlist","Close"],
}

def _determine_type(opportunity, verification):
    opp_score = opportunity.get("opportunity_score",0)
    trust = opportunity.get("trust_score",0)
    if verification and verification.get("block_reason"): return "Emergency"
    if trust < 50 or opp_score < 40: return "SignalNote"
    if opp_score >= 75: return "Strategic"
    return "Qualified"

def build(opportunity, analysis, verification=None, creative=None):
    sector = opportunity.get("sector","Real Estate")
    dossier_type = _determine_type(opportunity, verification)
    scores = {
        "trust_score":       opportunity.get("trust_score",0),
        "risk_score":        opportunity.get("risk_score",0),
        "opportunity_score": opportunity.get("opportunity_score",0),
        "confidence":        opportunity.get("confidence",0),
        "strategic_value":   analysis.get("strategic_value",0),
        "time_horizon":      analysis.get("time_horizon","medium"),
        "morocco_relevance": opportunity.get("morocco_relevance",0),
    }
    flags = []
    if scores["trust_score"] < 50: flags.append("Trust faible — verifier")
    if scores["risk_score"] > 70: flags.append("Risque eleve — escalader")
    if verification and not verification.get("verified"): flags.append("Non verifie")
    if verification:
        for rf in verification.get("red_flags",[])[:3]: flags.append(rf)
    from legal.legal_engine import inject_legal_context
    legal_ctx = opportunity.get("legal_context","") or inject_legal_context(sector)
    return {
        "dossier_id":    opportunity.get("dossier_id", generate_dossier_id(sector)),
        "created_at":    datetime.utcnow().strftime("%Y-%m-%d %H:%M"),
        "type":          dossier_type,
        "sector":        sector,
        "source_agent":  "Zaeer->Chaheb->Zakia->Basil",
        "priority":      opportunity.get("priority","Medium"),
        "urgency":       "Urgent" if scores["trust_score"]>=75 and scores["opportunity_score"]>=70 else "Normal",
        "executive_summary": {
            "what":           opportunity.get("title",""),
            "why":            opportunity.get("summary",""),
            "recommendation": analysis.get("recommendation",""),
            "investor_country": opportunity.get("investor_country",""),
            "investor_profile": opportunity.get("investor_profile",""),
        },
        "scores":        scores,
        "flags":         flags,
        "verification":  verification or {"verified":False},
        "cross_sector_links": analysis.get("cross_sector_links",[]),
        "scenarios":     analysis.get("scenarios",{}),
        "pattern_detected": analysis.get("pattern_detected"),
        "legal_context": legal_ctx,
        "basil_classic": creative.get("classic_solution","") if creative else "",
        "basil_bold":    creative.get("bold_idea","") if creative else "",
        "ibrahim_question": analysis.get("ibrahim_question"),
        "confidence_reason": opportunity.get("confidence_reason",""),
        "status":        "Pending Ibrahim",
        "decision_commands": SECTOR_COMMANDS.get(sector, SECTOR_COMMANDS["default"]),
    }

def format_web(dossier, lang="french"):
    """Format propre pour Web App — card style, pas Telegram"""
    s = dossier["scores"]
    ex = dossier["executive_summary"]
    lines = []
    lines.append(f"{dossier['sector']} — {dossier['type']} | {dossier['priority']}")
    lines.append(f"{ex['what']}")
    lines.append(f"")
    lines.append(ex['why'][:300])
    lines.append(f"")
    lines.append(f"Trust {s['trust_score']}/100 · Risk {s['risk_score']}/100 · Opp {s['opportunity_score']}/100")
    if ex.get('recommendation'):
        lines.append(f"")
        lines.append(ex['recommendation'][:250])
    if dossier.get('ibrahim_question'):
        lines.append(f"")
        lines.append(f"→ {dossier['ibrahim_question']}")
    flags = dossier.get('flags', [])
    if flags:
        lines.append(f"")
        lines.append("⚠️ " + " · ".join(flags[:3]))
    lines.append(f"")
    lines.append(" · ".join(dossier["decision_commands"]))
    return "\n".join(lines)


def format_telegram(dossier, lang="french"):
    s = dossier["scores"]
    ex = dossier["executive_summary"]
    flags_text = "\n".join(dossier.get("flags",[])) or "Clean"
    msg = (f"DOSSIER {dossier['dossier_id']} — {dossier['sector']}\n"
           f"Type: {dossier['type']} | Priorite: {dossier['priority']} | {dossier['urgency']}\n"
           f"==================\n"
           f"{ex['what']}\n\n"
           f"Resume:\n{ex['why'][:400]}\n\n")
    if ex.get("investor_country"):
        msg += f"Pays: {ex['investor_country']}"
        if ex.get("investor_profile"): msg += f" | {ex['investor_profile']}"
        msg += "\n"
    msg += (f"\nScores:\n"
            f"  Trust: {s['trust_score']}/100 | Risk: {s['risk_score']}/100\n"
            f"  Opportunite: {s['opportunity_score']}/100 | Confiance: {s['confidence']}%\n"
            f"  Valeur strat.: {s['strategic_value']}/100 | Horizon: {s['time_horizon']}\n\n"
            f"Flags:\n{flags_text}\n\n"
            f"Recommandation:\n{ex['recommendation'][:300]}\n")
    if dossier.get("legal_context"): msg += f"\n{dossier['legal_context']}\n"
    if dossier.get("cross_sector_links"): msg += f"\nCross-Sector: {', '.join(dossier['cross_sector_links'][:3])}\n"
    if dossier.get("pattern_detected"): msg += f"\nPattern detecte: {dossier['pattern_detected']}\n"
    if dossier.get("ibrahim_question"): msg += f"\nIbrahim: {dossier['ibrahim_question']}\n"
    if dossier.get("basil_bold"): msg += f"\nBasil Wild Card: {dossier['basil_bold'][:200]}\n"
    msg += f"\n==================\n"
    msg += " | ".join(dossier["decision_commands"])
    return msg
