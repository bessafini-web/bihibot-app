"""
db.py — Google Sheets wrapper V4
19 sheets — setup automatique au premier lancement
"""
import gspread
from google.oauth2.service_account import Credentials
from config import GOOGLE_CREDENTIALS_FILE, GOOGLE_SHEET_ID

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

_client = None
_spreadsheet = None

SHEETS_CONFIG = {
    "INVESTORS_CRM":    ["ID","Date","Name","Company","Nationality","Country","Source","Source_URL",
                         "Interest_Level","Sectors","Trust_Score","Risk_Score","Qualification",
                         "Morocco_Relevance","Notes","CRM_Status","Nurture_Next_Date"],
    "OPPORTUNITIES":    ["BB_ID","Date","Title","Sector","Type","Source","Summary",
                         "Trust_Score","Risk_Score","Opportunity_Score","Confidence",
                         "Priority","Status","Legal_Context","Basil_Idea"],
    "ILM":              ["Date","Command","Action","Context","Status","Applied_Count","Success_Rate","Source"],
    "Execution_Log":    ["Date","Agent","Operation","Platform","What_Changed","Approval","Result","Rollback"],
    "Alerts":           ["Date","Level","Title","Summary","Agent","Status"],
    "Sector_Rules":     ["ID","Sector","Rule_Type","Condition","Action","Source","Created_At","Applied_Count","Success_Rate"],
    "DECISIONS_LOG":    ["Date","Dossier_ID","Command","Agent","Result","Status","Learning_Note"],
    "NURTURE":          ["Investor_ID","Name","Status","Next_Contact","Last_Contact","Notes","Channel"],
    "REFERRALS":        ["Referral_ID","Referred_By","Name","Country","Sector","Status","Date"],
    "LEADS_INDUSTRIEL": ["ID","Date","Name","Country","Asset_Type","Location","Budget","Status","Notes"],
    "LEADS_TOURISME":   ["ID","Date","Name","Country","Asset_Type","Stars","Budget","Status","Notes"],
    "LEADS_AGRO":       ["ID","Date","Name","Country","Asset_Type","Product","Certification","Budget","Status","Notes"],
    "EXPORT_MATCHES":   ["Match_ID","Category","Product","Supplier","Buyer","Country","Volume","Confidence","Status"],
    "ECOMMERCE_OPS":    ["Op_ID","Date","Platform","Product","Budget","Status","ROI","Notes","Approval"],
    "WEEKLY_REPORTS":   ["Week","Date","Signals","Dossiers","Learning_Rules","Top_Opp","Alerts","KPI_JSON"],
    "OVERVIEW":         ["Date","Signals_Today","Dossiers_Total","High_Priority","Pending","Alerts","Rules_Learned","Top_Sector"],
    "SOURCES":          ["URL","Sector","Score","Freshness_Seconds","Last_Fetch","Status","Added_By"],
    "SETTINGS":         ["Key","Value","Description","Last_Updated"],
    "WORKFLOW":         ["Date","Pattern_Type","Trigger","Action_Taken","Frequency","Last_Seen"],
}

DEFAULT_SETTINGS = [
    ["TRUST_SCORE_MIN","50","Score minimum pour proceed",""],
    ["RISK_SCORE_MAX","70","Score max risque acceptable",""],
    ["CONFIDENCE_MIN","60","Confiance minimum %",""],
    ["CONFIDENCE_AUTO_FETCH","60","En dessous auto-fetch sources",""],
    ["FINANCIAL_LIMIT_USD","50","Budget mensuel max USD",""],
    ["SCHEDULE_RE","6","Heures entre scans Real Estate",""],
    ["SCHEDULE_ECOM","8","Heures entre scans E-Commerce",""],
    ["SCHEDULE_TRADING","2","Heures entre scans Trading",""],
    ["PHASE1_FOCUS","E-Commerce,Export","Secteurs prioritaires Phase 1",""],
]


def _init():
    global _client, _spreadsheet
    if _client is None:
        creds = Credentials.from_service_account_file(GOOGLE_CREDENTIALS_FILE, scopes=SCOPES)
        _client = gspread.authorize(creds)
    if _spreadsheet is None:
        _spreadsheet = _client.open_by_key(GOOGLE_SHEET_ID)

def get_sheet(name):
    _init()
    return _spreadsheet.worksheet(name)

def get_or_create_sheet(name, headers=None):
    _init()
    try:
        return _spreadsheet.worksheet(name)
    except gspread.exceptions.WorksheetNotFound:
        ws = _spreadsheet.add_worksheet(title=name, rows=1000, cols=30)
        if headers:
            ws.append_row(headers)
        return ws

def setup_all_sheets():
    print("Setting up BihiApp DB...")
    for name, headers in SHEETS_CONFIG.items():
        try:
            get_or_create_sheet(name, headers)
            print(f"  OK: {name}")
        except Exception as e:
            print(f"  SKIP: {name} — {str(e)[:60]}")
    try:
        existing = get_all_records("SETTINGS")
        keys = [r.get("Key") for r in existing]
        for row in DEFAULT_SETTINGS:
            if row[0] not in keys:
                append_row("SETTINGS", row)
    except: pass
    print("All sheets ready.")

def append_row(sheet_name, row):
    get_sheet(sheet_name).append_row(row)

def get_all_records(sheet_name):
    return get_sheet(sheet_name).get_all_records()

def update_cell(sheet_name, row, col, value):
    get_sheet(sheet_name).update_cell(row, col, value)

def find_row(sheet_name, query, col=1):
    try:
        cell = get_sheet(sheet_name).find(query, in_column=col)
        return cell.row
    except gspread.exceptions.CellNotFound:
        return None

def get_setting(key, default=None):
    try:
        for r in get_all_records("SETTINGS"):
            if r.get("Key") == key:
                return r.get("Value", default)
    except:
        pass
    return default
