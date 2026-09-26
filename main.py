"""Entry point for LinkedIn Automation."""

from scheduler import start_scheduler
from post_generator import generate_posts

def main():
    # Generate initial posts JSON if needed
    generate_posts()
    # Start background scheduler to post at intervals
    start_scheduler()

if __name__ == "__main__":
    main()
