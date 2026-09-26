"""Generate a JSON file with a list of posts for LinkedIn automation."""
import json, os
from config import GENERATED_POSTS_FILE

def generate_posts():
    """Create a sample generated_posts.json if it is missing or empty."""
    os.makedirs(os.path.dirname(GENERATED_POSTS_FILE), exist_ok=True)
    sample_posts = [
        {"title": "Welcome to Automation", "content": "Excited to share our new LinkedIn automation tool!"},
        {"title": "Feature Highlight", "content": "Automatically schedule posts and track engagement with minimal effort."},
    ]
    with open(GENERATED_POSTS_FILE, "w", encoding="utf-8") as f:
        json.dump(sample_posts, f, indent=2, ensure_ascii=False)
