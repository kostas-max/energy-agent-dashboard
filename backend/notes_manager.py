"""
Notes Manager - Σημειωματάριο με κατηγορίες και tags
"""

import sqlite3
from datetime import datetime
import os

# Database path
NOTES_DB = os.path.join(os.path.dirname(__file__), "..", "data", "notes.db")

def init_notes_table():
    """Δημιουργία πίνακα notes αν δεν υπάρχει"""
    conn = sqlite3.connect(NOTES_DB)
    cur = conn.cursor()

    # Notes table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT,
            category TEXT,
            tags TEXT,
            created_at TEXT,
            updated_at TEXT,
            pinned INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()

def add_note(title: str, content: str = "", category: str = "", tags: list = None) -> dict:
    """
    Προσθήκη νέας σημείωσης

    Args:
        title: Τίτλος σημείωσης
        content: Περιεχόμενο
        category: Κατηγορία (π.χ. "Έργα", "Ιδέες", "TODO")
        tags: List από tags (π.χ. ["επείγον", "φωτοβολταϊκά"])

    Returns:
        dict με το note που δημιουργήθηκε
    """
    if not title or not title.strip():
        return {"error": "Ο τίτλος είναι υποχρεωτικός"}

    try:
        init_notes_table()
        conn = sqlite3.connect(NOTES_DB)
        cur = conn.cursor()

        now = datetime.now().isoformat()
        tags_str = ",".join(tags) if tags else ""

        cur.execute("""
            INSERT INTO notes (title, content, category, tags, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (title.strip(), content.strip(), category.strip(), tags_str, now, now))

        note_id = cur.lastrowid
        conn.commit()
        conn.close()

        return {
            "id": note_id,
            "title": title,
            "content": content,
            "category": category,
            "tags": tags or [],
            "created_at": now,
            "updated_at": now,
            "pinned": False
        }
    except Exception as e:
        return {"error": f"Σφάλμα κατά την προσθήκη σημείωσης: {str(e)}"}

def get_all_notes(category: str = None, tag: str = None, pinned_only: bool = False) -> list:
    """
    Ανάκτηση όλων των σημειώσεων με προαιρετικά φίλτρα

    Args:
        category: Φιλτράρισμα ανά κατηγορία
        tag: Φιλτράρισμα ανά tag
        pinned_only: Μόνο pinned σημειώσεις

    Returns:
        list από notes
    """
    try:
        init_notes_table()
        conn = sqlite3.connect(NOTES_DB)
        cur = conn.cursor()

        query = "SELECT id, title, content, category, tags, created_at, updated_at, pinned FROM notes WHERE 1=1"
        params = []

        if category:
            query += " AND category = ?"
            params.append(category)

        if tag:
            query += " AND tags LIKE ?"
            params.append(f"%{tag}%")

        if pinned_only:
            query += " AND pinned = 1"

        query += " ORDER BY pinned DESC, updated_at DESC"

        cur.execute(query, params)
        rows = cur.fetchall()
        conn.close()

        notes = []
        for row in rows:
            notes.append({
                "id": row[0],
                "title": row[1],
                "content": row[2],
                "category": row[3],
                "tags": row[4].split(",") if row[4] else [],
                "created_at": row[5],
                "updated_at": row[6],
                "pinned": bool(row[7])
            })

        return notes
    except Exception as e:
        print(f"[ERROR] Σφάλμα κατά την ανάκτηση σημειώσεων: {e}")
        return []

def update_note(note_id: int, title: str = None, content: str = None,
                category: str = None, tags: list = None) -> dict:
    """Ενημέρωση υπάρχουσας σημείωσης"""
    try:
        conn = sqlite3.connect(NOTES_DB)
        cur = conn.cursor()

        # Έλεγχος αν υπάρχει
        cur.execute("SELECT id FROM notes WHERE id = ?", (note_id,))
        if not cur.fetchone():
            conn.close()
            return {"error": "Η σημείωση δεν βρέθηκε"}

        updates = []
        params = []

        if title is not None:
            updates.append("title = ?")
            params.append(title.strip())

        if content is not None:
            updates.append("content = ?")
            params.append(content.strip())

        if category is not None:
            updates.append("category = ?")
            params.append(category.strip())

        if tags is not None:
            updates.append("tags = ?")
            params.append(",".join(tags))

        if updates:
            updates.append("updated_at = ?")
            params.append(datetime.now().isoformat())
            params.append(note_id)

            query = f"UPDATE notes SET {', '.join(updates)} WHERE id = ?"
            cur.execute(query, params)
            conn.commit()

        conn.close()
        return {"success": True, "id": note_id}
    except Exception as e:
        return {"error": f"Σφάλμα κατά την ενημέρωση: {str(e)}"}

def delete_note(note_id: int) -> dict:
    """Διαγραφή σημείωσης"""
    try:
        conn = sqlite3.connect(NOTES_DB)
        cur = conn.cursor()

        cur.execute("DELETE FROM notes WHERE id = ?", (note_id,))

        if cur.rowcount == 0:
            conn.close()
            return {"error": "Η σημείωση δεν βρέθηκε"}

        conn.commit()
        conn.close()
        return {"success": True, "id": note_id}
    except Exception as e:
        return {"error": f"Σφάλμα κατά τη διαγραφή: {str(e)}"}

def toggle_pin(note_id: int) -> dict:
    """Toggle pin status"""
    try:
        conn = sqlite3.connect(NOTES_DB)
        cur = conn.cursor()

        cur.execute("SELECT pinned FROM notes WHERE id = ?", (note_id,))
        row = cur.fetchone()

        if not row:
            conn.close()
            return {"error": "Η σημείωση δεν βρέθηκε"}

        new_pinned = 0 if row[0] else 1
        cur.execute("UPDATE notes SET pinned = ? WHERE id = ?", (new_pinned, note_id))
        conn.commit()
        conn.close()

        return {"success": True, "id": note_id, "pinned": bool(new_pinned)}
    except Exception as e:
        return {"error": f"Σφάλμα: {str(e)}"}

def get_categories() -> list:
    """Επιστρέφει όλες τις μοναδικές κατηγορίες"""
    try:
        conn = sqlite3.connect(NOTES_DB)
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT category FROM notes WHERE category != '' ORDER BY category")
        categories = [row[0] for row in cur.fetchall()]
        conn.close()
        return categories
    except Exception:
        return []

def get_all_tags() -> list:
    """Επιστρέφει όλα τα μοναδικά tags"""
    try:
        conn = sqlite3.connect(NOTES_DB)
        cur = conn.cursor()
        cur.execute("SELECT tags FROM notes WHERE tags != ''")
        all_tags = set()
        for row in cur.fetchall():
            if row[0]:
                all_tags.update(row[0].split(","))
        conn.close()
        return sorted(list(all_tags))
    except Exception:
        return []
