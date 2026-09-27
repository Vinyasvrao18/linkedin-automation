"""
linkedin.py
───────────
Posts content to LinkedIn using the LinkedIn Marketing API (OAuth 2.0).
Handles authentication, post creation, and error handling.
"""
import json
import requests
from config import LINKEDIN_ACCESS_TOKEN, LINKEDIN_PERSON_URN


LINKEDIN_API_BASE = "https://api.linkedin.com/v2"
LINKEDIN_POST_URL = f"{LINKEDIN_API_BASE}/ugcPosts"


def _get_headers() -> dict:
    """Return authorisation headers for LinkedIn API calls."""
    if not LINKEDIN_ACCESS_TOKEN:
        raise ValueError(
            "LINKEDIN_ACCESS_TOKEN is not set. "
            "Please set it in your .env file or as an environment variable."
        )
    return {
        "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0",
    }


def _validate_config() -> None:
    """Raise if required LinkedIn config values are missing."""
    if not LINKEDIN_PERSON_URN:
        raise ValueError(
            "LINKEDIN_PERSON_URN is not set. "
            "Set it to your URN like 'urn:li:person:XXXXXX'."
        )


def post_to_linkedin(post_text: str) -> dict:
    """
    Publish a text post to LinkedIn.

    Args:
        post_text: The body text of the LinkedIn post.

    Returns:
        dict with keys: success (bool), post_id (str|None), error (str|None)
    """
    _validate_config()

    payload = {
        "author": LINKEDIN_PERSON_URN,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": post_text,
                },
                "shareMediaCategory": "NONE",
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        },
    }

    try:
        resp = requests.post(
            LINKEDIN_POST_URL,
            headers=_get_headers(),
            data=json.dumps(payload),
            timeout=30,
        )

        if resp.status_code in (200, 201):
            post_id = resp.json().get("id", "unknown")
            print(f"[linkedin] ✓ Post published successfully! ID: {post_id}")
            return {"success": True, "post_id": post_id, "error": None}

        error_msg = f"HTTP {resp.status_code}: {resp.text}"
        print(f"[linkedin] ✗ Failed to post: {error_msg}")
        return {"success": False, "post_id": None, "error": error_msg}

    except requests.RequestException as exc:
        error_msg = f"Request failed: {exc}"
        print(f"[linkedin] ✗ {error_msg}")
        return {"success": False, "post_id": None, "error": error_msg}


def verify_credentials() -> bool:
    """
    Quick health-check: fetch the current user's profile to confirm
    the access token is valid.
    """
    try:
        resp = requests.get(
            f"{LINKEDIN_API_BASE}/me",
            headers=_get_headers(),
            timeout=15,
        )
        if resp.status_code == 200:
            data = resp.json()
            name = f"{data.get('localizedFirstName', '')} {data.get('localizedLastName', '')}"
            print(f"[linkedin] ✓ Authenticated as: {name.strip()}")
            return True
        print(f"[linkedin] ✗ Credential check failed: HTTP {resp.status_code}")
        return False
    except Exception as exc:
        print(f"[linkedin] ✗ Credential check error: {exc}")
        return False
