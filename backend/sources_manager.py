
import os, sqlite3, requests
from db import SOURCES_DB

def init_sources_table():
    conn = sqlite3.connect(SOURCES_DB)
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS sources (id INTEGER PRIMARY KEY AUTOINCREMENT, url TEXT UNIQUE, type TEXT, last_check TEXT)")
    conn.commit()
    conn.close()

def detect_source_type(url: str) -> str:
    try:
        r = requests.get(url, timeout=8)
        ct = r.headers.get("content-type","").lower()
        if "xml" in ct or "<rss" in r.text.lower():
            return "RSS"
        if "application/json" in ct or "api" in url.lower():
            return "API"
        if "<html" in r.text.lower():
            return "HTML"
    except Exception:
        pass
    return "unknown"

def add_source(url: str) -> str:
    if not url or not url.strip():
        return "[ERROR] Το URL δεν μπορεί να είναι κενό."

    url = url.strip()
    if not url.startswith(("http://", "https://")):
        return "[ERROR] Το URL πρέπει να ξεκινάει με http:// ή https://"

    try:
        init_sources_table()
        typ = detect_source_type(url)
        conn = sqlite3.connect(SOURCES_DB)
        cur = conn.cursor()

        # Έλεγχος αν υπάρχει ήδη
        cur.execute("SELECT 1 FROM sources WHERE url=?", (url,))
        if cur.fetchone():
            conn.close()
            return f"[WARNING] Η πηγή {url} υπάρχει ήδη."

        cur.execute("INSERT INTO sources (url,type) VALUES (?,?)", (url, typ))
        conn.commit()
        conn.close()
        return f"[OK] Προστέθηκε πηγή {url} ({typ})"
    except Exception as e:
        return f"[ERROR] Σφάλμα κατά την προσθήκη πηγής: {str(e)}"

def remove_source(url: str) -> str:
    if not url or not url.strip():
        return "[ERROR] Το URL δεν μπορεί να είναι κενό."

    try:
        conn = sqlite3.connect(SOURCES_DB)
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM sources WHERE url=?", (url.strip(),))
        if not cur.fetchone():
            conn.close()
            return f"[WARNING] Η πηγή {url} δεν βρέθηκε."

        cur.execute("DELETE FROM sources WHERE url=?", (url.strip(),))
        conn.commit()
        conn.close()
        return f"[OK] Αφαιρέθηκε η πηγή {url}"
    except Exception as e:
        return f"[ERROR] Σφάλμα κατά την αφαίρεση πηγής: {str(e)}"

def get_all_sources():
    try:
        init_sources_table()
        conn = sqlite3.connect(SOURCES_DB)
        cur = conn.cursor()
        cur.execute("SELECT url,type,last_check FROM sources ORDER BY url ASC")
        rows = cur.fetchall()
        conn.close()
        return [{"url": r[0], "type": r[1], "last_check": r[2]} for r in rows]
    except Exception as e:
        print(f"[ERROR] Σφάλμα κατά την ανάκτηση πηγών: {e}")
        return []
