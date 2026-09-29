# config.py
"""
Central configuration for LinkedIn Automation.
All secrets should be set as environment variables (or in a .env file).
"""
import os
import logging
from dotenv import load_dotenv

load_dotenv()  # Load .env file if present

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("automation.log"),
        logging.StreamHandler()
    ]
)

# ─────────────────────────────────────────────
# Ollama settings
# ─────────────────────────────────────────────
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")
# Vision-capable model for reading certificate images
OLLAMA_VISION_MODEL = os.getenv("OLLAMA_VISION_MODEL", "llava")

# ─────────────────────────────────────────────
# LinkedIn API (OAuth 2.0)
# ─────────────────────────────────────────────
LINKEDIN_CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID", "")
LINKEDIN_CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET", "")
LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN", "")
# Your LinkedIn URN  (format: "urn:li:person:XXXXXXX")
LINKEDIN_PERSON_URN = os.getenv("LINKEDIN_PERSON_URN", "")

# ─────────────────────────────────────────────
# Schedule settings
# ─────────────────────────────────────────────
# Days of the week to post (0 = Monday … 6 = Sunday)
SCHEDULE_DAYS = [0, 3]       # Monday & Thursday
# Note: Time is based on the local system timezone where the script is running
SCHEDULE_TIME = "10:00"      # 24-hr format, local time

# ─────────────────────────────────────────────
# Paths
# ─────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CERTIFICATES_DIR = os.path.join(BASE_DIR, "certificates")
POSTS_DIR = os.path.join(BASE_DIR, "posts")
GENERATED_POSTS_FILE = os.path.join(POSTS_DIR, "generated_posts.json")
POSTED_LOG_FILE = os.path.join(POSTS_DIR, "posted_log.json")
