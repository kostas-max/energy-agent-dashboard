
import os, time, json
from datetime import datetime

USAGE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "api_usage.log")
MAX_DAILY_SECONDS = 1200  # 20 minutes

def check_api_quota():
    if not os.path.exists(USAGE_FILE):
        return 0
    try:
        with open(USAGE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        today = datetime.now().strftime("%Y-%m-%d")
        if data.get("date") != today:
            return 0
        return float(data.get("seconds", 0))
    except Exception:
        return 0

def update_quota(elapsed):
    today = datetime.now().strftime("%Y-%m-%d")
    current = check_api_quota()
    with open(USAGE_FILE, "w", encoding="utf-8") as f:
        json.dump({"date": today, "seconds": current + float(elapsed)}, f)

def summarize_article(title, content):
    api_key = os.getenv("OPENAI_API_KEY") or ""
    if not api_key:
        return None
    if check_api_quota() >= MAX_DAILY_SECONDS:
        return None

    start = time.time()
    try:
        import httpx
        from openai import OpenAI

        # Δημιουργία custom http client χωρίς proxies
        http_client = httpx.Client(
            proxies=None,  # Explicitly disable proxies
            timeout=30.0
        )

        client = OpenAI(api_key=api_key, http_client=http_client)
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": f"Σύνοψη στα ελληνικά με 2-3 προτάσεις:\nΤίτλος: {title}\nΚείμενο: {content[:4000]}"}],
            max_tokens=120,
        )
        text = resp.choices[0].message.content.strip()
        http_client.close()
    except Exception as e:
        print(f"[ERROR] Σφάλμα AI summarization: {e}")
        text = None
    elapsed = time.time() - start
    update_quota(elapsed)
    return text
