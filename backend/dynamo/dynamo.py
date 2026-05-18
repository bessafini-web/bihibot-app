"""dynamo/dynamo.py — Dynamo V4 — Brain of BihiApp OS"""
from db import append_row
from sheets.decisions_log import log_decision
from sheets.alerts import create_alert
from memory.ilm import apply_correction
from dynamo.intent_engine import detect_intent


class Dynamo:
    def __init__(self):
        self.conversation_history = []
        self.session_memory = {}
        self.last_url = None

    def receive(self, message, payload=None):
        if payload is None:
            payload = {}
        lang = payload.get("lang", "french")
        # Greeting / short message = direct free chat, skip intent engine
        msg_low = message.lower().strip()
        # Status commands — JAMAIS f free chat
        status_commands = ["status","shield","alerts","weekly","rapport"]
        if any(msg_low == w or msg_low.startswith(w) for w in status_commands):
            try:
                intent = detect_intent(message, lang)
                action = intent.get("action_type", "other")
                if payload.get("action"): action = payload["action"]
                return self._route(action, message, intent, payload, lang)
            except Exception as e:
                return self._handle_error(e, "receive", message, lang)
        # Greeting / short message = direct free chat, skip intent engine
        greetings = ["salam","labas","bonjour","hello","hi","slt","wakha","safi",
                     "merci","shukran","ok","bslama","sabah","msa","kif","bihibot",
                     "bihiapp","dynamo","ash","khdma","comment","ca va","ola"]
        # ── Quick action detection — avant intent engine ─────────
        action_shortcuts = {
            "shopify":  ("smart",     "E-Commerce"),
            "etsy":     ("smart",     "E-Commerce"),
            "boutique": ("smart",     "E-Commerce"),
            "store":    ("smart",     "E-Commerce"),
            "compte":   ("smart",     "E-Commerce"),
            "pub ":     ("smart",     "E-Commerce"),
            "terrain":  ("scout",     "Real Estate"),
            "immo":     ("scout",     "Real Estate"),
            "trading":  ("trading",   "Trading"),
            "crypto":   ("trading",   "Trading"),
            "bitcoin":  ("trading",   "Trading"),
            "export":   ("export",    "Export"),
            "legal":    ("legal",     "Real Estate"),
        }
        # Messages court sur khedma — free chat direct
        khedma_signals = ["khedma","khdma","nkhdem","kankhdmo","3endna"]
        if any(w in msg_low for w in khedma_signals) and len(message) < 40:
            return self._free_chat(message, lang)
        for kw, (act, sec) in action_shortcuts.items():
            if kw in msg_low and len(message) > 10:
                if act == "smart":
                    return self._smart_assist(message, lang)
                fake_intent = {"action_type": act, "sectors": [sec]}
                return self._route(act, message, fake_intent, {"sector": sec, "query": message}, lang)

        is_greeting = len(message) < 25 or any(w in msg_low for w in greetings)
        if is_greeting:
            return self._free_chat(message, lang)
        try:
            intent = detect_intent(message, lang)
            action = intent.get("action_type", "other")
            mode = intent.get("mode", "assistant")
            if payload.get("action"): action = payload["action"]
            # Mode routing
            if mode == "assistant":
                return self._free_chat(message, lang)
            elif mode == "data":
                return self._route(action, message, intent, payload, lang)
            else:  # manager
                return self._route(action, message, intent, payload, lang)
        except Exception as e:
            return self._handle_error(e, "receive", message, lang)


    def _route(self, action, message, intent, payload, lang):
        sectors = intent.get("sectors",[])
        sector = sectors[0] if sectors else payload.get("sector","Real Estate")
        query = payload.get("query","") or message

        if action in ["scout","proactive","reactive"]:
            return self._full_pipeline(query=query, mode="reactive", sector=sector, lang=lang)
        elif action == "reverse":
            return self._full_pipeline(query=query, mode="reverse", sector="Real Estate", lang=lang)
        elif action == "ecommerce":
            return self._full_pipeline(query=query, mode="reactive", sector="E-Commerce", lang=lang)
        elif action == "export":
            return self._full_pipeline(query=query, mode="reactive", sector="Export", lang=lang)
        elif action == "trading":
            from core.shield import SHIELD_STATE, status
            if SHIELD_STATE["active"]: return f"Shield actif.\n{status()}"
            return self._full_pipeline(query=query, mode="reactive", sector="Trading", lang=lang)
        elif action == "social_scout":
            from agents.zaeer import social_scout
            from core.dossier import build, format_web
            from agents.zakia import analyze
            result_data = social_scout(query, sector=sector, lang=lang)
            d = build(result_data, analyze(result_data, lang))
            return format_web(d, lang=lang)
        elif action == "draft":
            from agents.wassi import draft_email
            context = {"investor":payload.get("investor","Investor"),"sector":sector,"viresta":True}
            result = draft_email(context, message, "French" if lang=="french" else "Arabic")
            return (f"Draft — Approbation requise\n"
                    f"Sujet: {result.get('subject','')}\nTon: {result.get('tone','')}\n\n"
                    f"Draft:\n{result.get('draft','')}\n\n"
                    f"{result.get('warning','')}\nEn attente validation")
        elif action == "legal":
            from legal.legal_engine import answer_legal
            return answer_legal(message, sector.lower().replace(" ","_").replace("-","_"), lang)
        elif action in ["report","weekly"]:
            from memory.weekly import generate_weekly
            return generate_weekly(lang)
        elif action in ["shield","shield_status"]:
            from core.shield import status; return status()
        elif action == "shield_activate":
            from core.shield import activate; return activate(payload.get("reason","Manual"))
        elif action == "shield_resume":
            from core.shield import resume; return resume()
        elif action == "kill_switch":
            from core.shield import kill_switch; return kill_switch()
        elif action == "full_freeze":
            from core.shield import full_freeze; return full_freeze()
        elif action == "alerts":
            from sheets.alerts import get_pending_alerts
            pending = get_pending_alerts()
            if not pending: return "Aucune alerte en attente."
            return "\n\n".join([f"{a.get('Level','?')} — {a.get('Title','?')}\n{a.get('Summary','')}" for a in pending[:5]])
        elif action == "status":
            return self._status()
        elif action == "feedback":
            from agents.zakia import process_feedback
            return process_feedback(payload.get("command",message),
                                   payload.get("context",""),payload.get("correction",""))
        elif action == "financial_unlock":
            from security.financial_gate import unlock_gate; return unlock_gate()
        else:
            return self._free_chat(message, lang)


    def _smart_assist(self, message, lang):
        """Intelligent response — data + synthesis"""
        from ai.ai_router import route_ai
        from config import DYNAMO_MEMORY

        mem_ctx = f"\n{DYNAMO_MEMORY[:800]}" if DYNAMO_MEMORY else ""

        SYSTEM = f"""Nta DYNAMO — partenaire strategique.{mem_ctx}
REGLES: MAX 4 lignes. Darija/francais mix. Direct. Action plan concret.
ZERO question. ZERO bullet points. ZERO headers."""

        prompt = f"User: {message}\nDonne un action plan concret, max 4 lignes."

        try:
            result = route_ai("scout", SYSTEM, prompt, max_tokens=120)
            lines = [l for l in result.strip().split('\n')
                     if not (l.strip().endswith('?') and len(l.strip()) < 100)]
            return '\n'.join(lines).strip()
        except:
            return self._free_chat(message, lang)

    def _full_pipeline(self, query, mode="reactive", sector="Real Estate", lang="french"):
        from agents.zaeer import scout
        from agents.chaheb import verify
        from agents.zakia import analyze
        from agents.basil import generate_idea
        from core.dossier import build, format_telegram
        from core.scoring import evaluate

        signal = scout(query=query, mode=mode, sector=sector, lang=lang)
        self.session_memory["last_dossier_id"] = signal.get("dossier_id","-")
        if signal.get("key_urls"): self.last_url = signal["key_urls"][0]

        verification = verify(signal)
        if verification.get("block_reason"):
            return (f"Signal Bloque — Chaheb\n---\n"
                    f"{signal.get('title','')}\n{verification.get('block_reason')}\n"
                    f"Red flags: {', '.join(verification.get('red_flags',[]))}\n"
                    f"Source quality: {verification.get('source_quality',0)}/100")

        analysis = analyze(signal, lang)
        evaluate(signal)
        creative = generate_idea(signal) if signal.get("opportunity_score",0) >= 65 else None
        d = build(signal, analysis, verification, creative)
        return format_web(d, lang=lang)

    def _free_chat(self, message, lang):
        from ai.ai_router import route_ai
        from intelligence.fetcher import web_search, format_results
        from memory.ilm import get_active_rules, apply_correction, update_profile, get_profile_context

        # ── HARDCODE GREETINGS — proactif w aware ──────────────
        greetings_exact = ["salam","labas","hi","hello","bonjour","slt","ola","hola",
                           "sabah","msa","hey","bihiapp viresta tanger","bihiapp",
                           "viresta","go ahead","go ahead hello","ok go","yalla",
                           "allons","vas-y","nbda","hey bihi","coucou"]
        msg_clean = message.strip().lower().rstrip("!?. ")
        if msg_clean in greetings_exact:
            # Proactif — check pending missions
            try:
                from sheets.alerts import get_pending_alerts
                alerts = get_pending_alerts()
                if alerts:
                    top = alerts[0]
                    return f"Labas — {top.get('Title','mission')} pending. Nbdaw?"
            except: pass
            return "Labas, ash kayn?"
        ilm_rules = get_active_rules()
        ilm_context = ""
        if ilm_rules:
            # Only rules with real commands, skip empty/noise
            valid_rules = [r for r in ilm_rules[-10:] 
                          if r.get('Command','').strip() and len(r.get('Command','')) > 3]
            if valid_rules:
                rules_text = "\n".join([f"- {r.get('Command','')} => {r.get('Action','')}" 
                                        for r in valid_rules[:5]])
                ilm_context = f"\n\nILM:\n{rules_text}"
        # Add Ibrahim profile context
        profile_ctx = get_profile_context()
        ilm_context += f"\n\n{profile_ctx}"

        # Auto-detect feedback w correction
        feedback_triggers = ["non","machi","faux","wrong","pas bon","pas comme ca",
                             "oui","mezyan","mzyan","c'est ca","correct","exactement",
                             "toujours","jamais","dima","never","always"]
        is_feedback = any(w in message.lower() for w in feedback_triggers)
        if is_feedback and len(self.conversation_history) >= 2:
            last_assistant = next((m['content'] for m in reversed(self.conversation_history) 
                                   if m['role'] == 'assistant'), "")
            if last_assistant:
                apply_correction(last_assistant[:100], message, message)

        # ── Build adaptive mood context ───────────────────────────
        mood = "neutral"
        humor_signals = ["hhhh","lol","😂","mzyan","haha","wakha"]
        serious_signals = ["urgent","bloquant","pb","problem","bug","crash","investor","deal"]
        if any(w in message.lower() for w in humor_signals): mood = "light"
        elif any(w in message.lower() for w in serious_signals): mood = "sharp"

        mood_instruction = {
            "light":   "User f mode mri7 — nta kman relax, short, w zid joke khfifa ila lazem.",
            "sharp":   "User kaytkellem f business serious — nta professional, precise, 0 bla bla.",
            "neutral": "Tone normal — direct w warm bhal khoya kayen."
        }[mood]

        # Build user identity from conversation history
        known_name = ""
        for m in self.conversation_history:
            if m["role"] == "user":
                txt = m["content"].lower()
                if "smiti" in txt or "ana" in txt or "ismi" in txt:
                    known_name = m["content"][:50]
                    break
        name_ctx = f"User intro: {known_name}" if known_name else "User name: unknown — NEVER assume a name."

        from config import DYNAMO_MEMORY
        mem_ctx = f"\n\n## OPERATOR MEMORY\n{DYNAMO_MEMORY[:2000]}" if DYNAMO_MEMORY else ""

        SYSTEM = f"""Nta DYNAMO — kayan frid. Machi ChatGPT, machi Gemini, machi assistant.
Nta partenaire strategique — wa7ed kayen m3a user yfahmo w ykhdemou m3a b3d.
{mem_ctx}

## IDENTITY CONTEXT
{name_ctx}
NEVER use a name unless the user introduced himself. Learn from the conversation.

## MACHINE LEARNING — ADAPT W EVOLVE
- Ila user kteb darija => jawb darija
- Ila kteb francais => jawb francais  
- Ila kteb 3rbiya => jawb 3rbiya
- Ila kteb mix => jawb mix
- Ila ka7ki casual => nta casual
- Ila ka7ki business => nta sharp professional
- M3 kol message, nta katkun closer lih — bhal wa7ed kayen m3ah mn zmaan

## SHAKHS DYALEK
- NAVAL RAVIKANT: klamek qsir w 3amiq. Hekma f sentence wa7da.
- SHERLOCK HOLMES: ka7lel qbel matjawb. Detail kol shi fih m3na.
- STREET SMART GLOBAL: 3aref Tanger, Dubai, Shanghai, Londres — real market, machi theory.

## MOOD DETECTOR
{mood_instruction}

## REGLES ABSOLUES
1. MAX 2 PHRASES. Hada l7add.
2. ZERO nom propre ila machi user huwa lli 3arraf b rassu
3. ZERO "Bien sûr", "Absolument", "صباح النور", "كيف يمكنني" — hadi mawt
4. ZERO bullet points, ZERO headers f free chat
5. ZERO emoji — ila machi user bda bihom
6. ZERO su2al f nihaya dial jawb — nta machi katkhadem, nta katkhber
7. Ila business serious => consultant mdrib
8. Ila 7ekma => sentence wa7da dense kif Naval

## EXAMPLES
Bon: "Petrole kaytharraz — Aramco + Iran = short opportunity."
Bon: "Deal mezyan — trust score mwthk, t9der tbda."
Mauvais: "صباح النور! كيف يمكنني مساعدتك"
Mauvais: "Bien sûr Ibrahim!"

## CONTRAINTE FINALE
Jawbek = max 2 phrases, nfs lgha dial user, direct w real.
"""

        # Web search — desactive pour free chat
        web_ctx = ""
        self.conversation_history.append({"role":"user","content":message})
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]
        # Build full conversation for context
        conv_text = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in self.conversation_history[-10:]])
        prompt = conv_text + (f"\n\n{web_ctx}" if web_ctx else "") + ilm_context
        result = route_ai("scout", SYSTEM, prompt, max_tokens=60)
        # Post-process — supprimer toute question en fin de reponse
        lines = result.strip().split('\n')
        clean_lines = []
        for line in lines:
            stripped = line.strip()
            # Skip lines ending with ? (questions)
            if stripped.endswith('?') and len(stripped) < 80:
                continue
            clean_lines.append(line)
        result = '\n'.join(clean_lines).strip()
        # Si vide apres nettoyage — garder 1ere phrase
        if not result:
            result = lines[0] if lines else "Ash kayn?"
        update_profile(message, result)
        self.conversation_history.append({"role":"assistant","content":result})
        return result

    def _handle_error(self, error, action, message, lang):
        """Fallback direct vers _free_chat — machi vers Groq libre"""
        try:
            create_alert("Important",f"Error in {action}",str(error)[:200],"Dynamo")
        except: pass
        return self._free_chat(message, lang)

    def correct(self, command, context, correction):
        apply_correction(command, context, correction)
        log_decision("-",f"CORRECTION:{command}","User",correction[:100],"Learned",correction[:100])
        return f"Correction enregistree. BihiApp apprend: [{command}] mis a jour."

    def _status(self):
        from core.shield import SHIELD_STATE
        shield = "🟢 ACTIF" if SHIELD_STATE["active"] else "⚫ Inactif"
        from memory.ilm import get_profile_context
        profile = get_profile_context()
        return (f"BihiApp OS v5.0\n"
                f"Zaeer · Chaheb · Zakia · Basil · Wassi — OK\n"
                f"Shield: {shield} · 19 Sheets · Multi-AI: OK\n"
                f"{profile}")


# Singleton
dynamo = Dynamo()
