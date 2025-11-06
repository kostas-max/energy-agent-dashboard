"""
Initialization script - Προσθήκη default πηγών
Χρήση: python init_default_sources.py
"""

from sources_manager import add_source

DEFAULT_SOURCES = [
    "https://ypen.gov.gr/feed/",  # ΥΠΕΝ RSS Feed
    "https://www.rae.gr/feed/",   # ΡΑΕ RSS Feed
    # Προσθήκη περισσότερων πηγών εδώ
]

def init_sources():
    print("=" * 60)
    print("Προσθήκη Default Πηγών")
    print("=" * 60)

    for url in DEFAULT_SOURCES:
        result = add_source(url)
        print(f"  {result}")

    print("\n[OK] Ολοκληρώθηκε!")
    print("=" * 60)

if __name__ == "__main__":
    init_sources()
