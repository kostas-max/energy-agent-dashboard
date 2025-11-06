
import os
import time
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from ai_summarizer import summarize_article

# Predefined search topics με keywords
SMART_TOPICS = {
    "Φωτοβολταϊκά": [
        "φωτοβολταϊκά νέα",
        "net metering ελλάδα",
        "net billing πρόγραμμα",
        "αυτοπαραγωγή ενέργειας",
        "επιδότηση φωτοβολταϊκών",
        "παράταση φωτοβολταϊκών"
    ],
    "Αντλίες Θερμότητας": [
        "αντλίες θερμότητας νέα",
        "επιδότηση αντλιών θερμότητας",
        "θέρμανση ελλάδα",
        "heat pump greece",
        "πρόγραμμα εξοικονομώ"
    ],
    "Νομοθεσία": [
        "φεκ ενέργεια",
        "νόμος ενέργειας",
        "ρυθμίσεις ενέργειας",
        "rae νέα",
        "υπουργείο ενέργειας"
    ],
    "Επιδοτήσεις": [
        "επιχορήγηση ενέργεια",
        "εσπα ενέργεια",
        "πρόγραμμα επιδότησης",
        "παράταση προγράμματος",
        "εξοικονομώ κατ' οίκον"
    ],
    "Μπαταρίες": [
        "αποθήκευση ενέργειας",
        "battery storage greece",
        "μπαταρίες φωτοβολταϊκών",
        "energy storage"
    ]
}

def google_search(query: str, num_results: int = 10) -> list:
    """
    Κάνει Google search χρησιμοποιώντας web scraping.
    ΠΡΟΣΟΧΗ: Το Google μπορεί να μπλοκάρει το IP αν κάνεις πολλά requests.
    """
    results = []
    try:
        # Google search URL
        url = f"https://www.google.com/search?q={quote_plus(query)}&num={num_results}&hl=el"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Βρίσκουμε τα search results
        search_results = soup.find_all('div', class_='g')

        for result in search_results[:num_results]:
            try:
                # Τίτλος
                title_elem = result.find('h3')
                title = title_elem.get_text() if title_elem else ""

                # Link
                link_elem = result.find('a')
                link = link_elem.get('href') if link_elem else ""

                # Snippet (περιγραφή)
                snippet_elem = result.find('div', class_='VwiC3b')
                snippet = snippet_elem.get_text() if snippet_elem else ""

                if title and link:
                    results.append({
                        'title': title,
                        'url': link,
                        'snippet': snippet,
                        'date': datetime.now().isoformat(timespec='seconds')
                    })
            except Exception as e:
                print(f"[WARNING] Σφάλμα parsing result: {e}")
                continue

        # Rate limiting
        time.sleep(1)

    except Exception as e:
        print(f"[ERROR] Σφάλμα Google search: {e}")

    return results

def duckduckgo_search(query: str, num_results: int = 10) -> list:
    """
    Κάνει DuckDuckGo search (πιο φιλικό, δεν μπλοκάρει εύκολα).
    """
    results = []
    try:
        # DuckDuckGo HTML search
        url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # DuckDuckGo results
        search_results = soup.find_all('div', class_='result')

        for result in search_results[:num_results]:
            try:
                # Τίτλος
                title_elem = result.find('a', class_='result__a')
                title = title_elem.get_text() if title_elem else ""

                # Link
                link = title_elem.get('href') if title_elem else ""

                # Snippet
                snippet_elem = result.find('a', class_='result__snippet')
                snippet = snippet_elem.get_text() if snippet_elem else ""

                if title and link:
                    results.append({
                        'title': title,
                        'url': link,
                        'snippet': snippet,
                        'date': datetime.now().isoformat(timespec='seconds')
                    })
            except Exception as e:
                print(f"[WARNING] Σφάλμα parsing result: {e}")
                continue

        time.sleep(0.5)

    except Exception as e:
        print(f"[ERROR] Σφάλμα DuckDuckGo search: {e}")

    return results

def ai_filter_relevance(query: str, results: list, min_relevance: float = 0.6) -> list:
    """
    Χρησιμοποιεί AI για να φιλτράρει τα αποτελέσματα με βάση τη σχετικότητα.
    """
    api_key = os.getenv("OPENAI_API_KEY") or ""
    if not api_key or not results:
        return results

    try:
        from openai import OpenAI
        import httpx

        http_client = httpx.Client(proxies=None, timeout=30.0)
        client = OpenAI(api_key=api_key, http_client=http_client)

        filtered = []

        for result in results:
            try:
                # Ρωτάμε το AI αν το αποτέλεσμα είναι σχετικό
                prompt = f"""Είναι αυτό το άρθρο σχετικό με το query "{query}";

Τίτλος: {result.get('title', '')}
Περιγραφή: {result.get('snippet', '')}

Απάντησε ΜΟΝΟ με "ΝΑΙ" ή "ΟΧΙ"."""

                resp = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=10,
                    temperature=0
                )

                answer = resp.choices[0].message.content.strip().upper()

                if "ΝΑΙ" in answer or "YES" in answer:
                    filtered.append(result)

                time.sleep(0.2)  # Rate limiting

            except Exception as e:
                print(f"[WARNING] Σφάλμα AI filtering: {e}")
                # Αν αποτύχει το AI, κρατάμε το αποτέλεσμα
                filtered.append(result)
                continue

        http_client.close()
        return filtered

    except Exception as e:
        print(f"[ERROR] Σφάλμα AI filtering: {e}")
        return results

def smart_web_search(query: str, max_results: int = 10, use_ai_filter: bool = True) -> list:
    """
    Έξυπνη αναζήτηση στο web με AI filtering.
    """
    print(f"[INFO] Smart web search για: '{query}'")

    # Δοκιμάζουμε πρώτα DuckDuckGo (πιο φιλικό)
    results = duckduckgo_search(query, max_results * 2)

    # Αν δεν βρήκαμε αρκετά, δοκιμάζουμε Google
    if len(results) < 5:
        print(f"[INFO] Προσπάθεια με Google search...")
        google_results = google_search(query, max_results)
        results.extend(google_results)

    print(f"[INFO] Βρέθηκαν {len(results)} αποτελέσματα")

    # AI filtering για να κρατήσουμε μόνο σχετικά
    if use_ai_filter and results:
        print(f"[INFO] Φιλτράρισμα με AI...")
        results = ai_filter_relevance(query, results)
        print(f"[INFO] Μετά το filtering: {len(results)} σχετικά αποτελέσματα")

    return results[:max_results]

def search_by_topics(topics: list = None, max_per_topic: int = 5) -> dict:
    """
    Αναζήτηση με βάση predefined topics.

    Args:
        topics: List με topic names (π.χ. ["Φωτοβολταϊκά", "Αντλίες Θερμότητας"])
                Αν None, ψάχνει όλα τα topics.
        max_per_topic: Μέγιστος αριθμός αποτελεσμάτων ανά topic

    Returns:
        Dict με topic -> results mapping
    """
    if topics is None:
        topics = list(SMART_TOPICS.keys())

    all_results = {}

    for topic in topics:
        if topic not in SMART_TOPICS:
            print(f"[WARNING] Άγνωστο topic: {topic}")
            continue

        print(f"\n[INFO] === Αναζήτηση για topic: {topic} ===")
        topic_results = []

        # Ψάχνουμε με όλα τα keywords του topic
        for keyword in SMART_TOPICS[topic][:3]:  # Top 3 keywords ανά topic
            print(f"[INFO] Keyword: {keyword}")
            results = smart_web_search(keyword, max_results=3, use_ai_filter=True)
            topic_results.extend(results)
            time.sleep(1)  # Rate limiting

        # Αφαιρούμε duplicates (με βάση το URL)
        seen_urls = set()
        unique_results = []
        for r in topic_results:
            url = r.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(r)

        all_results[topic] = unique_results[:max_per_topic]
        print(f"[INFO] Βρέθηκαν {len(all_results[topic])} μοναδικά αποτελέσματα για {topic}")

    return all_results

def save_search_results_to_db(results: list, query: str = "", topic: str = "", fetch_content: bool = True) -> int:
    """
    Αποθηκεύει τα search results στη βάση δεδομένων.

    Args:
        results: List με search results
        query: Το query που χρησιμοποιήθηκε
        topic: Το topic (optional)
        fetch_content: Αν True, κάνει fetch το πραγματικό content για καλύτερη AI ανάλυση
    """
    from db import save_news_if_new
    from scraper import fetch_article_content

    saved_count = 0

    for result in results:
        try:
            title = result.get('title', '')
            url = result.get('url', '')
            snippet = result.get('snippet', '')

            if not title or not url:
                continue

            # Fetch το πραγματικό περιεχόμενο αν ζητηθεί
            content = ""
            if fetch_content:
                content = fetch_article_content(url)
                print(f"[INFO] Fetched {len(content)} chars από {url[:50]}...")

            # Δημιουργία AI summary με το πραγματικό content (αν υπάρχει) ή το snippet
            summary = summarize_article(title, content or snippet) or snippet

            item = {
                'title': title,
                'url': url,
                'date': result.get('date', datetime.now().isoformat(timespec='seconds')),
                'source': f'Smart Search: {query or topic}',
                'topic': topic or 'Γενικά',
                'summary': summary
            }

            if save_news_if_new(item):
                saved_count += 1

        except Exception as e:
            print(f"[WARNING] Σφάλμα αποθήκευσης result: {e}")
            continue

    return saved_count
