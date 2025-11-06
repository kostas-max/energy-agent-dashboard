
import os

BASE = os.path.dirname(os.path.dirname(__file__))
STORAGE = os.path.join(BASE, "data", "storage")

def create_folder(name: str):
    sanitized = name.replace("/", "_").replace("\\", "_").strip()
    path = os.path.join(STORAGE, sanitized)
    os.makedirs(path, exist_ok=True)
