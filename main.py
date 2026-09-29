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


def main():
    print("=" * 60)
    print("  🚀 LinkedIn Certification Post Automation")
    print("=" * 60)

    # ── Step 0: Verify LinkedIn credentials ──────────────────
    print("\n[main] Verifying LinkedIn credentials …")
    if not verify_credentials():
        print("[main] ⚠ LinkedIn credentials are invalid or missing.")
        print("[main]   Set LINKEDIN_ACCESS_TOKEN and LINKEDIN_PERSON_URN")
        print("[main]   in your .env file. See README.md for instructions.")
        print("[main]   Continuing anyway (posts will be generated but not published).\n")

    # ── Step 1: Scan certificate images ──────────────────────
    print("[main] Scanning certificates/ folder …")
    certs = scan_certificates()
    if not certs:
        print("[main] No certificates found. Add images to the certificates/ folder.")
        print("[main]   Supported formats: PNG, JPG, JPEG, WEBP")
        print("[main]   The scheduler will still run and post any existing pending posts.\n")

    # ── Step 2: Generate posts for new certs ─────────────────
    if certs:
        print(f"\n[main] Generating posts for {len(certs)} certificate(s) …")
        posts = generate_posts(certs)
        pending = sum(1 for p in posts if p["status"] == "pending")
        posted = sum(1 for p in posts if p["status"] == "posted")
        print(f"[main] Posts summary: {pending} pending, {posted} already posted\n")

    # ── Step 3: Start scheduler ──────────────────────────────
    print("[main] Starting weekly scheduler …")
    start_scheduler()


if __name__ == "__main__":
    main()
