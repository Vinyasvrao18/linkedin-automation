# scheduler.py
import time
import threading
from config import POST_INTERVAL_MINUTES
from linkedin import post_to_linkedin

def start_scheduler():
    def worker():
        while True:
            post_to_linkedin()
            time.sleep(POST_INTERVAL_MINUTES * 60)
    threading.Thread(target=worker, daemon=True).start()
