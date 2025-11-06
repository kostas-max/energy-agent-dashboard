"""
Test script for article content fetching
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from scraper import fetch_article_content

# Test URLs from popular energy news sites
test_urls = [
    "https://energypress.gr",
    "https://www.rae.gr",
]

def test_fetch_content():
    """Test fetching article content"""
    print("="*60)
    print("ARTICLE CONTENT FETCHING TEST")
    print("="*60)

    for url in test_urls:
        print(f"\nTesting URL: {url}")
        print("-"*60)

        content = fetch_article_content(url, max_chars=500)

        if content:
            print(f"[OK] Fetched {len(content)} characters")
            print(f"\nFirst 200 chars:")
            print(content[:200])
            print("...")
        else:
            print("[WARNING] No content fetched")

        print("-"*60)

def test_with_ai_summary():
    """Test με AI summarization"""
    print("\n" + "="*60)
    print("AI SUMMARIZATION WITH REAL CONTENT TEST")
    print("="*60)

    from ai_summarizer import summarize_article

    url = test_urls[0]
    print(f"\nURL: {url}")

    # Fetch content
    content = fetch_article_content(url, max_chars=2000)

    if content:
        print(f"[OK] Content: {len(content)} chars")

        # Generate AI summary
        print("\n[INFO] Generating AI summary...")
        summary = summarize_article("Energy News Article", content)

        if summary:
            print(f"\n[OK] AI Summary:")
            print(summary)
        else:
            print("\n[WARNING] No AI summary generated (check API key)")
    else:
        print("[ERROR] No content to summarize")

if __name__ == "__main__":
    print("\n" + "="*70)
    print(" ARTICLE CONTENT FETCHING - TEST SUITE ")
    print("="*70 + "\n")

    test_fetch_content()

    # Uncomment to test with AI
    # test_with_ai_summary()

    print("\n" + "="*70)
    print("TESTS COMPLETE")
    print("="*70 + "\n")
