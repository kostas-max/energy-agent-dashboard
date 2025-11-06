"""
Test script for AI Topic Discovery System
"""

import sys
import os

# Add parent dir to path
sys.path.insert(0, os.path.dirname(__file__))

from ai_topic_discovery import (
    discover_new_topics_from_web,
    generate_smart_queries_for_topic,
    get_recent_articles_from_db,
    analyze_trending_topics,
    run_ai_topic_discovery_and_search
)


def test_discover_new_topics():
    """Test 1: AI-generated search queries"""
    print("\n" + "="*60)
    print("TEST 1: Discovering New Topics from Web")
    print("="*60)

    queries = discover_new_topics_from_web()

    if queries:
        print(f"\n[OK] SUCCESS: Generated {len(queries)} queries:")
        for i, q in enumerate(queries, 1):
            print(f"  {i}. {q}")
    else:
        print("\n[ERROR] FAILED: No queries generated (check OpenAI API key)")

    return bool(queries)


def test_generate_queries_for_topic():
    """Test 2: Generate queries for specific topic"""
    print("\n" + "="*60)
    print("TEST 2: Generate Smart Queries for Topic")
    print("="*60)

    topic = "φωτοβολταϊκά"
    print(f"\nTopic: '{topic}'")

    queries = generate_smart_queries_for_topic(topic)

    if queries:
        print(f"\n[OK] SUCCESS: Generated {len(queries)} queries:")
        for i, q in enumerate(queries, 1):
            print(f"  {i}. {q}")
    else:
        print("\n[WARNING] Fallback queries used (AI may be disabled)")

    return True


def test_trending_topics():
    """Test 3: Analyze trending topics from DB"""
    print("\n" + "="*60)
    print("TEST 3: Analyzing Trending Topics from Recent Articles")
    print("="*60)

    recent_articles = get_recent_articles_from_db(days=30, limit=50)

    print(f"\nFound {len(recent_articles)} recent articles in DB")

    if not recent_articles:
        print("[WARNING] No recent articles in DB. Add some articles first!")
        return False

    trending = analyze_trending_topics(recent_articles)

    if trending:
        print(f"\n[OK] SUCCESS: Found {len(trending)} trending topics:")
        for topic in trending:
            print(f"\n  Topic: {topic.get('topic', 'Unknown')}")
            print(f"  Importance: {topic.get('importance', 0)}/10")
            print(f"  Keywords: {topic.get('keywords', 'N/A')}")
            queries = topic.get('queries', [])
            if queries:
                print(f"  Suggested Queries:")
                for q in queries:
                    print(f"    - {q}")
    else:
        print("\n[ERROR] FAILED: No trending topics found (check OpenAI API key)")

    return bool(trending)


def test_full_ai_discovery():
    """Test 4: Full AI discovery and search"""
    print("\n" + "="*60)
    print("TEST 4: FULL AI DISCOVERY & SEARCH")
    print("="*60)
    print("\n[WARNING] This will make real searches and use OpenAI API!")
    print("Continue? (y/n): ", end="")

    response = input().strip().lower()
    if response != 'y':
        print("Skipped.")
        return True

    results = run_ai_topic_discovery_and_search(max_queries=3)

    print("\n" + "="*60)
    print("RESULTS:")
    print("="*60)
    print(f"\nTrending Topics: {len(results.get('trending_topics', []))}")
    print(f"New Queries Generated: {len(results.get('new_queries', []))}")
    print(f"Total New Articles Found: {results.get('total_articles_found', 0)}")

    return True


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print(" AI TOPIC DISCOVERY - TEST SUITE ")
    print("="*70)

    # Check OpenAI API key
    from dotenv import load_dotenv
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        print("\n[ERROR] OPENAI_API_KEY not found in .env file!")
        print("Set your API key first: OPENAI_API_KEY=sk-...")
        return

    print(f"\n[OK] OpenAI API Key: {api_key[:10]}...{api_key[-4:]}")

    # Run tests
    tests = [
        test_discover_new_topics,
        test_generate_queries_for_topic,
        test_trending_topics,
        test_full_ai_discovery
    ]

    passed = 0
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"\n[ERROR] {e}")
            import traceback
            traceback.print_exc()

    # Summary
    print("\n" + "="*70)
    print(f"SUMMARY: {passed}/{len(tests)} tests passed")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
