"""
scheduler.py
────────────
Runs a background scheduler that:
  1. Checks twice a week (Monday & Thursday at 10:00 AM by default).
  2. Picks the next pending post from generated_posts.json.
  3. Publishes it to LinkedIn via the API.
  4. Updates the post status to 'posted' or 'failed'.

Uses the `schedule` library for human-friendly scheduling.
"""
import schedule
import time
import signal
import sys
import logging
from config import SCHEDULE_DAYS, SCHEDULE_TIME
from post_generator import get_next_pending_post, mark_post_as_posted, mark_post_as_failed
from linkedin import post_to_linkedin

DAY_NAMES = {
    0: "monday",
    1: "tuesday",
    2: "wednesday",
    3: "thursday",
    4: "friday",
    5: "saturday",
    6: "sunday",
}


def _post_next():
    """Fetch the next pending post and publish it to LinkedIn."""
    post = get_next_pending_post()
    if post is None:
        logging.info("No pending posts to publish. Skipping.")
        return

    logging.info(f"Publishing post #{post['id']}: {post['cert_name']}")
    result = post_to_linkedin(post["post_text"])

    if result["success"]:
        mark_post_as_posted(post["id"])
        logging.info(f"✓ Post #{post['id']} published successfully!")
    else:
        mark_post_as_failed(post["id"], error=result.get("error", ""))
        logging.error(f"✗ Post #{post['id']} failed: {result.get('error', 'unknown')}")


def start_scheduler():
    """
    Register scheduled jobs and run the event loop.
    Posts are scheduled on the configured days at the configured time.
    """
    for day_num in SCHEDULE_DAYS:
        day_name = DAY_NAMES.get(day_num)
        if day_name is None:
            logging.warning(f"Invalid day number: {day_num}, skipping.")
            continue

        # schedule.every().monday.at("10:00").do(...)
        getattr(schedule.every(), day_name).at(SCHEDULE_TIME).do(_post_next)
        logging.info(f"Registered: {day_name.capitalize()} at {SCHEDULE_TIME}")

    logging.info("✓ Scheduler is running. Press Ctrl+C to stop.")
    logging.info(f"Next run: {schedule.next_run()}")

    # Graceful shutdown
    def _shutdown(sig, frame):
        logging.info("Shutting down gracefully …")
        schedule.clear()
        sys.exit(0)

    signal.signal(signal.SIGINT, _shutdown)

    while True:
        schedule.run_pending()
        time.sleep(30)  # Check every 30 seconds


if __name__ == "__main__":
    start_scheduler()
