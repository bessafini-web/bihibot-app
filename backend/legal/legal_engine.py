"""legal/legal_engine.py — Legal Intelligence V4"""
from ai.ai_router import route_ai
from datetime import datetime

LEGAL_KB = {
    "real_estate": {
        "loi_39_08":    "Code des droits reels — propriete fonciere Maroc",
        "terres_agri":  "Restrictions achat terres agricoles etrangers (Loi 62-19)",
        "vna":          "VNA — Vocation Non Agricole: procedure declassement terrain",
        "titre_foncier":"Melk vs Titre Foncier vs Habous — differences et risques",
        "charte_invest":"Charte Investissement 2022-2025 — primes jusqu'a 30%",
        "is_exemption": "IS exonere 5 ans pour investissements > 10M MAD",
        "zai":          "Zones Acceleration Industrielle — avantages fiscaux Maroc",
    },
    "export": {
        "office_changes":"Office des Changes — reglementation transferts internationaux",
        "certifications":"GlobalGAP, Halal, BIO — certifications export requises",
        "accords":       "Accords Maroc: UE, USA, Afrique — regles origine",
        "douanes":       "Procedures douanieres export Maroc",
    },
    "ecommerce": {
        "rgpd":          "EU RGPD — obligations donnees personnelles clients EU",
        "tva_oss":       "TVA e-commerce UE — OSS scheme",
        "dropshipping":  "Dropshipping legalite Maroc — Payoneer/Wise Office des Changes",
        "spa_maroc":     "SPA Maroc — capital minimum 300K MAD, procedure RC, IS",
        "platform_tos":  "Shopify/Amazon/Etsy/TikTok ToS compliance",
    },
    "trading": {
        "mica":           "MiCA 2024 — reglementation crypto Europe",
        "bank_al_maghrib":"Position Bank Al-Maghrib sur crypto — statut 2025",
        "ammc":           "AMMC — reglementation trading Maroc, Forex, Office des Changes",
        "kyc_aml":        "KYC/AML obligations plateformes trading",
    }
}

LEGAL_SYSTEM = """You are BihiApp Legal Intelligence.
Answer legal questions about Morocco real estate, export, e-commerce, dropshipping, SPA, and trading.
RULES:
- Always cite official source (SGG, AMDIE, Bank Al-Maghrib, AMMC, Office des Changes)
- Always state confidence: High/Medium/Low
- Always add disclaimer: general info only, consult lawyer for critical decisions
- If uncertain: say so clearly — NEVER invent
Format: REPONSE / SOURCE / DERNIERE VERIF / CONFIANCE / DISCLAIMER"""

def answer_legal(question, sector="real_estate", lang="french"):
    context = LEGAL_KB.get(sector, {})
    ctx_text = "\n".join([f"- {k}: {v}" for k, v in context.items()])
    prompt = f"""Question legale: {question}
Secteur: {sector} | Langue: {lang}
Base de connaissance:\n{ctx_text}
Date: {datetime.utcnow().strftime("%Y-%m-%d")}"""
    return route_ai("legal", LEGAL_SYSTEM, prompt, max_tokens=600)

def inject_legal_context(sector):
    s = sector.lower()
    if "real estate" in s or "immobilier" in s:
        return "Legal: Verifier titre foncier + eligibilite acheteur etranger (Loi 62-19) + VNA si terrain agricole"
    elif "export" in s or "agro" in s:
        return "Legal: Certifications GlobalGAP/Halal + Office des Changes + regles origine accords UE/USA"
    elif "ecommerce" in s or "dropship" in s:
        return "Legal: Platform ToS + RGPD si clients EU + TVA OSS + legalite Payoneer/Wise Maroc"
    elif "trading" in s or "crypto" in s:
        return "Legal: Position Bank Al-Maghrib crypto + MiCA 2024 + KYC/AML + AMMC Maroc"
    elif "industriel" in s:
        return "Legal: ZAI disponibilite + primes investissement + Charte 2022-2025"
    return "Legal: Verifier reglementation locale applicable"
