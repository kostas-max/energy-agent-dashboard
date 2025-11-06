"""
AI-powered natural language command parser με Conversation Memory
Χρησιμοποιεί OpenAI για να καταλαβαίνει φυσική γλώσσα και να μετατρέπει σε εντολές
Διατηρεί conversation history για context-aware responses
"""

import os
import time
from dotenv import load_dotenv
from conversation_manager import (
    get_conversation_history,
    save_conversation,
    log_ai_api_call
)

load_dotenv()

# Καθαρισμός proxy environment variables που προκαλούν πρόβλημα με OpenAI client
proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy',
              'ALL_PROXY', 'all_proxy', 'NO_PROXY', 'no_proxy']
saved_proxies = {}
for var in proxy_vars:
    if var in os.environ:
        saved_proxies[var] = os.environ[var]
        del os.environ[var]

# Ελέγχουμε αν υπάρχει OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
AI_ENABLED = bool(OPENAI_API_KEY and OPENAI_API_KEY.strip())

if AI_ENABLED:
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
    except Exception as e:
        print(f"[WARNING] AI agent disabled: {e}")
        AI_ENABLED = False

# Επαναφορά proxy variables
for var, value in saved_proxies.items():
    os.environ[var] = value

SYSTEM_PROMPT = """Είσαι ένας έξυπνος βοηθός για Energy Agent Dashboard που μετατρέπει φυσική ελληνική γλώσσα σε συγκεκριμένες εντολές.

Διαθέσιμες εντολές:
1. SEARCH <όρος> - Αναζήτηση ειδήσεων
   - Αναγνωρίζεις όταν ο χρήστης θέλει να ψάξει για κάτι
   - Εξάγεις το σημαντικό keyword/phrase από την ερώτηση
   - Παραδείγματα:
     * "ψάξε για φωτοβολταϊκά" → SEARCH φωτοβολταϊκά
     * "βρες μου νέα για ανακοινώσεις φωτοβολταϊκών" → SEARCH ανακοινώσεις φωτοβολταϊκών
     * "θέλω πληροφορίες από energy press για μπαταρίες" → SEARCH energy press μπαταρίες
     * "δες τι λέει το energypress για επιδοτήσεις" → SEARCH energypress επιδοτήσεις

2. ADD_SOURCE <url> - Προσθήκη πηγής
3. LIST_SOURCES - Εμφάνιση πηγών
4. CREATE_FOLDER <όνομα> - Δημιουργία φακέλου
5. HELP - Βοήθεια

ΣΗΜΑΝΤΙΚΟ:
- Όταν ο χρήστης αναφέρει πηγή (π.χ. "energy press", "energypress"), ΤΗΝ ΣΥΜΠΕΡΙΛΑΜΒΑΝΕΙΣ στο search query
- Εξάγεις ΟΛΑ τα keywords που αναφέρει ο χρήστης, όχι μόνο το τελευταίο
- Αν το context από τα προηγούμενα μηνύματα βοηθάει, το χρησιμοποιείς

Απάντα ΜΟΝΟ με την εντολή, τίποτα άλλο. Μην προσθέσεις εξηγήσεις."""

def parse_with_ai(user_input: str, use_history: bool = True) -> dict:
    """
    Χρησιμοποιεί AI ή smart keyword matching για να μετατρέψει φυσική γλώσσα σε εντολή

    Args:
        user_input: Το input του χρήστη
        use_history: Αν θα χρησιμοποιήσει conversation history για context

    Returns:
        dict με keys: command, params, original_input, conversation_id (αν χρησιμοποιήθηκε AI)
    """
    # Smart keyword-based fallback (χωρίς AI)
    text = user_input.lower()

    # SEARCH patterns
    search_keywords = ["ψάξε", "ψαξε", "βρες", "βρεσ", "αναζητησε", "αναζήτησε", "κανε αναζητηση", "κάνε αναζήτηση",
                       "δειξε μου", "δείξε μου", "θελω να βρω", "θέλω να βρω", "πληροφοριες για", "πληροφορίες για",
                       "νεα για", "νέα για", "αρθρα για", "άρθρα για", "search", "δες τι", "δες", "τι λεει", "τι λέει"]
    for keyword in search_keywords:
        if keyword in text:
            # Βρες τι ακολουθεί μετά το keyword
            parts = text.split(keyword, 1)
            if len(parts) > 1:
                params = parts[1].strip().lstrip("για").strip().lstrip("το").strip().lstrip("απο").strip().lstrip("από").strip()
                if params:
                    # Καθαρισμός από κοινά filler words αλλά κράτηση πηγών
                    return {"command": "SEARCH", "params": params, "original_input": user_input}

    # LIST_SOURCES patterns
    list_keywords = ["ποιες πηγες", "ποιές πηγές", "δειξε τις πηγες", "δείξε τις πηγές",
                      "εμφανισε πηγες", "εμφάνισε πηγές", "τις πηγες μου", "τις πηγές μου"]
    for keyword in list_keywords:
        if keyword in text:
            return {"command": "LIST_SOURCES", "params": "", "original_input": user_input}

    # ADD_SOURCE patterns
    if ("προσθεσε πηγη" in text or "πρόσθεσε πηγή" in text or "προσθηκη πηγης" in text) and "http" in text:
        import re
        url_match = re.search(r"https?://\S+", user_input)
        if url_match:
            return {"command": "ADD_SOURCE", "params": url_match.group(0), "original_input": user_input}

    # CREATE_FOLDER patterns
    folder_keywords = ["φτιαξε φακελο", "φτιάξε φάκελο", "δημιουργησε φακελο", "δημιούργησε φάκελο", "νεος φακελος", "νέος φάκελος"]
    for keyword in folder_keywords:
        if keyword in text:
            parts = text.split(keyword, 1)
            if len(parts) > 1:
                params = parts[1].strip()
                if params:
                    return {"command": "CREATE_FOLDER", "params": params, "original_input": user_input}

    # HELP patterns
    help_keywords = ["βοηθεια", "βοήθεια", "help", "τι μπορεις να κανεις", "τι μπορείς να κάνεις", "εντολες", "εντολές"]
    for keyword in help_keywords:
        if keyword in text:
            return {"command": "HELP", "params": "", "original_input": user_input}

    # Αν το AI είναι enabled, προσπάθησε με OpenAI
    if AI_ENABLED:
        try:
            # Φτιάξε το messages array με history αν χρειάζεται
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]

            if use_history:
                history = get_conversation_history(limit=5)  # Τελευταία 5 exchanges
                messages.extend(history)

            messages.append({"role": "user", "content": user_input})

            start_time = time.time()

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.3,
                max_tokens=100
            )

            latency_ms = int((time.time() - start_time) * 1000)
            ai_output = response.choices[0].message.content.strip()

            # Parse την απάντηση του AI
            parts = ai_output.split(" ", 1)
            command = parts[0].upper()
            params = parts[1] if len(parts) > 1 else ""

            # Log το AI call (θα γίνει save της conversation αργότερα)
            conv_result = {
                "command": command,
                "params": params.strip(),
                "original_input": user_input,
                "ai_response": ai_output,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "latency_ms": latency_ms
                }
            }

            print(f"[AI] Query: '{user_input}' → Command: {command} {params}")
            print(f"[AI] Tokens: {response.usage.prompt_tokens} in + {response.usage.completion_tokens} out = {response.usage.total_tokens} total")
            print(f"[AI] Latency: {latency_ms}ms")

            return conv_result

        except Exception as e:
            print(f"[WARNING] AI parsing failed, using keyword matching: {e}")
            # Fallback σε UNKNOWN αν τίποτα δε δούλεψε
            return {"command": "UNKNOWN", "params": "", "original_input": user_input}

    # Αν δεν βρέθηκε τίποτα
    return {"command": "UNKNOWN", "params": "", "original_input": user_input}

def is_ai_enabled() -> bool:
    """Επιστρέφει True αν το smart parsing είναι ενεργοποιημένο (πάντα True)"""
    # Πάντα enabled γιατί χρησιμοποιούμε smart keyword matching ως fallback
    return True
