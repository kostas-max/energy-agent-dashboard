
import re
from db import save_prompt, mark_saved
from sources_manager import add_source, get_all_sources
from scraper import search_on_demand
from calendar_utils import add_event
from file_manager import create_folder
from ai_agent import parse_with_ai, is_ai_enabled
from conversation_manager import save_conversation, log_ai_api_call

# Κρατάμε το τελευταίο conversation_id
last_conversation_id = None

def handle_prompt(prompt: str) -> dict:
    """
    Επεξεργασία prompt και επιστροφή dict με reply και conversation_id
    """
    global last_conversation_id
    save_prompt(prompt)

    response_text = _execute_prompt_logic(prompt)

    return {
        "reply": response_text,
        "conversation_id": last_conversation_id
    }

def _execute_prompt_logic(prompt: str) -> str:
    """Εσωτερική function που εκτελεί τη λογική του prompt"""
    global last_conversation_id
    save_prompt(prompt)

    # Αν το AI είναι ενεργοποιημένο, προσπάθησε πρώτα με AI
    if is_ai_enabled():
        ai_result = parse_with_ai(prompt)
        command = ai_result.get("command", "")
        params = ai_result.get("params", "")
        usage = ai_result.get("usage", {})

        # Εκτέλεση της εντολής που επέστρεψε το AI
        if command == "SEARCH" and params:
            try:
                n = search_on_demand(params)
                response = f"[OK] Βρέθηκαν {n} νέα σχετικά αποτελέσματα για '{params}'. Δες το tab 'Νέα'."
                last_conversation_id = save_conversation(prompt, response, f"SEARCH: {params}")
                if usage:
                    log_ai_api_call(last_conversation_id, "gpt-4o-mini", usage.get("prompt_tokens", 0),
                                   usage.get("completion_tokens", 0), usage.get("latency_ms", 0))
                return response
            except Exception as e:
                response = f"[ERROR] Σφάλμα κατά την αναζήτηση: {str(e)}"
                last_conversation_id = save_conversation(prompt, response, "SEARCH_ERROR")
                return response

        elif command == "ADD_SOURCE" and params:
            try:
                response = add_source(params)
                last_conversation_id = save_conversation(prompt, response, f"ADD_SOURCE: {params}")
                if usage:
                    log_ai_api_call(last_conversation_id, "gpt-4o-mini", usage.get("prompt_tokens", 0),
                                   usage.get("completion_tokens", 0), usage.get("latency_ms", 0))
                return response
            except Exception as e:
                response = f"[ERROR] Σφάλμα κατά την προσθήκη πηγής: {str(e)}"
                last_conversation_id = save_conversation(prompt, response, "ADD_SOURCE_ERROR")
                return response

        elif command == "LIST_SOURCES":
            try:
                sources = get_all_sources()
                lines = [f"- {s['url']} ({s['type']})" for s in sources]
                response = "Πηγές:\n" + "\n".join(lines) if lines else "Δεν υπάρχουν πηγές."
                last_conversation_id = save_conversation(prompt, response, "LIST_SOURCES")
                if usage:
                    log_ai_api_call(last_conversation_id, "gpt-4o-mini", usage.get("prompt_tokens", 0),
                                   usage.get("completion_tokens", 0), usage.get("latency_ms", 0))
                return response
            except Exception as e:
                response = f"[ERROR] Σφάλμα κατά την ανάκτηση πηγών: {str(e)}"
                last_conversation_id = save_conversation(prompt, response, "LIST_SOURCES_ERROR")
                return response

        elif command == "CREATE_FOLDER" and params:
            try:
                create_folder(params)
                response = f"[OK] Δημιουργήθηκε ο φάκελος: {params}"
                last_conversation_id = save_conversation(prompt, response, f"CREATE_FOLDER: {params}")
                if usage:
                    log_ai_api_call(last_conversation_id, "gpt-4o-mini", usage.get("prompt_tokens", 0),
                                   usage.get("completion_tokens", 0), usage.get("latency_ms", 0))
                return response
            except Exception as e:
                response = f"[ERROR] Σφάλμα κατά τη δημιουργία φακέλου: {str(e)}"
                last_conversation_id = save_conversation(prompt, response, "CREATE_FOLDER_ERROR")
                return response

        elif command == "HELP":
            response = """[AI ENABLED] Διαθέσιμες εντολές:
• Ψάξε/Βρες/Κάνε αναζήτηση για <θέμα> - Αναζήτηση ειδήσεων
• Πρόσθεσε πηγή <url> - Προσθήκη νέας πηγής
• Ποιες πηγές έχω/Δείξε τις πηγές - Εμφάνιση πηγών
• Φτιάξε/Δημιούργησε φάκελο <όνομα> - Δημιουργία φακέλου
• Βοήθεια - Αυτό το μήνυμα

Μιλάς ελεύθερα στον agent, δεν χρειάζονται ακριβείς εντολές!"""
            last_conversation_id = save_conversation(prompt, response, "HELP")
            if usage:
                log_ai_api_call(last_conversation_id, "gpt-4o-mini", usage.get("prompt_tokens", 0),
                               usage.get("completion_tokens", 0), usage.get("latency_ms", 0))
            return response

        elif command == "DISABLED":
            # Fallback στο παλιό σύστημα αν το AI είναι disabled
            pass
        elif command == "ERROR":
            # Fallback αν το AI είχε σφάλμα
            pass
        else:
            # Άγνωστη εντολή από AI, fallback στο παλιό σύστημα
            pass

    # Fallback στο παλιό rule-based σύστημα
    p = prompt.lower()

    if p.startswith("πρόσθεσε πηγή") or p.startswith("προσθεσε πηγη"):
        # Υποστήριξη και για τις δύο εκδοχές (με/χωρίς τόνους)
        if "πηγή" in prompt.lower():
            url = prompt.lower().split("πηγή")[-1].strip()
        else:
            url = prompt.lower().split("πηγη")[-1].strip()
        try:
            res = add_source(url)
            last_conversation_id = save_conversation(prompt, res, f"ADD_SOURCE: {url}")
            return res
        except Exception as e:
            response = f"[ERROR] Σφάλμα κατά την προσθήκη πηγής: {str(e)}"
            last_conversation_id = save_conversation(prompt, response, "ADD_SOURCE_ERROR")
            return response

    if p.startswith("δείξε τις πηγές") or p.startswith("δειξε τις πηγες"):
        try:
            sources = get_all_sources()
            lines = [f"- {s['url']} ({s['type']})" for s in sources]
            response = "Πηγές:\n" + "\n".join(lines) if lines else "Δεν υπάρχουν πηγές."
            last_conversation_id = save_conversation(prompt, response, "LIST_SOURCES")
            return response
        except Exception as e:
            response = f"[ERROR] Σφάλμα κατά την ανάκτηση πηγών: {str(e)}"
            last_conversation_id = save_conversation(prompt, response, "LIST_SOURCES_ERROR")
            return response

    if p.startswith("ψάξε") or p.startswith("ψαξε"):
        try:
            parts = prompt.split(" ", 1)
            if len(parts) < 2:
                response = "[ERROR] Πρέπει να δώσεις έναν όρο αναζήτησης. Π.χ.: 'ψάξε φωτοβολταϊκά'"
                last_conversation_id = save_conversation(prompt, response, "SEARCH_ERROR")
                return response
            query = parts[1].strip()
            n = search_on_demand(query)
            response = f"[OK] Βρέθηκαν {n} νέα σχετικά αποτελέσματα για '{query}'. Δες το tab 'Νέα'."
            last_conversation_id = save_conversation(prompt, response, f"SEARCH: {query}")
            return response
        except Exception as e:
            response = f"[ERROR] Σφάλμα κατά την αναζήτηση: {str(e)}"
            last_conversation_id = save_conversation(prompt, response, "SEARCH_ERROR")
            return response

    if "σημαντικό" in p or "σημαντικο" in p:
        try:
            m = re.search(r"https?://\S+", prompt)
            if m:
                mark_saved(m.group(0))
                response = "[OK] Σημάνθηκε ως σημαντικό."
                last_conversation_id = save_conversation(prompt, response, f"MARK_SAVED: {m.group(0)}")
                return response
            response = "[INFO] Δώσε και το link στο ίδιο prompt για να το σημάνω ως σημαντικό."
            last_conversation_id = save_conversation(prompt, response, "MARK_SAVED_INFO")
            return response
        except Exception as e:
            response = f"[ERROR] Σφάλμα: {str(e)}"
            last_conversation_id = save_conversation(prompt, response, "MARK_SAVED_ERROR")
            return response

    if p.startswith("φτιάξε φάκελο") or p.startswith("φτιαξε φακελο"):
        # Υποστήριξη και για τις δύο εκδοχές (με/χωρίς τόνους)
        if "φάκελο" in prompt.lower():
            name = prompt.lower().split("φάκελο")[-1].strip()
        else:
            name = prompt.lower().split("φακελο")[-1].strip()

        if not name:
            response = "[ERROR] Πρέπει να δώσεις όνομα για τον φάκελο. Π.χ.: 'φτιάξε φάκελο Έργα'"
            last_conversation_id = save_conversation(prompt, response, "CREATE_FOLDER_ERROR")
            return response

        try:
            create_folder(name)
            response = f"[OK] Δημιουργήθηκε ο φάκελος: {name}"
            last_conversation_id = save_conversation(prompt, response, f"CREATE_FOLDER: {name}")
            return response
        except Exception as e:
            response = f"[ERROR] Σφάλμα κατά τη δημιουργία φακέλου: {str(e)}"
            last_conversation_id = save_conversation(prompt, response, "CREATE_FOLDER_ERROR")
            return response

    if "βάλε στο ημερολόγιο" in p or "βαλε στο ημερολογιο" in p:
        try:
            dates = re.findall(r"(\d{1,2}/\d{1,2}/\d{4})", prompt)
            if len(dates) == 2:
                add_event("Πρόγραμμα", dates[0], dates[1], description="Καταχώρηση από prompt")
                response = f"[OK] Προστέθηκε event {dates[0]} -> {dates[1]} στο calendar."
                last_conversation_id = save_conversation(prompt, response, f"ADD_EVENT: {dates[0]}-{dates[1]}")
                return response
            elif len(dates) == 1:
                add_event("Σημαντικό γεγονός", dates[0], None, description="Καταχώρηση από prompt")
                response = f"[OK] Προστέθηκε event την {dates[0]}."
                last_conversation_id = save_conversation(prompt, response, f"ADD_EVENT: {dates[0]}")
                return response
            response = "[INFO] Δεν βρήκα ημερομηνίες (μορφή: ΗΗ/ΜΜ/ΕΕΕΕ)."
            last_conversation_id = save_conversation(prompt, response, "ADD_EVENT_INFO")
            return response
        except Exception as e:
            response = f"[ERROR] Σφάλμα κατά την προσθήκη event: {str(e)}"
            last_conversation_id = save_conversation(prompt, response, "ADD_EVENT_ERROR")
            return response

    if "βοήθεια" in p or "help" in p:
        if is_ai_enabled():
            response = """[AI ENABLED] Διαθέσιμες εντολές:
• Ψάξε/Βρες/Κάνε αναζήτηση για <θέμα> - Αναζήτηση ειδήσεων
• Πρόσθεσε πηγή <url> - Προσθήκη νέας πηγής
• Ποιες πηγές έχω/Δείξε τις πηγές - Εμφάνιση πηγών
• Φτιάξε/Δημιούργησε φάκελο <όνομα> - Δημιουργία φακέλου
• Βοήθεια - Αυτό το μήνυμα

Μιλάς ελεύθερα στον agent, δεν χρειάζονται ακριβείς εντολές!"""
        else:
            response = """Διαθέσιμες εντολές:
• ψάξε <όρος> - Αναζήτηση σχετικών αποτελεσμάτων
• πρόσθεσε πηγή <url> - Προσθήκη νέας πηγής
• δείξε τις πηγές - Εμφάνιση όλων των πηγών
• φτιάξε φάκελο <όνομα> - Δημιουργία νέου φακέλου
• βάλε στο ημερολόγιο ΗΗ/ΜΜ/ΕΕΕΕ - Προσθήκη event στο calendar
• σημαντικό <link> - Σημείωση link ως σημαντικό"""
        save_conversation(prompt, response, "HELP")
        return response

    response = "[INFO] Δεν αναγνώρισα εντολή. Γράψε 'βοήθεια' για να δεις τις διαθέσιμες εντολές."
    save_conversation(prompt, response, "UNKNOWN")
    return response
