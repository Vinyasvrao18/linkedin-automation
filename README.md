# 🎓 LinkedIn Certification Post Automation

Automatically read your certification images using **Ollama** (local AI), generate professional LinkedIn posts, and publish them on a **weekly schedule** — all running locally on your machine.

## How It Works

```
certificates/          Ollama (llava)        Ollama (llama3)        LinkedIn API
┌──────────────┐      ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│ cert1.png    │ ───► │ Extract name │ ───► │ Generate a   │ ───► │ Auto-publish │
│ cert2.jpg    │      │ issuer, date │      │ LinkedIn     │      │ on Mon & Thu │
│ cert3.webp   │      │ skills       │      │ post         │      │ at 10:00 AM  │
└──────────────┘      └──────────────┘      └──────────────┘      └──────────────┘
```

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.10+ | Runtime |
| Ollama | 0.3+ | Local AI for reading certs & writing posts |
| `llava` model | — | Vision model to read certificate images |
| `llama3` model | — | Text model to write LinkedIn posts |

## Quick Setup

### 1. Install Ollama models

```bash
ollama pull llava
ollama pull llama3
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up LinkedIn API credentials

1. Go to [LinkedIn Developer Portal](https://www.linkedin.com/developers/apps)
2. Create a new app (or use an existing one)
3. Under **Auth** → add the product **"Share on LinkedIn"**
4. Generate an OAuth 2.0 access token with scope `w_member_social`
5. Find your Person URN: call `GET https://api.linkedin.com/v2/me` with your token

### 4. Create your `.env` file

```bash
copy .env.example .env
```

Edit `.env` with your real credentials:

```env
LINKEDIN_ACCESS_TOKEN=your_real_token_here
LINKEDIN_PERSON_URN=urn:li:person:your_person_id
```

### 5. Add certificate images

Drop your certificate screenshots/images into the `certificates/` folder:
- Supported formats: **PNG, JPG, JPEG, WEBP**

### 6. Run it!

```bash
python main.py
```

## Project Structure

```
LinkedInAutomation/
├── certificates/       # Drop your cert images here (PNG/JPG/WEBP)
├── posts/
│   └── generated_posts.json  # Generated posts with status tracking
├── cert_reader.py      # Reads cert images via Ollama vision (llava)
├── post_generator.py   # Generates LinkedIn posts via Ollama (llama3)
├── linkedin.py         # Posts to LinkedIn via API (OAuth 2.0)
├── scheduler.py        # Weekly scheduler (Mon & Thu at 10:00 AM)
├── config.py           # All configuration (reads from .env)
├── main.py             # Entry point – runs the full pipeline
├── .env.example        # Template for secrets
├── .env                # Your secrets (gitignored)
└── requirements.txt    # Python dependencies
```

## Configuration

All settings are in [`config.py`](config.py) and can be overridden via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama API endpoint |
| `OLLAMA_MODEL` | `llama3` | Model for generating post text |
| `OLLAMA_VISION_MODEL` | `llava` | Model for reading certificate images |
| `LINKEDIN_ACCESS_TOKEN` | — | Your LinkedIn OAuth token |
| `LINKEDIN_PERSON_URN` | — | Your LinkedIn person URN |
| `SCHEDULE_DAYS` | `[0, 3]` | Days to post (0=Mon, 3=Thu) |
| `SCHEDULE_TIME` | `10:00` | Time to post (24h format) |

## Customising the Schedule

Edit `config.py` to change posting days and time:

```python
# Post every Wednesday and Friday at 2:30 PM
SCHEDULE_DAYS = [2, 4]       # 0=Mon, 1=Tue, 2=Wed, 3=Thu, 4=Fri
SCHEDULE_TIME = "14:30"
```

## Post Status Tracking

Each generated post has a status tracked in `posts/generated_posts.json`:

| Status | Meaning |
|--------|---------|
| `pending` | Generated, waiting to be published |
| `posted` | Successfully published to LinkedIn |
| `failed` | Publishing failed (error is logged) |

## Troubleshooting

- **"Ollama connection refused"** → Make sure Ollama is running: `ollama serve`
- **"No certificate images found"** → Add images to the `certificates/` folder
- **"LinkedIn credentials invalid"** → Check your access token hasn't expired (they last ~60 days)
- **Posts not appearing** → LinkedIn API has rate limits; check `generated_posts.json` for error details
