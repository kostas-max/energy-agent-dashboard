
import os
from datetime import datetime
from ics import Calendar, Event

BASE = os.path.dirname(os.path.dirname(__file__))
CAL_PATH = os.path.join(BASE, "data", "calendar.ics")

def add_event(title: str, start_str: str, end_str: str = None, description: str = ""):
    c = Calendar()
    if os.path.exists(CAL_PATH):
        with open(CAL_PATH, "r", encoding="utf-8") as f:
            try:
                c = Calendar(f.read())
            except Exception:
                c = Calendar()

    e = Event()
    try:
        dt = datetime.strptime(start_str, "%d/%m/%Y")
        e.begin = dt
    except Exception:
        return
    if end_str:
        try:
            e.end = datetime.strptime(end_str, "%d/%m/%Y")
        except Exception:
            pass
    e.name = title
    e.description = description
    c.events.add(e)

    with open(CAL_PATH, "w", encoding="utf-8") as f:
        f.writelines(c)
