"""models.py — Data Models V4"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
import uuid

def _now(): return datetime.utcnow().strftime("%Y-%m-%d %H:%M")
def _today(): return datetime.utcnow().strftime("%Y-%m-%d")

@dataclass
class Investor:
    name: str
    country: str
    sector_interest: List[str]
    source: str
    source_url: str = ""
    id: str = field(default_factory=lambda: f"INV-{datetime.utcnow().strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}")
    company: Optional[str] = None
    nationality: str = ""
    interest_level: str = "Active"
    interest_signals: List[str] = field(default_factory=list)
    morocco_relevance: int = 0
    trust_score: int = 0
    risk_score: int = 0
    qualification_status: str = "New"
    public_proof_indicators: List[str] = field(default_factory=list)
    red_flags: List[str] = field(default_factory=list)
    notes: str = ""
    crm_status: str = "Active"
    discovery_date: str = field(default_factory=_today)
    last_interaction: Optional[str] = None
    referral_source: Optional[str] = None
    nurture_next_date: Optional[str] = None
    dossier_ids: List[str] = field(default_factory=list)

    def to_crm_row(self):
        return [self.id, self.discovery_date, self.name, self.company or "",
                self.nationality, self.country, self.source, self.source_url,
                self.interest_level, ",".join(self.sector_interest),
                self.trust_score, self.risk_score, self.qualification_status,
                self.morocco_relevance, self.notes, self.crm_status,
                self.nurture_next_date or ""]

@dataclass
class SectorRule:
    sector: str
    rule_type: str
    condition: str
    action: str
    source: str = "Ibrahim"
    id: str = field(default_factory=lambda: f"RULE-{str(uuid.uuid4())[:6].upper()}")
    created_at: str = field(default_factory=_now)
    applied_count: int = 0
    success_rate: float = 0.0

    def to_sheet_row(self):
        return [self.id, self.sector, self.rule_type, self.condition,
                self.action, self.source, self.created_at,
                self.applied_count, self.success_rate]

def generate_dossier_id(sector=""):
    year = datetime.utcnow().year
    suffix = str(uuid.uuid4())[:4].upper()
    sector_code = {
        "Real Estate":"RE","E-Commerce":"EC","Trading":"TR",
        "Agro":"AG","Export":"EX","Industriel":"IN",
        "Tourisme":"TU","Cross-Sector":"CS"
    }.get(sector,"XX")
    return f"BB-{year}-{sector_code}-{suffix}"
