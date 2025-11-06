# 🤖 AI-Powered Topic Discovery System

## Τι κάνει;

Το νέο σύστημα χρησιμοποιεί **Artificial Intelligence** για να:

1. **Ανακαλύπτει trending topics** - Αναλύει τα πρόσφατα άρθρα και βρίσκει τι είναι hot αυτή τη στιγμή
2. **Δημιουργεί smart search queries** - Το AI φτιάχνει αυτόματα queries για νέα προγράμματα, επιδοτήσεις, αλλαγές νομοθεσίας
3. **Κάνει automatic scraping** - Ψάχνει αυτόματα για νέα θέματα χωρίς να χρειάζεται manual input

---

## 🚀 Πώς να το χρησιμοποιήσεις

### Μέθοδος 1: Μέσω API (Recommended)

#### 1. **Full AI Discovery & Search**
Αυτόματη ανακάλυψη και αναζήτηση:

```bash
curl -X POST http://localhost:8000/scrape/ai-discovery \
  -H "Content-Type: application/json" \
  -d '{"max_queries": 5}'
```

**Response:**
```json
{
  "success": true,
  "trending_topics": [
    {
      "topic": "Νέο πρόγραμμα φωτοβολταϊκών 2025",
      "importance": 9,
      "keywords": "φωτοβολταϊκά, επιδότηση, 2025",
      "queries": ["νέα προγράμματα φωτοβολταϊκών 2025", "επιδότηση φωτοβολταϊκών"]
    }
  ],
  "new_queries": [
    "παράταση εξοικονομώ κατ οίκον 2025",
    "net billing αλλαγές ελλάδα"
  ],
  "total_articles_found": 12
}
```

#### 2. **Trending Topics Only**
Δες μόνο τα trending topics:

```bash
curl http://localhost:8000/scrape/trending-topics
```

#### 3. **Generate Queries για συγκεκριμένο Topic**
Δημιούργησε queries για ένα topic:

```bash
curl -X POST http://localhost:8000/scrape/generate-queries \
  -H "Content-Type: application/json" \
  -d '{"topic": "αντλίες θερμότητας", "context": "επιδοτήσεις 2025"}'
```

**Response:**
```json
{
  "success": true,
  "topic": "αντλίες θερμότητας",
  "queries": [
    "αντλίες θερμότητας επιδότηση 2025",
    "νέα προγράμματα αντλίες θερμότητας",
    "εξοικονομώ αντλίες"
  ]
}
```

---

### Μέθοδος 2: Μέσω Python Script

Τρέξε το test script:

```bash
cd backend
python test_ai_discovery.py
```

Ή χρησιμοποίησε το σαν module:

```python
from ai_topic_discovery import run_ai_topic_discovery_and_search

# Run full discovery
results = run_ai_topic_discovery_and_search(max_queries=5)

print(f"Found {results['total_articles_found']} new articles")
```

---

## 🎯 Use Cases

### 1. Daily Automatic Discovery
Κάνε automatic discovery κάθε πρωί:

```bash
# Στο cron (Linux) ή Task Scheduler (Windows)
curl -X POST http://localhost:8000/scrape/ai-discovery -d '{"max_queries": 10}'
```

### 2. Manual Topic Exploration
Ψάξε για συγκεκριμένο θέμα:

```python
from ai_topic_discovery import generate_smart_queries_for_topic
from smart_search import smart_web_search, save_search_results_to_db

# Generate queries
queries = generate_smart_queries_for_topic("net metering")

# Search
for query in queries:
    results = smart_web_search(query, max_results=10)
    save_search_results_to_db(results, query=query)
```

### 3. Trending Analysis
Δες τι trending αυτή τη στιγμή:

```bash
curl http://localhost:8000/scrape/trending-topics
```

---

## ⚙️ Configuration

### Environment Variables

Βεβαιώσου ότι έχεις στο `.env`:

```bash
OPENAI_API_KEY=sk-your-api-key-here
```

### API Rate Limits

Το σύστημα έχει built-in rate limiting:
- **2 seconds** μεταξύ searches (για να μην μπλοκάρει το Google/DuckDuckGo)
- **0.2 seconds** μεταξύ AI filtering calls
- **Daily quota** για AI summarization (20 minutes/day)

---

## 🧠 Πώς Λειτουργεί (Technical)

### 1. Trending Topics Analysis

```
Recent Articles (last 7 days)
        ↓
   AI Analysis (GPT-4o-mini)
        ↓
Trending Topics + Importance Score
        ↓
   Generate Queries
```

### 2. New Topic Discovery

```
AI Prompt: "Discover new energy topics in Greece"
        ↓
   GPT-4o-mini generates queries
        ↓
   DuckDuckGo/Google Search
        ↓
   AI Filtering (relevance check)
        ↓
   Save to Database
```

### 3. Smart Query Generation

```
User Topic: "φωτοβολταϊκά"
        ↓
AI Context: "Find news about programs, subsidies, deadlines"
        ↓
Generated Queries:
  - "νέα προγράμματα φωτοβολταϊκών 2025"
  - "επιδότηση φωτοβολταϊκών ελλάδα"
  - "παράταση φωτοβολταϊκών"
```

---

## 📊 API Cost Estimation

### GPT-4o-mini Pricing
- Input: **$0.150 / 1M tokens**
- Output: **$0.600 / 1M tokens**

### Typical Costs per Run
- **Trending Analysis**: ~500 tokens = $0.0004
- **Query Generation**: ~300 tokens = $0.0002
- **AI Filtering (10 results)**: ~1000 tokens = $0.0008

**Total per full discovery run**: ~**$0.002** (0.2 cents)

---

## 🐛 Troubleshooting

### Problem: "No trending topics found"
**Solution:** Προσθες πρώτα άρθρα στη βάση:
```bash
curl -X POST http://localhost:8000/scrape/manual
```

### Problem: "AI disabled" or empty results
**Solution:** Ελεγξε το OpenAI API key:
```bash
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('OPENAI_API_KEY'))"
```

### Problem: "Timeout" errors
**Solution:** Το Google search μπορεί να μπλοκάρει. Χρησιμοποιεί DuckDuckGo by default.

---

## 🔮 Future Enhancements

- [ ] **Multi-language support** (English + Greek)
- [ ] **Custom AI models** (fine-tuned για energy domain)
- [ ] **Automatic scheduling** (built-in cron)
- [ ] **Email notifications** για trending topics
- [ ] **Topic clustering** (group similar topics)
- [ ] **Sentiment analysis** (positive/negative news)

---

## 📚 API Reference

### POST `/scrape/ai-discovery`
Full AI discovery and search.

**Request:**
```json
{
  "max_queries": 5  // Number of queries to execute
}
```

**Response:**
```json
{
  "success": true,
  "trending_topics": [...],
  "new_queries": [...],
  "total_articles_found": 12
}
```

### GET `/scrape/trending-topics`
Get trending topics from recent articles.

**Response:**
```json
{
  "success": true,
  "total_articles_analyzed": 45,
  "topics": [
    {
      "topic": "...",
      "importance": 8,
      "keywords": "...",
      "queries": [...]
    }
  ]
}
```

### POST `/scrape/generate-queries`
Generate search queries for a topic.

**Request:**
```json
{
  "topic": "φωτοβολταϊκά",
  "context": "επιδοτήσεις 2025"  // optional
}
```

**Response:**
```json
{
  "success": true,
  "topic": "φωτοβολταϊκά",
  "queries": ["...", "..."]
}
```

---

## 📝 Example Workflow

```bash
# 1. Δες τα trending topics
curl http://localhost:8000/scrape/trending-topics

# 2. Generate queries για ένα topic
curl -X POST http://localhost:8000/scrape/generate-queries \
  -H "Content-Type: application/json" \
  -d '{"topic": "φωτοβολταϊκά"}'

# 3. Run full AI discovery
curl -X POST http://localhost:8000/scrape/ai-discovery \
  -H "Content-Type: application/json" \
  -d '{"max_queries": 10}'

# 4. Check τα νέα άρθρα
curl http://localhost:8000/news
```

---

**Enjoy your AI-powered energy news discovery! 🚀**
