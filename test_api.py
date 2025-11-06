"""
Test script για το Energy Agent Dashboard API
Χρήση: python test_api.py
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_prompt():
    """Test του /prompt endpoint"""
    print("\n🧪 Testing /prompt endpoint...")

    test_prompts = [
        "βοήθεια",
        "ψάξε φωτοβολταϊκά",
        "δείξε τις πηγές"
    ]

    for prompt in test_prompts:
        try:
            response = requests.post(
                f"{BASE_URL}/prompt",
                json={"prompt": prompt},
                timeout=10
            )
            print(f"  ✓ '{prompt}' → {response.json()['reply'][:100]}...")
        except Exception as e:
            print(f"  ✗ '{prompt}' → Error: {e}")

def test_sources():
    """Test των sources endpoints"""
    print("\n🧪 Testing /sources endpoints...")

    try:
        # GET sources
        response = requests.get(f"{BASE_URL}/sources", timeout=10)
        sources = response.json()["sources"]
        print(f"  ✓ GET /sources → {len(sources)} πηγές")

        # ADD source
        test_url = "https://example.com/feed"
        response = requests.post(
            f"{BASE_URL}/sources/add",
            json={"url": test_url},
            timeout=10
        )
        print(f"  ✓ POST /sources/add → {response.json()['result']}")

        # REMOVE source
        response = requests.post(
            f"{BASE_URL}/sources/remove",
            json={"url": test_url},
            timeout=10
        )
        print(f"  ✓ POST /sources/remove → {response.json()['result']}")

    except Exception as e:
        print(f"  ✗ Error: {e}")

def test_news():
    """Test των news endpoints"""
    print("\n🧪 Testing /news endpoints...")

    try:
        # GET news
        response = requests.get(f"{BASE_URL}/news", timeout=10)
        news = response.json()["news"]
        print(f"  ✓ GET /news → {len(news)} άρθρα")

        # GET saved
        response = requests.get(f"{BASE_URL}/saved", timeout=10)
        saved = response.json()["news"]
        print(f"  ✓ GET /saved → {len(saved)} σημαντικά άρθρα")

    except Exception as e:
        print(f"  ✗ Error: {e}")

def test_api_usage():
    """Test του /api-usage endpoint"""
    print("\n🧪 Testing /api-usage endpoint...")

    try:
        response = requests.get(f"{BASE_URL}/api-usage", timeout=10)
        usage = response.json()
        print(f"  ✓ GET /api-usage →")
        print(f"    - Max: {usage['max_daily_minutes']} λεπτά")
        print(f"    - Used: {usage['used_minutes']} λεπτά")
        print(f"    - Remaining: {usage['remaining_minutes']} λεπτά")
        print(f"    - Quota exceeded: {usage['quota_exceeded']}")
    except Exception as e:
        print(f"  ✗ Error: {e}")

def main():
    print("=" * 50)
    print("Energy Agent Dashboard API Tests")
    print("=" * 50)
    print(f"Base URL: {BASE_URL}")

    # Έλεγχος αν ο server τρέχει
    try:
        response = requests.get(BASE_URL, timeout=5)
        print("✓ Server is running!")
    except Exception:
        print("✗ Server is not running!")
        print("  Please start the server first: cd backend && python main.py")
        return

    # Run tests
    test_prompt()
    test_sources()
    test_news()
    test_api_usage()

    print("\n" + "=" * 50)
    print("Tests completed!")
    print("=" * 50)

if __name__ == "__main__":
    main()
