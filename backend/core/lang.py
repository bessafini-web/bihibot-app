"""core/lang.py — Language detection"""
DARIJA_WORDS = ["wach","kayn","mashi","bghit","kifach","daba","nta","ana","nel9a","3la","ash",
                "chno","had","dyal","3andi","bghiti","sifet","kteb","nkhdm","chouf","walakin",
                "nzid","hta","men ","wla ","ila ","bach ","rah ","ima ","fin ","9al","gal",
                "dir","diro","ghadi","waqila","bzaf","bzzaf","sabon","sbban","mwarid","moustathmir"]
ARABIC_WORDS = ["هذا","كيف","ماذا","في","أن","كان","هل","من","على","مستثمر","عقار"]
FRENCH_WORDS = ["bonjour","merci","comment","pourquoi","avec","pour ","dans ","donc","mais ",
                "je ","tu ","nous","vous","terrain","investisseur","maroc","opportunite"]

def detect(text):
    t = text.lower()
    d = sum(1 for w in DARIJA_WORDS if w in t)
    a = sum(1 for w in ARABIC_WORDS if w in text)
    f = sum(1 for w in FRENCH_WORDS if w in t)
    if d >= 1: return "darija"
    elif a >= 2: return "arabic"
    elif f >= 2: return "french"
    return "french"

MESSAGES = {
    "darija":  {"pipeline":"Pipeline kaydur...","processing":"Kandiru...","done":"Safi!"},
    "french":  {"pipeline":"Pipeline en cours...","processing":"Traitement...","done":"Termine!"},
    "arabic":  {"pipeline":"جاري التحليل...","processing":"جاري المعالجة...","done":"تم!"},
    "english": {"pipeline":"Running pipeline...","processing":"Processing...","done":"Done!"},
}
def get(lang, key): return MESSAGES.get(lang, MESSAGES["french"]).get(key,"...")
