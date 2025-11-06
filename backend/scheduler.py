
from apscheduler.schedulers.background import BackgroundScheduler
from scraper import run_scraping

_scheduler = None

def start_scheduler():
    global _scheduler
    if _scheduler:
        return
    _scheduler = BackgroundScheduler()
    # Run twice daily (08:00 and 20:00)
    _scheduler.add_job(run_scraping, "cron", hour="8,20", id="scraper_job")
    _scheduler.start()
    print("Scheduler activated (08:00 & 20:00).")
