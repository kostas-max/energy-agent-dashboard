# Smart Search System - Οδηγίες Χρήσης

## Περιγραφή

Το Smart Search System κάνει **έξυπνη αναζήτηση στο web** με AI filtering για να βρίσκει σχετικά άρθρα για ενεργειακά θέματα.

### Χαρακτηριστικά:
- ✅ Web scraping από Google και DuckDuckGo
- ✅ AI-powered filtering για σχετικότητα
- ✅ Predefined topics (Φωτοβολταϊκά, Αντλίες Θερμότητας, Νομοθεσία, κλπ.)
- ✅ Αυτόματη αποθήκευση στη βάση δεδομένων
- ✅ AI summarization για κάθε άρθρο

## Predefined Topics

Το σύστημα έχει 5 predefined topics με keywords:

1. **Φωτοβολταϊκά**
   - φωτοβολταϊκά νέα
   - net metering ελλάδα
   - net billing πρόγραμμα
   - αυτοπαραγωγή ενέργειας
   - επιδότηση φωτοβολταϊκών
   - παράταση φωτοβολταϊκών

2. **Αντλίες Θερμότητας**
   - αντλίες θερμότητας νέα
   - επιδότηση αντλιών θερμότητας
   - θέρμανση ελλάδα
   - heat pump greece
   - πρόγραμμα εξοικονομώ

3. **Νομοθεσία**
   - φεκ ενέργεια
   - νόμος ενέργειας
   - ρυθμίσεις ενέργειας
   - rae νέα
   - υπουργείο ενέργειας

4. **Επιδοτήσεις**
   - επιχορήγηση ενέργεια
   - εσπα ενέργεια
   - πρόγραμμα επιδότησης
   - παράταση προγράμματος
   - εξοικονομώ κατ' οίκον

5. **Μπαταρίες**
   - αποθήκευση ενέργειας
   - battery storage greece
   - μπαταρίες φωτοβολταϊκών
   - energy storage

## Χρήση από Agent Prompt

### 1. Απλή αναζήτηση με λέξη-κλειδί

```
ψάξε αντλίες θερμότητας
```

Αυτό θα κάνει smart web search για "αντλίες θερμότητας" και θα αποθηκεύσει τα αποτελέσματα.

### 2. Αναζήτηση με πολλαπλές λέξεις

```
ψάξε παράταση φωτοβολταϊκών πρόγραμμα
```

## Χρήση από API

### 1. Smart Search για συγκεκριμένο query

```bash
POST http://localhost:8000/prompt
{
  "prompt": "ψάξε νομοθεσία ενέργειας"
}
```

### 2. Smart Scraping για όλα τα topics

```bash
POST http://localhost:8000/scrape/smart
{
  "topics": null,
  "max_per_topic": 5
}
```

Αυτό θα ψάξει όλα τα 5 predefined topics και θα βρει έως 5 άρθρα ανά topic.

### 3. Smart Scraping για συγκεκριμένα topics

```bash
POST http://localhost:8000/scrape/smart
{
  "topics": ["Φωτοβολταϊκά", "Αντλίες Θερμότητας"],
  "max_per_topic": 10
}
```

### 4. Δες διαθέσιμα topics

```bash
GET http://localhost:8000/scrape/topics
```

## Πώς λειτουργεί το AI Filtering

1. **Web Search**: Ψάχνει στο DuckDuckGo και Google με το query
2. **AI Analysis**: Για κάθε αποτέλεσμα, το AI ελέγχει αν είναι σχετικό
3. **Filtering**: Κρατάει μόνο τα σχετικά αποτελέσματα
4. **Summarization**: Δημιουργεί AI summary για κάθε άρθρο
5. **Storage**: Αποθηκεύει στη βάση δεδομένων

## Κόστος API

**ΠΡΟΣΟΧΗ**: Το Smart Search χρεώνει το OpenAI API:
- ~0.001$ ανά query για AI filtering
- ~0.0005$ ανά άρθρο για summarization

**Παράδειγμα**:
- 5 topics × 5 άρθρα = 25 άρθρα
- AI filtering: 5 topics × 10 results × 0.001$ = ~0.05$
- Summarization: 25 άρθρα × 0.0005$ = ~0.0125$
- **Συνολικό κόστος**: ~0.06$ ανά smart scraping

## Test Script

Δοκίμασε το Smart Search με:

```bash
cd backend
python test_smart_search.py
```

Αυτό θα κάνει 2 test searches και θα δείξει τα αποτελέσματα.

## Προσθήκη νέων Topics

Για να προσθέσεις νέα topics, επεξεργάσου το [backend/smart_search.py](backend/smart_search.py):

```python
SMART_TOPICS = {
    "Το Νέο Topic": [
        "keyword 1",
        "keyword 2",
        "keyword 3"
    ]
}
```

## Troubleshooting

### Δεν βρίσκει αποτελέσματα
- Ελέγξτε αν έχετε internet σύνδεση
- Δοκιμάστε με πιο γενικά keywords
- Απενεργοποιήστε το AI filtering (`use_ai_filter=False`)

### Rate Limiting
- Το Google μπορεί να μπλοκάρει το IP αν κάνετε πολλά requests
- Χρησιμοποιήστε `time.sleep()` ανάμεσα στα requests
- Προτιμήστε το DuckDuckGo (πιο φιλικό)

### API Quota Exceeded
- Ελέγξτε το API usage: `GET http://localhost:8000/api-usage`
- Το limit είναι 20 λεπτά/μέρα (1200 δευτερόλεπτα)
- Μειώστε το `max_per_topic` για λιγότερες κλήσεις

## Σύγκριση με το παλιό Search

| Feature | Παλιό Search | Smart Search |
|---------|-------------|--------------|
| Πηγές | Μόνο RSS feeds | Όλο το web |
| Filtering | Keyword matching | AI-powered |
| Νέα άρθρα | Μόνο από sources | Από παντού |
| Σχετικότητα | Χαμηλή | Υψηλή |
| Κόστος | $0 | ~$0.06/session |

## Συμπέρασμα

Το Smart Search είναι ιδανικό όταν:
- Θέλεις να βρεις τα πιο πρόσφατα νέα για ένα θέμα
- Θέλεις AI filtering για υψηλή σχετικότητα
- Δεν έχεις προσθέσει RSS feeds για το θέμα που ψάχνεις

Χρησιμοποίησε το παλιό scraping όταν:
- Έχεις ήδη καλές πηγές RSS
- Θέλεις να αποφύγεις το κόστος API
- Δεν χρειάζεσαι AI filtering
