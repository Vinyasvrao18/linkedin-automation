"""
main.py
───────
Entry point for LinkedIn Automation.

Workflow:
  1. Scan certificates/ folder → extract cert details via Ollama vision (llava)
  2. Generate LinkedIn posts for each cert via Ollama (llama3)
  3. Start the weekly scheduler to auto-publish posts
"""
import sys
from cert_reader import scan_certificates
from post_generator import generate_posts
from linkedin import verify_credentials
from scheduler import start_scheduler
import logging
import requests
from config import OLLAMA_BASE_URL

def check_ollama():
    """Verify Ollama is running before starting everything."""
    try:
        resp = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if resp.status_code == 200:
            logging.info("Ollama is reachable.")
            return True
        else:
            logging.warning(f"Ollama returned status {resp.status_code}")
            return False
    except requests.RequestException:
        logging.error("Ollama is not reachable. Make sure it is running.")
        return False


def main():
    logging.info("=" * 60)
    logging.info("  🚀 LinkedIn Certification Post Automation")
    logging.info("=" * 60)

    # ── Step 0: Verify LinkedIn credentials ──────────────────
    logging.info("Verifying LinkedIn credentials …")
    if not verify_credentials():
        logging.warning("LinkedIn credentials are invalid or missing.")
        logging.warning("Set LINKEDIN_ACCESS_TOKEN and LINKEDIN_PERSON_URN in your .env file.")
        logging.warning("Continuing anyway (posts will be generated but not published).")
        
    logging.info("Checking Ollama status...")
    check_ollama()

    # ── Step 1: Scan certificate images ──────────────────────
    logging.info("Scanning certificates/ folder …")
    certs = scan_certificates()
    if not certs:
        logging.info("No certificates found. Add images to the certificates/ folder.")
        logging.info("Supported formats: PNG, JPG, JPEG, WEBP")
        logging.info("The scheduler will still run and post any existing pending posts.")

    # ── Step 2: Generate posts for new certs ─────────────────
    if certs:
        logging.info(f"Generating posts for {len(certs)} certificate(s) …")
        posts = generate_posts(certs)
        pending = sum(1 for p in posts if p["status"] == "pending")
        posted = sum(1 for p in posts if p["status"] == "posted")
        logging.info(f"Posts summary: {pending} pending, {posted} already posted")

    # ── Step 3: Start scheduler ──────────────────────────────
    logging.info("Starting weekly scheduler …")
    start_scheduler()


if __name__ == "__main__":
    main()
