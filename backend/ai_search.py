"""
AI-powered search με έξυπνη κατηγοριοποίηση και φιλτράρισμα
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Ρυθμίσεις
AI_SEARCH_ENABLED = os.getenv("AI_SEARCH_ENABLED", "false").lower() == "true"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

if AI_SEARCH_ENABLED and OPENAI_API_KEY:
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        print("[INFO] AI Search enabled with OpenAI")
    except Exception as e:
        print(f"[WARNING] AI Search disabled: {e}")
        AI_SEARCH_ENABLED = False
else:
    print("[INFO] AI Search disabled (set AI_SEARCH_ENABLED=true in .env to enable)")

# Keyword-based fallback (χωρίς OpenAI)
TOPIC_KEYWORDS = {
    "Φωτοβολταϊκά": [
        "φωτοβολταϊκά", "φωτοβολταϊκα", "φωτοβολταικά", "φωτοβολταικα",
        "pv", "solar", "ηλιακά", "ηλιακα", "net metering", "net billing",
        "αυτοπαραγωγή", "αυτοπαραγωγη", "πάνελ", "πανελ", "panels"
    ],
    "Μπαταρίες": [
        "μπαταρία", "μπαταριά", "μπαταριες", "μπαταρίες",
        "battery", "batteries", "αποθήκευση", "αποθηκευση",
        "storage", "ενεργειακή αποθήκευση", "ενεργειακη αποθηκευση"
    ],
    "Αντλίες": [
        "αντλία", "αντλια", "αντλίες", "αντλιες",
        "heat pump", "θερμότητα", "θερμοτητα",
        "θέρμανση", "θερμανση", "ψύξη", "ψυξη"
    ],
    "Νομοθεσία": [
        "νόμος", "νομος", "νομοθεσία", "νομοθεσια",
        "φεκ", "κανονισμός", "κανονισμος", "απόφαση", "αποφαση",
        "ρυθμιστικό", "ρυθμιστικο", "πλαίσιο", "πλαισιο",
        "law", "regulation", "legislation"
    ],
    "Επιδοτήσεις": [
        "επιδότηση", "επιδοτηση", "επιδοτήσεις", "επιδοτησεις",
        "επιχορήγηση", "επιχορηγηση", "πρόγραμμα", "προγραμμα",
        "εσπα", "espa", "χρηματοδότηση", "χρηματοδοτηση",
        "subsidy", "grant", "funding"
    ],
    "Smart_Σπίτια": [
        "smart", "έξυπνο", "εξυπνο", "iot",
        "αυτοματισμός", "αυτοματισμος", "αισθητήρες", "αισθητηρες",
        "έξυπνο σπίτι", "εξυπνο σπιτι", "smart home",
        "automation", "sensors"
    ]
}

def classify_query_keyword(query: str) -> str:
    """
    Κατηγοριοποίηση query με keywords (fallback χωρίς AI)
    """
    query_lower = query.lower()

    # Έλεγχος για κάθε κατηγορία
    matches = {}
    for topic, keywords in TOPIC_KEYWORDS.items():
        match_count = sum(1 for kw in keywords if kw in query_lower)
        if match_count > 0:
            matches[topic] = match_count

    # Επιστροφή της κατηγορίας με τα περισσότερα matches
    if matches:
        return max(matches.items(), key=lambda x: x[1])[0]

    return ""

def classify_query_with_ai(query: str) -> dict:
    """
    Χρησιμοποιεί AI για να κατηγοριοποιήσει και να επεξεργαστεί το query

    Returns:
        {
            "topics": ["Φωτοβολταϊκά", ...],  # Κατηγορίες που αφορά
            "keywords": ["φωτοβολταϊκά", ...],  # Keywords για αναζήτηση
            "intent": "comparison|information|news|subsidy|...",  # Τι θέλει ο χρήστης
            "query_refined": "..."  # Βελτιωμένο query
        }
    """
    if not AI_SEARCH_ENABLED:
        # Fallback σε keyword-based
        topic = classify_query_keyword(query)
        return {
            "topics": [topic] if topic else [],
            "keywords": [query.lower()],
            "intent": "search",
            "query_refined": query
        }

    try:
        system_prompt = """Είσαι ένας ειδικός στον ενεργειακό τομέα. Αναλύεις ερωτήσεις χρηστών.

Κατηγορίες:
- Φωτοβολταϊκά (solar, PV, net metering, etc)
- Μπαταρίες (αποθήκευση ενέργειας, batteries)
- Αντλίες (αντλίες θερμότητας, heat pumps)
- Νομοθεσία (νόμοι, ΦΕΚ, κανονισμοί)
- Επιδοτήσεις (προγράμματα, ΕΣΠΑ, χρηματοδότηση)
- Smart_Σπίτια (IoT, έξυπνα σπίτια, automation)

Intent types:
- information: Ζητάει πληροφορίες
- news: Ζητάει νέα/ενημερώσεις
- comparison: Συγκρίνει προϊόντα/υπηρεσίες
- subsidy: Ψάχνει για επιδοτήσεις
- legal: Ψάχνει νομοθεσία
- howto: Ζητάει οδηγίες

Απάντα σε JSON format:
{
  "topics": ["κατηγορία1", "κατηγορία2"],
  "keywords": ["keyword1", "keyword2"],
  "intent": "intent_type",
  "query_refined": "βελτιωμένο query"
}"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Ανάλυσε αυτό το query: {query}"}
            ],
            temperature=0.3,
            max_tokens=200,
            response_format={"type": "json_object"}
        )

        import json
        result = json.loads(response.choices[0].message.content)
        return result

    except Exception as e:
        print(f"[WARNING] AI classification failed: {e}")
        # Fallback
        topic = classify_query_keyword(query)
        return {
            "topics": [topic] if topic else [],
            "keywords": [query.lower()],
            "intent": "search",
            "query_refined": query
        }

def filter_results_by_relevance(query: str, news_items: list) -> list:
    """
    Φιλτράρει αποτελέσματα με βάση τη σχετικότητα

    Args:
        query: Το αρχικό query
        news_items: Lista από news items με keys: title, url, topic, summary

    Returns:
        Filtered και sorted list
    """
    # Αν δεν έχουμε AI, κάνε απλό keyword matching
    query_analysis = classify_query_with_ai(query)
    topics = query_analysis.get("topics", [])
    keywords = query_analysis.get("keywords", [query.lower()])

    # Score κάθε άρθρο
    scored_items = []
    for item in news_items:
        score = 0
        title = (item.get("title", "") or "").lower()
        topic = item.get("topic", "")
        summary = (item.get("summary", "") or "").lower()

        # +10 points αν το topic ταιριάζει
        if topic and topic in topics:
            score += 10

        # +5 points για κάθε keyword στον τίτλο
        for kw in keywords:
            if kw in title:
                score += 5

        # +2 points για κάθε keyword στο summary
        for kw in keywords:
            if kw in summary:
                score += 2

        # Κράτα μόνο αν έχει score > 0
        if score > 0:
            scored_items.append((score, item))

    # Sort by score (descending)
    scored_items.sort(key=lambda x: x[0], reverse=True)

    # Return top results
    return [item for score, item in scored_items]

def is_ai_search_enabled() -> bool:
    """Επιστρέφει True αν το AI search είναι enabled"""
    return AI_SEARCH_ENABLED

def get_search_status() -> dict:
    """Επιστρέφει status του AI search"""
    return {
        "enabled": AI_SEARCH_ENABLED,
        "mode": "openai" if AI_SEARCH_ENABLED else "keyword",
        "message": "AI search active" if AI_SEARCH_ENABLED else "Keyword-based search (set AI_SEARCH_ENABLED=true to enable AI)"
    }
