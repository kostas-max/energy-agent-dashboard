"""
AI-Powered Topic Discovery System
Αυτόματη ανακάλυψη trending topics και δημιουργία smart search queries
"""

import os
import time
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from dotenv import load_dotenv

load_dotenv()

def get_openai_client():
    """Δημιουργία OpenAI client με proper proxy handling"""
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        return None

    try:
        import httpx
        from openai import OpenAI

        # Disable proxies που μπορεί να προκαλούν προβλήματα
        http_client = httpx.Client(proxies=None, timeout=60.0)
        client = OpenAI(api_key=api_key, http_client=http_client)
        return client
    except Exception as e:
        print(f"[ERROR] Αδυναμία δημιουργίας OpenAI client: {e}")
        return None


def analyze_trending_topics(recent_articles: List[Dict]) -> List[Dict]:
    """
    Αναλύει πρόσφατα άρθρα και ανιχνεύει trending topics με AI

    Args:
        recent_articles: List με άρθρα (title, summary, date)

    Returns:
        List με trending topics [{topic, importance, keywords, suggested_queries}]
    """
    client = get_openai_client()
    if not client or not recent_articles:
        return []

    try:
        # Δημιουργία summary από τα άρθρα
        articles_text = "\n".join([
            f"- {art.get('title', '')}: {art.get('summary', '')[:100]}"
            for art in recent_articles[:30]  # Top 30 πρόσφατα
        ])

        prompt = f"""Ανάλυσε τα παρακάτω άρθρα ενέργειας και βρες τα TOP 5 trending topics:

{articles_text}

Για κάθε topic δώσε:
1. Όνομα topic (π.χ. "Νέο πρόγραμμα φωτοβολταϊκών")
2. Importance (1-10)
3. Keywords (comma-separated)
4. 2-3 suggested search queries

Απάντησε σε JSON format:
[
  {{
    "topic": "...",
    "importance": 8,
    "keywords": "φωτοβολταϊκά, επιδότηση, 2025",
    "queries": ["νέα προγράμματα φωτοβολταϊκών 2025", "επιδότηση φωτοβολταϊκών"]
  }}
]"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1000,
            response_format={"type": "json_object"}
        )

        result_text = response.choices[0].message.content.strip()

        # Parse JSON response
        import json
        # Αν το response είναι wrapped σε object, πάρε το array
        parsed = json.loads(result_text)
        if isinstance(parsed, dict) and "topics" in parsed:
            topics = parsed["topics"]
        elif isinstance(parsed, list):
            topics = parsed
        else:
            # Fallback: ψάξε για array στο object
            topics = list(parsed.values())[0] if parsed else []

        print(f"[AI] Βρέθηκαν {len(topics)} trending topics")
        return topics

    except Exception as e:
        print(f"[ERROR] AI topic analysis failed: {e}")
        return []


def discover_new_topics_from_web() -> List[str]:
    """
    Χρησιμοποιεί AI για να ανακαλύψει νέα θέματα από energy news sites

    Returns:
        List με suggested search queries
    """
    client = get_openai_client()
    if not client:
        return []

    try:
        today = datetime.now().strftime("%Y-%m-%d")

        prompt = f"""Σήμερα είναι {today}. Δημιούργησε 10 smart search queries για energy news στην Ελλάδα.

Εστίασε σε:
1. Νέα προγράμματα επιδοτήσεων (φωτοβολταϊκά, αντλίες θερμότητας, μονώσεις)
2. Αλλαγές στη νομοθεσία (net metering, net billing, ΡΑΕ)
3. Νέες τεχνολογίες (μπαταρίες, smart home, IoT)
4. Market updates (τιμές ενέργειας, προμηθευτές)
5. Προθεσμίες και παρατάσεις προγραμμάτων

Απάντησε ΜΟΝΟ με τα queries, ένα ανά γραμμή, χωρίς numbering."""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=300
        )

        queries_text = response.choices[0].message.content.strip()
        queries = [q.strip() for q in queries_text.split('\n') if q.strip()]

        # Καθαρισμός από numbering αν υπάρχει
        cleaned_queries = []
        for q in queries:
            # Remove "1. ", "- ", etc.
            import re
            cleaned = re.sub(r'^\d+[\.\)]\s*', '', q)
            cleaned = re.sub(r'^[-•]\s*', '', cleaned)
            if cleaned:
                cleaned_queries.append(cleaned)

        print(f"[AI] Generated {len(cleaned_queries)} new search queries")
        return cleaned_queries[:10]

    except Exception as e:
        print(f"[ERROR] AI topic discovery failed: {e}")
        return []


def generate_smart_queries_for_topic(topic: str, context: str = "") -> List[str]:
    """
    Δημιουργεί smart search queries για ένα συγκεκριμένο topic

    Args:
        topic: Το θέμα (π.χ. "φωτοβολταϊκά")
        context: Extra context (προαιρετικό)

    Returns:
        List με search queries
    """
    client = get_openai_client()
    if not client:
        # Fallback σε basic queries
        return [
            f"{topic} νέα",
            f"{topic} προγράμματα 2025",
            f"{topic} επιδότηση ελλάδα"
        ]

    try:
        prompt = f"""Δημιούργησε 5 search queries για Google/DuckDuckGo σχετικά με: "{topic}"

{f"Context: {context}" if context else ""}

Οι queries πρέπει να βρίσκουν:
- Πρόσφατα νέα και ανακοινώσεις
- Νέα προγράμματα και επιδοτήσεις
- Αλλαγές στη νομοθεσία
- Προθεσμίες και παρατάσεις

Απάντησε ΜΟΝΟ με τα queries, ένα ανά γραμμή."""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=200
        )

        queries_text = response.choices[0].message.content.strip()
        queries = [q.strip() for q in queries_text.split('\n') if q.strip()]

        # Καθαρισμός
        import re
        cleaned = []
        for q in queries:
            q = re.sub(r'^\d+[\.\)]\s*', '', q)
            q = re.sub(r'^[-•]\s*', '', q)
            if q:
                cleaned.append(q)

        return cleaned[:5]

    except Exception as e:
        print(f"[ERROR] Query generation failed: {e}")
        return [f"{topic} νέα", f"{topic} 2025"]


def get_recent_articles_from_db(days: int = 7, limit: int = 50) -> List[Dict]:
    """Ανάκτηση πρόσφατων άρθρων από τη βάση για analysis"""
    from db import fetch_news
    import sqlite3
    from datetime import datetime, timedelta

    try:
        all_news = fetch_news()

        # Φιλτράρισμα για τις τελευταίες X μέρες
        cutoff_date = datetime.now() - timedelta(days=days)

        recent = []
        for article in all_news:
            try:
                # Parse date
                date_str = article.get('date', '')
                if date_str:
                    # Handle different date formats
                    for fmt in ['%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S']:
                        try:
                            article_date = datetime.strptime(date_str[:19], fmt)
                            if article_date >= cutoff_date:
                                recent.append(article)
                            break
                        except:
                            continue
            except:
                continue

        return recent[:limit]

    except Exception as e:
        print(f"[ERROR] Failed to fetch recent articles: {e}")
        return []


def run_ai_topic_discovery_and_search(max_queries: int = 5) -> Dict:
    """
    Main function: Ανακαλύπτει topics και κάνει automatic search

    Returns:
        Dict με results summary
    """
    print(f"\n{'='*60}")
    print("AI-POWERED TOPIC DISCOVERY & SMART SEARCH")
    print(f"{'='*60}\n")

    results = {
        "trending_topics": [],
        "new_queries": [],
        "total_articles_found": 0,
        "timestamp": datetime.now().isoformat()
    }

    # Step 1: Ανάλυση trending topics από existing articles
    print("[1/3] Analyzing recent articles for trending topics...")
    recent_articles = get_recent_articles_from_db(days=7, limit=50)

    if recent_articles:
        trending = analyze_trending_topics(recent_articles)
        results["trending_topics"] = trending
        print(f"[OK] Found {len(trending)} trending topics")

        for topic in trending:
            print(f"  - {topic.get('topic', 'Unknown')} (importance: {topic.get('importance', 0)})")
    else:
        print("[INFO] No recent articles found, skipping trending analysis")

    # Step 2: AI-generated new search queries
    print("\n[2/3] Discovering new topics with AI...")
    new_queries = discover_new_topics_from_web()
    results["new_queries"] = new_queries

    if new_queries:
        print(f"[OK] Generated {len(new_queries)} new search queries:")
        for i, q in enumerate(new_queries[:5], 1):
            print(f"  {i}. {q}")

    # Step 3: Execute smart searches
    print(f"\n[3/3] Executing smart searches (top {max_queries} queries)...")

    from smart_search import smart_web_search, save_search_results_to_db

    # Combine queries from trending + new discoveries
    all_queries = []

    # Από trending topics
    for topic in results["trending_topics"][:3]:
        topic_queries = topic.get("queries", [])
        all_queries.extend(topic_queries[:2])

    # Από AI discoveries
    all_queries.extend(new_queries[:max_queries])

    # Execute searches
    total_saved = 0
    for query in all_queries[:max_queries]:
        try:
            print(f"\n  Searching: '{query}'...")
            search_results = smart_web_search(query, max_results=5, use_ai_filter=True)

            if search_results:
                saved = save_search_results_to_db(search_results, query=query)
                total_saved += saved
                print(f"    → Found and saved {saved} new articles")
            else:
                print(f"    → No results found")

            time.sleep(2)  # Rate limiting

        except Exception as e:
            print(f"    → Error: {e}")
            continue

    results["total_articles_found"] = total_saved

    print(f"\n{'='*60}")
    print(f"SUMMARY: Found {total_saved} new articles from {max_queries} AI-generated queries")
    print(f"{'='*60}\n")

    return results


def schedule_ai_discovery():
    """Προσθήκη AI discovery στον scheduler (optional)"""
    from apscheduler.schedulers.background import BackgroundScheduler

    scheduler = BackgroundScheduler()

    # Run AI discovery 1x per day (at 09:00)
    scheduler.add_job(
        run_ai_topic_discovery_and_search,
        "cron",
        hour=9,
        id="ai_discovery_job",
        kwargs={"max_queries": 5}
    )

    scheduler.start()
    print("[OK] AI Topic Discovery scheduled (daily at 09:00)")

    return scheduler
