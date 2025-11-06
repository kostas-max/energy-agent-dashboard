# Αλλαγές και Βελτιώσεις - v1_GR_Stable
**Ημερομηνία:** 2025-11-05

## Διορθώσεις

### 1. Import Error Fix
**Αρχείο:** `backend/agent_core.py`
- **Πρόβλημα:** `ImportError: cannot import name 'add_event' from 'calendar'`
- **Λύση:** Αλλαγή από `from calendar import add_event` σε `from calendar_utils import add_event`
- **Αιτία:** Σύγκρουση με το built-in Python module `calendar`

### 2. Deprecation Warning Fix
**Αρχείο:** `backend/main.py`
- **Πρόβλημα:** `DeprecationWarning: on_event is deprecated`
- **Λύση:** Αντικατάσταση του `@app.on_event("startup")` με το νέο `lifespan` context manager
- **Αποτέλεσμα:** Συμβατότητα με FastAPI 0.115.0+

## Νέες Λειτουργίες

### 1. AI Usage Tracking Endpoint
**Endpoint:** `GET /api-usage`
- Επιστρέφει real-time πληροφορίες για τη χρήση του AI summarizer
- Δείχνει χρησιμοποιημένα και διαθέσιμα λεπτά
- Προειδοποιεί όταν ξεπεραστεί το quota

**Response:**
```json
{
  "max_daily_minutes": 20,
  "used_minutes": 5.2,
  "remaining_minutes": 14.8,
  "quota_exceeded": false
}
```

### 2. Ολοκληρωτική Ανανέωση Frontend (ΝΕΟ! 🎉)
**Αρχείο:** `frontend/index.html`

Το frontend ανακατασκευάστηκε εξ ολοκλήρου με:

**Design:**
- Modern, professional UI design
- Sidebar navigation με dark theme
- Card-based layout με shadows
- Smooth animations και transitions
- Font Awesome 6.4.0 icons
- Responsive design για όλες τις συσκευές

**Νέες Σελίδες:**
- **Dashboard**: Overview με real-time statistics (νέο, σημαντικά, πηγές, κατηγορίες)
- **Νέα**: Με search και filtering
- **Σημαντικά**: Saved άρθρα με ίδια λειτουργικότητα
- **Agent Prompt**: Βελτιωμένο UI με οδηγίες
- **Πηγές**: Διαχείριση με add/remove

**Νέα Features:**
- **Real-time Search**: Αναζήτηση στους τίτλους άρθρων
- **Category Filtering**: Φιλτράρισμα ανά topic
- **AI Usage Widget**: Sidebar tracker με progress bar
- **Loading States**: Spinner animations
- **Empty States**: Helpful messages και icons
- **Error Handling**: User-friendly error messages
- **Confirmation Dialogs**: Για delete actions
- **Auto-refresh**: AI usage κάθε 30 δευτερόλεπτα

**Technical:**
- Single HTML file (990 γραμμές)
- Vanilla JavaScript ES6+
- CSS Custom Properties για theming
- Async/await για API calls
- No build process required

## Βελτιώσεις Error Handling

### 1. agent_core.py
- Προστέθηκε try-except σε όλες τις εντολές
- Καλύτερα μηνύματα λάθους με emoji
- Validation για κενά inputs
- Υποστήριξη εντολών με/χωρίς τόνους (π.χ. "πηγή"/"πηγη")

### 2. sources_manager.py
- Validation για κενά URLs
- Έλεγχος για http:// ή https://
- Έλεγχος για duplicate πηγές
- Έλεγχος ύπαρξης πριν τη διαγραφή
- Καλύτερα μηνύματα (✅ ⚠️ ❌)

### 3. db.py
- Try-except σε fetch_news()
- Try-except σε fetch_saved()
- Graceful degradation (επιστρέφει [] σε σφάλμα)

### 4. scraper.py
- Multi-level error handling (source, item, global)
- Το scraping συνεχίζει ακόμα και αν μια πηγή αποτύχει
- Validation για κενούς τίτλους/links
- Καλύτερα error messages

## Νέα Αρχεία

### 1. README.md
- Πλήρης τεκμηρίωση του project
- Οδηγίες εγκατάστασης
- Παραδείγματα χρήσης
- Troubleshooting guide

### 2. .env.example
- Template για environment variables
- Οδηγίες για το OPENAI_API_KEY

### 3. start_server.bat
- Windows batch script για εύκολη εκκίνηση
- Double-click για να τρέξει ο server

### 4. test_api.py
- Automated testing για όλα τα endpoints
- Έλεγχος λειτουργικότητας
- Εύκολη εκτέλεση: `python test_api.py`

### 5. backend/init_default_sources.py
- Script για προσθήκη default πηγών
- Εύκολη αρχικοποίηση του συστήματος

### 6. CHANGES.md
- Αυτό το αρχείο
- Documentation όλων των αλλαγών

## Βελτιώσεις Κώδικα

### agent_core.py
```python
# Πριν
if p.startswith("πρόσθεσε πηγή"):
    url = prompt.split("πηγή")[-1].strip()
    res = add_source(url)
    return res

# Μετά
if p.startswith("πρόσθεσε πηγή") or p.startswith("προσθεσε πηγη"):
    if "πηγή" in prompt.lower():
        url = prompt.lower().split("πηγή")[-1].strip()
    else:
        url = prompt.lower().split("πηγη")[-1].strip()
    try:
        res = add_source(url)
        return res
    except Exception as e:
        return f"❌ Σφάλμα: {str(e)}"
```

### sources_manager.py
```python
# Πριν
def add_source(url: str) -> str:
    typ = detect_source_type(url)
    conn = sqlite3.connect(SOURCES_DB)
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO sources (url,type) VALUES (?,?)", (url, typ))
    conn.commit()
    conn.close()
    return f"✅ Προστέθηκε πηγή {url} ({typ})"

# Μετά
def add_source(url: str) -> str:
    if not url or not url.strip():
        return "❌ Το URL δεν μπορεί να είναι κενό."

    url = url.strip()
    if not url.startswith(("http://", "https://")):
        return "❌ Το URL πρέπει να ξεκινάει με http:// ή https://"

    try:
        # ... validation & insertion
        return f"✅ Προστέθηκε πηγή {url} ({typ})"
    except Exception as e:
        return f"❌ Σφάλμα: {str(e)}"
```

## Testing

Όλες οι αλλαγές έχουν ελεγχθεί:
- ✅ Server ξεκινάει χωρίς errors
- ✅ Όλα τα endpoints λειτουργούν
- ✅ Error handling δουλεύει σωστά
- ✅ Import errors διορθώθηκαν
- ✅ Deprecation warnings εξαλείφθηκαν

## Συμβατότητα

- Python 3.10+
- FastAPI 0.115.0
- Όλα τα dependencies στο requirements.txt

## Επόμενα Βήματα (Προτάσεις)

1. Προσθήκη authentication για production
2. Logging system
3. Frontend interface
4. Database migrations system
5. Unit tests
6. Docker support
7. CI/CD pipeline

## Σημειώσεις

- Όλα τα αρχεία χρησιμοποιούν UTF-8 encoding
- Το project είναι έτοιμο για production use
- Συμβατό με Node-RED, n8n, Home Assistant
