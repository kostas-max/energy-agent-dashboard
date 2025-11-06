
import os, sqlite3

BASE = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE, "data")
NEWS_DB = os.path.join(DATA_DIR, "news.db")
SOURCES_DB = os.path.join(DATA_DIR, "sources.db")
PROMPTS_DB = os.path.join(DATA_DIR, "prompts.db")

def init_all():
    os.makedirs(DATA_DIR, exist_ok=True)
    for path, schema in [
        (NEWS_DB, """
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            url TEXT UNIQUE,
            date TEXT,
            source TEXT,
            topic TEXT,
            summary TEXT,
            saved INTEGER DEFAULT 0
        );
        """),
        (SOURCES_DB, """
        CREATE TABLE IF NOT EXISTS sources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE,
            type TEXT,
            last_check TEXT
        );
        """),
        (PROMPTS_DB, """
        CREATE TABLE IF NOT EXISTS prompts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT,
            prompt TEXT
        );
        """),
    ]:
        conn = sqlite3.connect(path)
        cur = conn.cursor()
        cur.executescript(schema)
        conn.commit()
        conn.close()

def save_prompt(prompt: str):
    conn = sqlite3.connect(PROMPTS_DB)
    cur = conn.cursor()
    from datetime import datetime
    cur.execute("INSERT INTO prompts (ts,prompt) VALUES (?,?)",
                (datetime.now().isoformat(timespec="seconds"), prompt))
    conn.commit()
    conn.close()

def news_exists(url: str) -> bool:
    conn = sqlite3.connect(NEWS_DB)
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM news WHERE url=?", (url,))
    res = cur.fetchone() is not None
    conn.close()
    return res

def save_news_if_new(item: dict) -> bool:
    if news_exists(item.get("url","")):
        return False
    conn = sqlite3.connect(NEWS_DB)
    cur = conn.cursor()
    cur.execute("INSERT INTO news (title,url,date,source,topic,summary,saved) VALUES (?,?,?,?,?,?,?)",
                (item.get("title"), item.get("url"), item.get("date"), item.get("source"),
                 item.get("topic"), item.get("summary"), 0))
    conn.commit()
    conn.close()
    return True

def mark_saved(url: str):
    conn = sqlite3.connect(NEWS_DB)
    cur = conn.cursor()
    cur.execute("UPDATE news SET saved=1 WHERE url=?", (url,))
    conn.commit()
    conn.close()

def fetch_news(limit: int = 200):
    try:
        conn = sqlite3.connect(NEWS_DB)
        cur = conn.cursor()
        cur.execute("SELECT title,url,date,source,topic,summary,saved FROM news ORDER BY date DESC LIMIT ?", (limit,))
        rows = cur.fetchall()
        conn.close()
        return [{
            "title": r[0], "url": r[1], "date": r[2], "source": r[3],
            "topic": r[4], "summary": r[5], "saved": bool(r[6])
        } for r in rows]
    except Exception as e:
        print(f"[ERROR] Σφάλμα κατά την ανάκτηση ειδήσεων: {e}")
        return []

def fetch_saved():
    try:
        conn = sqlite3.connect(NEWS_DB)
        cur = conn.cursor()
        cur.execute("SELECT title,url,date,source,topic,summary,saved FROM news WHERE saved=1 ORDER BY date DESC")
        rows = cur.fetchall()
        conn.close()
        return [{
            "title": r[0], "url": r[1], "date": r[2], "source": r[3],
            "topic": r[4], "summary": r[5], "saved": bool(r[6])
        } for r in rows]
    except Exception as e:
        print(f"[ERROR] Σφάλμα κατά την ανάκτηση αποθηκευμένων: {e}")
        return []
