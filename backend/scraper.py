
import os
import sqlite3
from datetime import datetime
import feedparser, requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from db import save_news_if_new, SOURCES_DB
from ai_summarizer import summarize_article

load_dotenv()

# Configuration: Fetch article content or use snippets only
FETCH_ARTICLE_CONTENT = os.getenv("FETCH_ARTICLE_CONTENT", "true").lower() == "true"

TOPIC_KEYWORDS = {
    "Φωτοβολταϊκά": ["φωτοβολταϊκά", "net metering", "net billing", "αυτοπαραγωγή"],
    "Μπαταρίες": ["μπαταρία", "αποθήκευση", "storage"],
    "Αντλίες": ["αντλία θερμότητας","θέρμανση","θερμότητα"],
    "Νομοθεσία": ["φεκ","νόμος","κανονισμός","απόφαση"],
    "Επιδοτήσεις": ["επιχορήγηση","πρόγραμμα","επιδοτηση","εσπα"],
    "Smart_Σπίτια": ["smart","iot","έξυπνο σπίτι","αισθητήρες"],
}

def guess_topic(title: str) -> str:
    t = (title or "").lower()
    for topic, kws in TOPIC_KEYWORDS.items():
        for kw in kws:
            if kw in t:
                return topic
    return ""

def fetch_article_content(url: str, max_chars: int = 2000) -> str:
    """
    Fetch το πραγματικό περιεχόμενο του άρθρου από το URL

    Args:
        url: Το URL του άρθρου
        max_chars: Μέγιστος αριθμός χαρακτήρων να επιστρέψει

    Returns:
        Το περιεχόμενο του άρθρου (καθαρισμένο κείμενο)
    """
    try:
        r = requests.get(url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        # Αφαίρεση scripts, styles, navigation, footer, etc.
        for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
            element.decompose()

        # Προσπάθησε να βρεις το main content
        # Πρώτα δοκίμασε κοινά selectors για article content
        main_content = None
        for selector in ['article', 'main', '.article-content', '.entry-content', '.post-content']:
            main_content = soup.select_one(selector)
            if main_content:
                break

        # Αν δεν βρήκε main content, πάρε όλο το body
        if not main_content:
            main_content = soup.find('body')

        if not main_content:
            return ""

        # Πάρε το κείμενο
        text = main_content.get_text()

        # Καθαρισμός: αφαίρεση extra whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines
                 for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)

        # Κράτα τους πρώτους max_chars χαρακτήρες
        return text[:max_chars]
    except Exception as e:
        print(f"[WARNING] Αδυναμία fetch content από {url}: {e}")
        return ""

def iter_sources():
    conn = sqlite3.connect(SOURCES_DB)
    cur = conn.cursor()
    cur.execute("SELECT url,type FROM sources")
    rows = cur.fetchall()
    conn.close()
    for url, typ in rows:
        yield url, (typ or "unknown")

def fetch_rss(url):
    try:
        feed = feedparser.parse(url)
        items = []
        for e in feed.entries[:20]:
            title = e.get("title", "").strip()
            link = e.get("link", "").strip()
            if not title or not link:
                continue
            date = e.get("published", "") or e.get("updated", "") or datetime.now().isoformat(timespec="seconds")
            items.append({"title": title, "url": link, "date": date})
        return items
    except Exception as e:
        print(f"[ERROR] Σφάλμα RSS fetch από {url}: {e}")
        return []

def fetch_html(url):
    items = []
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        for a in soup.select("a"):
            title = (a.get_text() or "").strip()
            href = a.get("href") or ""
            if not title or not href or len(title) < 8:
                continue
            if href.startswith("/"):
                from urllib.parse import urljoin
                href = urljoin(url, href)
            items.append({"title": title, "url": href, "date": datetime.now().isoformat(timespec="seconds")})
            if len(items) >= 20:
                break
    except Exception:
        pass
    return items

def fetch_api(url):
    items = []
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        if isinstance(data, list):
            seq = data[:20]
        elif isinstance(data, dict):
            seq = data.get("results") or data.get("data") or []
            if isinstance(seq, dict):
                seq = [seq]
            seq = seq[:20]
        else:
            seq = []
        for obj in seq:
            title = str(obj.get("title") or obj.get("name") or obj.get("subject") or "")[:200]
            link = obj.get("url") or obj.get("link") or ""
            date = obj.get("date") or obj.get("updated_at") or obj.get("published_at") or datetime.now().isoformat(timespec="seconds")
            if title:
                items.append({"title": title, "url": link, "date": date})
    except Exception:
        pass
    return items

def run_scraping():
    print("[INFO] Έναρξη scraping...")
    total_new = 0
    try:
        for url, typ in iter_sources():
            try:
                if "rss" in typ.lower():
                    items = fetch_rss(url)
                elif "api" in typ.lower():
                    items = fetch_api(url)
                else:
                    items = fetch_html(url)

                for it in items:
                    try:
                        title = it.get("title","")
                        article_url = it.get("url","")
                        if not title:
                            continue

                        topic = guess_topic(title)

                        # Fetch το πραγματικό περιεχόμενο του άρθρου για καλύτερη AI ανάλυση
                        # (αν είναι enabled στο .env)
                        article_content = ""
                        if FETCH_ARTICLE_CONTENT and article_url:
                            article_content = fetch_article_content(article_url)
                            print(f"[INFO] Fetched {len(article_content)} chars από {article_url[:50]}...")

                        # AI summarization με το πραγματικό content (αν υπάρχει)
                        summary = summarize_article(title, article_content) or ""
                        item = {
                            "title": title,
                            "url": it.get("url",""),
                            "date": it.get("date",""),
                            "source": url,
                            "topic": topic,
                            "summary": summary
                        }
                        if save_news_if_new(item):
                            total_new += 1
                    except Exception as e:
                        print(f"[WARNING] Σφάλμα κατά την αποθήκευση άρθρου: {e}")
                        continue
            except Exception as e:
                print(f"[WARNING] Σφάλμα κατά το scraping πηγής {url}: {e}")
                continue

        print(f"[OK] Scraping ολοκληρώθηκε. Νέα αντικείμενα: {total_new}")
    except Exception as e:
        print(f"[ERROR] Κρίσιμο σφάλμα στο scraping: {e}")
    return total_new

def search_on_demand(query: str) -> int:
    """
    Κάνει ΕΞΥΠΝΗ αναζήτηση στο web με AI filtering και αποθηκεύει τα αποτελέσματα.
    Χρησιμοποιεί DuckDuckGo και Google search με AI για να βρει σχετικά άρθρα.
    """
    print(f"[INFO] Smart Web Search query: {query}")

    try:
        from smart_search import smart_web_search, save_search_results_to_db

        # Κάνουμε έξυπνη αναζήτηση στο web
        results = smart_web_search(query, max_results=10, use_ai_filter=True)

        if not results:
            print(f"[INFO] Δεν βρέθηκαν αποτελέσματα για: '{query}'")
            return 0

        # Αποθηκεύουμε τα αποτελέσματα στη βάση
        saved_count = save_search_results_to_db(results, query=query)

        print(f"[OK] Smart Search: Βρέθηκαν και αποθηκεύτηκαν {saved_count} νέα άρθρα")
        return saved_count

    except Exception as e:
        print(f"[ERROR] Σφάλμα κατά το smart search: {e}")
        return 0
