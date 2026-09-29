"""
post_generator.py
─────────────────
Takes structured certificate data and uses Ollama (llama3) to generate
a polished, engaging LinkedIn post for each certificate.
Saves all posts to generated_posts.json with status tracking.
"""
import json
import os
import requests
import logging
from datetime import datetime
from config import (
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    GENERATED_POSTS_FILE,
    POSTS_DIR,
)

POST_PROMPT_TEMPLATE = """You are a professional LinkedIn content writer.
Write a LinkedIn post celebrating that someone has earned a certification.

Certificate details:
- Certification Name: {cert_name}
- Issuing Organisation: {issuer}
- Recipient: {recipient}
- Date Issued: {date_issued}
- Skills learned: {skills}

Requirements for the post:
1. Start with an attention-grabbing hook (use an emoji).
2. Mention the certification name and issuer prominently.
3. Briefly describe what was learned and why it matters.
4. Include 3-5 relevant hashtags at the end.
5. Keep the tone professional yet enthusiastic.
6. Keep the post between 150-300 words.
7. Do NOT use markdown formatting — plain text only.

Write ONLY the post text, nothing else."""


def _generate_post_text(cert: dict) -> str:
    """Call Ollama to generate a LinkedIn post from certificate data."""
    prompt = POST_PROMPT_TEMPLATE.format(
        cert_name=cert.get("cert_name", "Unknown"),
        issuer=cert.get("issuer", "Unknown"),
        recipient=cert.get("recipient", "Unknown"),
        date_issued=cert.get("date_issued", "unknown"),
        skills=", ".join(cert.get("skills", [])) or "various topics",
    )

    url = f"{OLLAMA_BASE_URL}/api/generate"
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
    }
    resp = requests.post(url, json=payload, timeout=120)
    resp.raise_for_status()
    return resp.json().get("response", "").strip()


def generate_posts(certificates: list[dict]) -> list[dict]:
    """
    Generate LinkedIn posts for a list of certificate dicts.
    Returns list of post objects and saves them to generated_posts.json.

    Each post object:
    {
        "id": int,
        "cert_name": str,
        "issuer": str,
        "post_text": str,
        "status": "pending",       # pending | posted | failed
        "generated_at": ISO timestamp,
        "posted_at": null
    }
    """
    os.makedirs(POSTS_DIR, exist_ok=True)

    # Load existing posts so we don't overwrite
    existing_posts = _load_existing_posts()
    already_generated = {p["cert_name"] for p in existing_posts}

    new_posts = []
    next_id = max((p["id"] for p in existing_posts), default=0) + 1

    for cert in certificates:
        name = cert.get("cert_name", "Unknown")
        if name in already_generated:
            logging.info(f"Skipping (already generated): {name}")
            continue

        logging.info(f"Generating post for: {name} …")
        try:
            text = _generate_post_text(cert)
            post = {
                "id": next_id,
                "cert_name": name,
                "issuer": cert.get("issuer", "Unknown"),
                "post_text": text,
                "status": "pending",
                "generated_at": datetime.now().isoformat(),
                "posted_at": None,
            }
            new_posts.append(post)
            next_id += 1
            logging.info(f"  ✓ Post generated ({len(text)} chars)")
        except Exception as exc:
            logging.error(f"Error generating post for {name}: {exc}")

    all_posts = existing_posts + new_posts
    _save_posts(all_posts)
    logging.info(f"Total posts saved: {len(all_posts)} ({len(new_posts)} new)")
    return all_posts


def _load_existing_posts() -> list[dict]:
    """Load previously generated posts from disk."""
    if os.path.isfile(GENERATED_POSTS_FILE):
        try:
            with open(GENERATED_POSTS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
        except (json.JSONDecodeError, IOError):
            pass
    return []


def _save_posts(posts: list[dict]) -> None:
    """Write the post list to generated_posts.json."""
    with open(GENERATED_POSTS_FILE, "w", encoding="utf-8") as f:
        json.dump(posts, f, indent=2, ensure_ascii=False)


def get_next_pending_post() -> dict | None:
    """Return the first post with status 'pending', or None."""
    posts = _load_existing_posts()
    for p in posts:
        if p.get("status") == "pending":
            return p
    return None


def mark_post_as_posted(post_id: int) -> None:
    """Update a post's status to 'posted' and record the timestamp."""
    posts = _load_existing_posts()
    for p in posts:
        if p["id"] == post_id:
            p["status"] = "posted"
            p["posted_at"] = datetime.now().isoformat()
            break
    _save_posts(posts)


def mark_post_as_failed(post_id: int, error: str = "") -> None:
    """Update a post's status to 'failed'."""
    posts = _load_existing_posts()
    for p in posts:
        if p["id"] == post_id:
            p["status"] = "failed"
            p["error"] = error
            break
    _save_posts(posts)
