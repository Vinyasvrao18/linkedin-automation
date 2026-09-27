"""
cert_reader.py
──────────────
Scans the certificates/ folder for images (PNG, JPG, JPEG, WEBP),
sends each to Ollama's vision model (llava) to extract structured
certificate details, then returns the results.
"""
import os
import base64
import json
import requests
from config import OLLAMA_BASE_URL, OLLAMA_VISION_MODEL, CERTIFICATES_DIR

SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}

EXTRACTION_PROMPT = """You are analysing a certificate image.
Extract the following fields as valid JSON (no markdown fences, no extra text):
{
  "cert_name": "<name of the certification / course>",
  "issuer": "<issuing organisation>",
  "recipient": "<name of the person who earned it>",
  "date_issued": "<date on the certificate, or 'unknown'>",
  "skills": ["<skill1>", "<skill2>"]
}
Return ONLY the JSON object."""


def _image_to_base64(path: str) -> str:
    """Read an image file and return its base64-encoded string."""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def _query_ollama_vision(image_b64: str) -> dict:
    """Send a base64 image to Ollama's vision-capable model and parse the JSON response."""
    url = f"{OLLAMA_BASE_URL}/api/generate"
    payload = {
        "model": OLLAMA_VISION_MODEL,
        "prompt": EXTRACTION_PROMPT,
        "images": [image_b64],
        "stream": False,
    }
    resp = requests.post(url, json=payload, timeout=120)
    resp.raise_for_status()
    raw_text = resp.json().get("response", "")

    # Try to parse the model output as JSON
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        # Fallback: attempt to find JSON object inside the text
        start = raw_text.find("{")
        end = raw_text.rfind("}") + 1
        if start != -1 and end > start:
            return json.loads(raw_text[start:end])
        return {
            "cert_name": "Unknown Certificate",
            "issuer": "Unknown",
            "recipient": "Unknown",
            "date_issued": "unknown",
            "skills": [],
            "_raw_response": raw_text,
        }


def scan_certificates() -> list[dict]:
    """
    Walk the certificates directory, extract info from every image,
    and return a list of certificate dicts.

    Each dict has: cert_name, issuer, recipient, date_issued, skills,
    and the source image_path.
    """
    if not os.path.isdir(CERTIFICATES_DIR):
        os.makedirs(CERTIFICATES_DIR, exist_ok=True)
        print(f"[cert_reader] Created empty folder: {CERTIFICATES_DIR}")
        return []

    image_files = sorted(
        f
        for f in os.listdir(CERTIFICATES_DIR)
        if os.path.splitext(f)[1].lower() in SUPPORTED_EXTENSIONS
    )

    if not image_files:
        print("[cert_reader] No certificate images found in certificates/")
        return []

    certs = []
    for filename in image_files:
        filepath = os.path.join(CERTIFICATES_DIR, filename)
        print(f"[cert_reader] Processing: {filename} …")
        try:
            b64 = _image_to_base64(filepath)
            info = _query_ollama_vision(b64)
            info["image_path"] = filepath
            certs.append(info)
            print(f"  ✓ Extracted: {info.get('cert_name', '?')}")
        except Exception as exc:
            print(f"  ✗ Error processing {filename}: {exc}")
            certs.append({
                "cert_name": filename,
                "issuer": "Unknown",
                "recipient": "Unknown",
                "date_issued": "unknown",
                "skills": [],
                "image_path": filepath,
                "_error": str(exc),
            })

    return certs


if __name__ == "__main__":
    results = scan_certificates()
    print(f"\n{'='*50}")
    print(f"Found {len(results)} certificate(s):")
    for c in results:
        print(f"  • {c['cert_name']} — issued by {c['issuer']}")
