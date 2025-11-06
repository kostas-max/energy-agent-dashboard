
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from scheduler import start_scheduler
from agent_core import handle_prompt
from db import init_all

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_all()
    start_scheduler()
    yield
    # Shutdown (αν χρειαστεί στο μέλλον)

app = FastAPI(title="Energy Agent Dashboard (GR)", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/prompt")
async def run_prompt(data: dict):
    prompt = data.get("prompt", "")
    result = handle_prompt(prompt)

    # handle_prompt τώρα επιστρέφει dict με reply και conversation_id
    if isinstance(result, dict):
        return result
    else:
        # Fallback αν επιστρέφει string (για backward compatibility)
        return {"reply": result}

@app.get("/sources")
async def list_sources():
    from sources_manager import get_all_sources
    return {"sources": get_all_sources()}

@app.post("/sources/add")
async def add_source_api(data: dict):
    from sources_manager import add_source
    url = data.get("url", "").strip()
    return {"result": add_source(url)}

@app.post("/sources/remove")
async def remove_source_api(data: dict):
    from sources_manager import remove_source
    url = data.get("url", "").strip()
    return {"result": remove_source(url)}

@app.get("/news")
async def list_news():
    from db import fetch_news
    return {"news": fetch_news()}

@app.get("/saved")
async def list_saved():
    from db import fetch_saved
    return {"news": fetch_saved()}

@app.post("/scrape/manual")
async def manual_scrape():
    """
    Manual scraping όλων των πηγών.
    ΠΡΟΣΟΧΗ: Θα χρεώσει το OpenAI API για AI summarization!
    """
    from scraper import run_scraping
    try:
        total_new = run_scraping()
        return {
            "success": True,
            "new_articles": total_new,
            "message": f"Scraping ολοκληρώθηκε. Βρέθηκαν {total_new} νέα άρθρα."
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Σφάλμα κατά το scraping: {str(e)}"
        }

@app.post("/scrape/smart")
async def smart_scrape(data: dict):
    """
    Smart scraping με predefined topics ή custom keywords.
    ΠΡΟΣΟΧΗ: Θα χρεώσει το OpenAI API για AI filtering και summarization!
    """
    from smart_search import search_by_topics, save_search_results_to_db, SMART_TOPICS

    try:
        # Αν δίνονται topics, χρησιμοποιούμε αυτά, αλλιώς όλα
        topics = data.get("topics", None)  # π.χ. ["Φωτοβολταϊκά", "Αντλίες Θερμότητας"]
        max_per_topic = data.get("max_per_topic", 5)

        if topics is None:
            # Χρησιμοποιούμε όλα τα predefined topics
            topics = list(SMART_TOPICS.keys())

        print(f"[INFO] Smart scraping για topics: {topics}")

        # Κάνουμε smart search για κάθε topic
        all_results = search_by_topics(topics, max_per_topic)

        # Αποθηκεύουμε όλα τα αποτελέσματα
        total_saved = 0
        for topic, results in all_results.items():
            saved = save_search_results_to_db(results, topic=topic)
            total_saved += saved
            print(f"[INFO] Topic '{topic}': Αποθηκεύτηκαν {saved}/{len(results)} άρθρα")

        return {
            "success": True,
            "total_articles": total_saved,
            "results_by_topic": {topic: len(results) for topic, results in all_results.items()},
            "message": f"Smart scraping ολοκληρώθηκε. Βρέθηκαν {total_saved} νέα άρθρα σε {len(all_results)} topics."
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Σφάλμα κατά το smart scraping: {str(e)}"
        }

@app.get("/scrape/topics")
async def get_smart_topics():
    """Επιστρέφει τα διαθέσιμα predefined topics για smart search"""
    from smart_search import SMART_TOPICS
    return {
        "topics": list(SMART_TOPICS.keys()),
        "details": SMART_TOPICS
    }

@app.post("/scrape/ai-discovery")
async def ai_topic_discovery(data: dict):
    """
    AI-Powered Topic Discovery & Smart Search
    Χρησιμοποιεί AI για να ανακαλύψει trending topics και να κάνει automatic search
    ΠΡΟΣΟΧΗ: Θα χρεώσει το OpenAI API!
    """
    from ai_topic_discovery import run_ai_topic_discovery_and_search

    try:
        max_queries = data.get("max_queries", 5)

        print(f"[INFO] Starting AI topic discovery with max_queries={max_queries}")

        # Run AI discovery
        results = run_ai_topic_discovery_and_search(max_queries=max_queries)

        return {
            "success": True,
            "trending_topics": results.get("trending_topics", []),
            "new_queries": results.get("new_queries", []),
            "total_articles_found": results.get("total_articles_found", 0),
            "message": f"AI Discovery ολοκληρώθηκε. Βρέθηκαν {results.get('total_articles_found', 0)} νέα άρθρα."
        }
    except Exception as e:
        print(f"[ERROR] AI discovery failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": f"Σφάλμα κατά το AI discovery: {str(e)}"
        }

@app.get("/scrape/trending-topics")
async def get_trending_topics():
    """
    Επιστρέφει trending topics από τα πρόσφατα άρθρα χρησιμοποιώντας AI
    """
    from ai_topic_discovery import get_recent_articles_from_db, analyze_trending_topics

    try:
        recent_articles = get_recent_articles_from_db(days=7, limit=50)

        if not recent_articles:
            return {
                "success": False,
                "message": "Δεν βρέθηκαν πρόσφατα άρθρα",
                "topics": []
            }

        trending = analyze_trending_topics(recent_articles)

        return {
            "success": True,
            "total_articles_analyzed": len(recent_articles),
            "topics": trending
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "topics": []
        }

@app.post("/scrape/generate-queries")
async def generate_smart_queries(data: dict):
    """
    Δημιουργεί smart search queries για ένα topic χρησιμοποιώντας AI
    """
    from ai_topic_discovery import generate_smart_queries_for_topic

    try:
        topic = data.get("topic", "").strip()
        context = data.get("context", "")

        if not topic:
            return {"error": "Topic is required", "queries": []}

        queries = generate_smart_queries_for_topic(topic, context)

        return {
            "success": True,
            "topic": topic,
            "queries": queries
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "queries": []
        }

@app.get("/api-usage")
async def get_api_usage():
    """Επιστρέφει τη χρήση του AI summarizer για σήμερα"""
    from ai_summarizer import check_api_quota, MAX_DAILY_SECONDS
    used_seconds = check_api_quota()
    remaining_seconds = max(0, MAX_DAILY_SECONDS - used_seconds)
    return {
        "max_daily_seconds": MAX_DAILY_SECONDS,
        "max_daily_minutes": MAX_DAILY_SECONDS / 60,
        "used_seconds": round(used_seconds, 2),
        "used_minutes": round(used_seconds / 60, 2),
        "remaining_seconds": round(remaining_seconds, 2),
        "remaining_minutes": round(remaining_seconds / 60, 2),
        "quota_exceeded": used_seconds >= MAX_DAILY_SECONDS
    }

@app.post("/search/smart")
async def smart_search(data: dict):
    """AI-powered smart search με φιλτράρισμα"""
    from db import fetch_news
    from ai_search import filter_results_by_relevance, classify_query_with_ai

    query = data.get("query", "").strip()
    if not query:
        return {"error": "Query is required", "results": []}

    # Ανάλυση query
    query_analysis = classify_query_with_ai(query)

    # Fetch όλα τα νέα
    all_news = fetch_news()

    # Φιλτράρισμα με AI
    filtered_news = filter_results_by_relevance(query, all_news)

    return {
        "query": query,
        "analysis": query_analysis,
        "total_results": len(all_news),
        "filtered_results": len(filtered_news),
        "results": filtered_news[:50]  # Top 50
    }

@app.get("/search/status")
async def search_status():
    """Επιστρέφει το status του AI search"""
    from ai_search import get_search_status
    return get_search_status()

@app.post("/search/toggle")
async def toggle_ai_search(data: dict):
    """Toggle AI search on/off by updating .env file"""
    import os
    from pathlib import Path

    try:
        enabled = data.get("enabled", False)
        env_path = Path(__file__).parent.parent / ".env"

        # Read current .env
        if env_path.exists():
            with open(env_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        else:
            lines = []

        # Update or add AI_SEARCH_ENABLED line
        found = False
        new_lines = []
        for line in lines:
            if line.strip().startswith("AI_SEARCH_ENABLED="):
                new_lines.append(f"AI_SEARCH_ENABLED={'true' if enabled else 'false'}\n")
                found = True
            else:
                new_lines.append(line)

        # If not found, add it
        if not found:
            new_lines.append(f"\nAI_SEARCH_ENABLED={'true' if enabled else 'false'}\n")

        # Write back to .env
        with open(env_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

        # Update environment variable for current process
        os.environ["AI_SEARCH_ENABLED"] = "true" if enabled else "false"

        return {
            "success": True,
            "enabled": enabled,
            "message": f"AI Search {'ενεργοποιήθηκε' if enabled else 'απενεργοποιήθηκε'}. Κάνε restart τον backend για πλήρη εφαρμογή."
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

# ===========================
# Notes API Endpoints
# ===========================

@app.post("/notes/add")
async def add_note_api(data: dict):
    """Προσθήκη νέας σημείωσης"""
    from notes_manager import add_note
    return add_note(
        title=data.get("title", ""),
        content=data.get("content", ""),
        category=data.get("category", ""),
        tags=data.get("tags", [])
    )

@app.get("/notes")
async def get_notes_api(category: str = None, tag: str = None, pinned_only: bool = False):
    """Ανάκτηση όλων των σημειώσεων με προαιρετικά φίλτρα"""
    from notes_manager import get_all_notes
    return {"notes": get_all_notes(category, tag, pinned_only)}

@app.post("/notes/update")
async def update_note_api(data: dict):
    """Ενημέρωση υπάρχουσας σημείωσης"""
    from notes_manager import update_note
    return update_note(
        note_id=data.get("id"),
        title=data.get("title"),
        content=data.get("content"),
        category=data.get("category"),
        tags=data.get("tags")
    )

@app.post("/notes/delete")
async def delete_note_api(data: dict):
    """Διαγραφή σημείωσης"""
    from notes_manager import delete_note
    return delete_note(data.get("id"))

@app.post("/notes/toggle-pin")
async def toggle_pin_api(data: dict):
    """Toggle pin status σημείωσης"""
    from notes_manager import toggle_pin
    return toggle_pin(data.get("id"))

@app.get("/notes/categories")
async def get_categories_api():
    """Επιστρέφει όλες τις μοναδικές κατηγορίες"""
    from notes_manager import get_categories
    return {"categories": get_categories()}

@app.get("/notes/tags")
async def get_tags_api():
    """Επιστρέφει όλα τα μοναδικά tags"""
    from notes_manager import get_all_tags
    return {"tags": get_all_tags()}

@app.post("/notes/generate-summary")
async def generate_note_summary(data: dict):
    """Δημιουργία AI περίληψης για σημείωση από νέο"""
    from ai_summarizer import summarize_article

    try:
        title = data.get("title", "")
        summary = data.get("summary", "")
        topic = data.get("topic", "")

        # Δημιουργία πλούσιου context για περίληψη
        content = f"Θέμα: {topic}\n" if topic else ""
        content += summary if summary else ""

        # Χρήση της υπάρχουσας summarize_article function
        ai_summary = summarize_article(title, content)

        if ai_summary:
            return {
                "success": True,
                "ai_summary": ai_summary
            }
        else:
            return {
                "error": "Δεν ήταν δυνατή η δημιουργία περίληψης. Ελέγξτε το API key ή το όριο χρήσης.",
                "ai_summary": ""
            }

    except Exception as e:
        print(f"[ERROR] Σφάλμα κατά τη δημιουργία AI περίληψης: {e}")
        return {"error": f"Σφάλμα: {str(e)}", "ai_summary": ""}

# ===========================
# Conversation API Endpoints
# ===========================

@app.get("/conversations/history")
async def get_conversation_history_api(limit: int = 20):
    """Ανάκτηση conversation history"""
    from conversation_manager import get_conversation_history
    try:
        history = get_conversation_history(limit=limit)
        return {"history": history}
    except Exception as e:
        return {"error": str(e), "history": []}

@app.post("/conversations/rate")
async def rate_conversation_api(data: dict):
    """Rating συνομιλίας (1-5 stars)"""
    from conversation_manager import rate_conversation
    try:
        conversation_id = data.get("conversation_id")
        rating = data.get("rating")
        feedback = data.get("feedback", None)

        if not conversation_id or not rating:
            return {"success": False, "error": "conversation_id και rating είναι απαραίτητα"}

        if not (1 <= rating <= 5):
            return {"success": False, "error": "Rating πρέπει να είναι 1-5"}

        rate_conversation(conversation_id, rating, feedback)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/conversations/analytics")
async def get_conversation_analytics():
    """Επιστρέφει analytics για AI usage (cost, tokens, ratings)"""
    from conversation_manager import get_analytics
    try:
        analytics = get_analytics()
        return analytics
    except Exception as e:
        return {"error": str(e)}

@app.get("/conversations/export")
async def export_conversations_dataset(min_rating: int = None):
    """Export conversations ως dataset για fine-tuning"""
    from conversation_manager import get_dataset_export
    try:
        dataset = get_dataset_export(min_rating=min_rating)
        return {"dataset": dataset, "count": len(dataset)}
    except Exception as e:
        return {"error": str(e), "dataset": []}

if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("Energy Agent Dashboard - Starting...")
    print("=" * 60)
    print("Server: http://localhost:8000")
    print("Frontend: Open frontend/index.html in browser")
    print("Scheduler: Active (08:00 & 20:00)")
    print("\nPress CTRL+C to stop\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
