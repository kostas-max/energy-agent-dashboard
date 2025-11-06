
"""
Test script για το Smart Search system
Κάνει μια δοκιμαστική αναζήτηση και δείχνει τα αποτελέσματα
"""

from smart_search import smart_web_search, duckduckgo_search

def test_duckduckgo():
    print("=" * 60)
    print("TEST: DuckDuckGo Search")
    print("=" * 60)

    query = "φωτοβολταϊκά ελλάδα νέα"
    results = duckduckgo_search(query, num_results=5)

    print(f"\nQuery: {query}")
    print(f"Βρέθηκαν {len(results)} αποτελέσματα:\n")

    for i, r in enumerate(results, 1):
        print(f"{i}. {r['title']}")
        print(f"   URL: {r['url']}")
        print(f"   Snippet: {r['snippet'][:100]}...")
        print()

def test_smart_search():
    print("=" * 60)
    print("TEST: Smart Web Search (με AI filtering)")
    print("=" * 60)

    query = "αντλίες θερμότητας επιδότηση"
    results = smart_web_search(query, max_results=5, use_ai_filter=True)

    print(f"\nQuery: {query}")
    print(f"Βρέθηκαν {len(results)} σχετικά αποτελέσματα:\n")

    for i, r in enumerate(results, 1):
        print(f"{i}. {r['title']}")
        print(f"   URL: {r['url']}")
        print(f"   Snippet: {r['snippet'][:100]}...")
        print()

if __name__ == "__main__":
    # Test DuckDuckGo search
    test_duckduckgo()

    print("\n\n")

    # Test Smart Search με AI filtering
    # ΠΡΟΣΟΧΗ: Χρειάζεται valid OPENAI_API_KEY στο .env
    test_smart_search()
