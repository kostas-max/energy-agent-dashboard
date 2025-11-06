# Energy Agent Dashboard (GR) - v1_GR_Stable

Τοπικό REST API για τη συλλογή, ανάλυση και οργάνωση ενεργειακών ειδήσεων, νομοθεσίας και προγραμμάτων επιδότησης από ελληνικές πηγές.

## Χαρακτηριστικά

### Backend
- Αυτόματη συλλογή ειδήσεων από RSS, HTML και API πηγές
- AI Summarization (προαιρετικό - με OpenAI API)
- Scheduler για αυτόματο scraping (08:00 & 20:00)
- Διαχείριση πηγών
- Σημείωση σημαντικών άρθρων
- Calendar events (.ics)
- REST API με FastAPI
- CORS enabled για frontend integration

### Frontend (Νέο! 🎉)
- **Modern UI**: Professional dashboard με sidebar navigation
- **Dashboard**: Real-time statistics και overview
- **Search**: Αναζήτηση άρθρων σε πραγματικό χρόνο
- **Filtering**: Φιλτράρισμα ανά κατηγορία
- **AI Usage Tracker**: Παρακολούθηση χρήσης AI με progress bar
- **Responsive Design**: Works on desktop, tablet, mobile
- **Single HTML File**: Δεν χρειάζεται build process
- **Font Awesome Icons**: Professional iconography
- **Loading & Empty States**: Καλύτερη UX

## Εγκατάσταση

### Απαιτήσεις
- Python 3.10+
- Modern web browser (Chrome, Firefox, Safari, Edge)

### Βήματα

1. **Clone το repository**
```bash
cd C:\Users\USER\Desktop\EnergyAgentDashboard_v1_GR_Stable\energy_agent_windows
```

2. **Εγκατάσταση dependencies**
```bash
pip install -r requirements.txt
```

3. **Προαιρετικό: Ρύθμιση AI Summarizer**
Δημιούργησε αρχείο `.env` στο root directory:
```
OPENAI_API_KEY=your_api_key_here
```

4. **Εκκίνηση του server**
```bash
cd backend
python main.py
```

Το API θα είναι διαθέσιμο στο: `http://localhost:8000`

5. **Άνοιγμα Frontend**

**Επιλογή Α: Double-click**
```
Ανοίξτε το αρχείο: frontend/index.html
```

**Επιλογή Β: Batch script (Windows)**
```bash
start_server.bat
```

**Επιλογή Γ: HTTP Server**
```bash
cd frontend
python -m http.server 8080
# Ανοίξτε: http://localhost:8080
```

## Endpoints

### POST /prompt
Επεξεργάζεται εντολές στα ελληνικά.

**Παραδείγματα εντολών:**
- `ψάξε φωτοβολταϊκά`
- `πρόσθεσε πηγή https://example.com/feed`
- `δείξε τις πηγές`
- `φτιάξε φάκελο Αντλίες`
- `βάλε στο ημερολόγιο 15/11/2025`
- `σημαντικό https://example.com/article`

**Request:**
```json
{ "prompt": "ψάξε φωτοβολταϊκά" }
```

**Response:**
```json
{ "reply": "🔎 Βρέθηκαν 3 νέα σχετικά αποτελέσματα για 'φωτοβολταϊκά'." }
```

### GET /sources
Επιστρέφει όλες τις πηγές.

**Response:**
```json
{
  "sources": [
    {"url": "https://ypen.gov.gr/feed/", "type": "RSS", "last_check": null}
  ]
}
```

### POST /sources/add
Προσθέτει νέα πηγή.

**Request:**
```json
{ "url": "https://example.com/feed" }
```

### POST /sources/remove
Διαγράφει πηγή.

**Request:**
```json
{ "url": "https://example.com/feed" }
```

### GET /news
Επιστρέφει όλα τα νέα άρθρα (limit: 200).

**Response:**
```json
{
  "news": [
    {
      "title": "Νέο πρόγραμμα αυτοπαραγωγής",
      "url": "https://ypen.gov.gr/nea/programma",
      "date": "2025-11-05T08:30:00",
      "source": "https://ypen.gov.gr/feed/",
      "topic": "Φωτοβολταϊκά",
      "summary": "Επιδότηση 40% για εγκατάσταση ΦΒ.",
      "saved": false
    }
  ]
}
```

### GET /saved
Επιστρέφει μόνο τα σημαντικά άρθρα.

### GET /api-usage
Επιστρέφει τη χρήση του AI summarizer για σήμερα.

**Response:**
```json
{
  "max_daily_minutes": 20,
  "used_minutes": 5.2,
  "remaining_minutes": 14.8,
  "quota_exceeded": false
}
```

## Δομή Δεδομένων

Όλα τα δεδομένα αποθηκεύονται τοπικά στο φάκελο `data/`:

- `news.db` - Άρθρα και νέα
- `sources.db` - Πηγές
- `prompts.db` - Ιστορικό εντολών
- `calendar.ics` - Calendar events
- `api_usage.log` - AI usage tracking
- `storage/` - Φάκελοι που δημιουργούνται

### Πίνακας: news
| Πεδίο | Τύπος | Περιγραφή |
|-------|-------|-----------|
| id | INTEGER | Primary key |
| title | TEXT | Τίτλος |
| url | TEXT | Unique URL |
| date | TEXT | Ημερομηνία |
| source | TEXT | Πηγή |
| topic | TEXT | Κατηγορία |
| summary | TEXT | AI Περίληψη |
| saved | INTEGER | 0/1 |

## Κατηγορίες (Topics)

- Φωτοβολταϊκά
- Μπαταρίες
- Αντλίες
- Νομοθεσία
- Επιδοτήσεις
- Smart_Σπίτια

## Scheduler

Αυτόματο scraping 2 φορές την ημέρα:
- **08:00** (πρωί)
- **20:00** (βράδυ)

## AI Summarizer

- **Όριο:** 20 λεπτά/ημέρα
- **Model:** GPT-4o-mini
- **Reset:** Αυτόματα κάθε μεσάνυχτα
- **Offline mode:** Αν ξεπεραστεί το όριο ή δεν υπάρχει API key

## Troubleshooting

### Σφάλμα Import
Αν δεις σφάλμα `ImportError: cannot import name 'add_event' from 'calendar'`:
- Βεβαιώσου ότι το αρχείο λέγεται `calendar_utils.py` και όχι `calendar.py`

### Deprecation Warning
Το deprecation warning για `@app.on_event("startup")` έχει διορθωθεί με το νέο `lifespan` API.

### Dependencies
Αν έχεις προβλήματα με dependencies:
```bash
pip install --upgrade -r requirements.txt
```

## Ασφάλεια

- Το API λειτουργεί **μόνο τοπικά** (localhost)
- Δεν υπάρχει authentication (για τοπική χρήση)
- Τα API keys (αν χρησιμοποιηθούν) πρέπει να είναι στο `.env` (όχι στο git)

## Version

**v1_GR_Stable**
- Python: 3.10+
- Ημερομηνία: 2025-11-05
- Τελευταία ενημέρωση: 2025-11-05

## Support

Για προβλήματα και ερωτήσεις, ανατρέξτε στο API Reference documentation.
