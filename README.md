# Valorant Auto Poster (Discord + GitHub Actions)

This project is an automated Discord posting system that runs on GitHub Actions.  
It fetches images from an API (optionally via Cloudflare Worker), filters duplicates, and posts them to a Discord channel using a webhook.

---

# 🚀 Features

- Fully automated scheduled posting via GitHub Actions
- Discord webhook integration
- Persistent duplicate prevention (`posted.txt`)
- Lightweight Python engine (no heavy dependencies)
- Retry + fallback logic for API requests
- Optional Cloudflare Worker API proxy
- Simple file-based memory system
- Free hosting (no VPS required)

---

# 🧠 How It Works

1. GitHub Actions triggers `main.py` on a schedule
2. Script generates search tags
3. Requests image data from API / Worker
4. Filters already posted content using `posted.txt`
5. Sends embed to Discord webhook
6. Saves post ID for future runs
7. Pushes updated state back to repository

---

# 📦 Project Structure
```
.
├── main.py # Main bot engine
├── posted.txt # List of already posted IDs
├── engine_memory.json # Tag performance memory (optional)
├── requirements.txt # Python dependencies
└── .github/
└── workflows/
└── post.yml # GitHub Actions workflow
```
---

# ⚙️ Requirements

- GitHub account
- Python 3.10+
- Discord webhook URL
- (Optional) Cloudflare Worker for API proxy

---

# 🔐 Step 1: Create Discord Webhook

1. Open your Discord server
2. Go to channel settings
3. Click **Integrations → Webhooks**
4. Create webhook
5. Copy webhook URL

You will use it in GitHub Secrets.

---

# ☁️ Step 2: (Optional) Cloudflare Worker Setup

If you use an API proxy:

1. Go to the dashboard
2. Open **Workers & AI**
3. Create a new Worker
4. Deploy a script that returns JSON like:

```json
{
  "id": 123456,
  "file_url": "https://example.com/image.jpg",
  "large_file_url": "https://example.com/image_large.jpg"
}
```
---

Copy Worker URL:

https://your-worker.workers.dev/?tags=valorant

🔐 Step 3: Configure GitHub Secrets

Go to:

GitHub → Repository → Settings → Secrets and variables → Actions

Add:
```

Name	       | Description
WEBHOOK_URL	 | Discord webhook URL
WORKER_URL	 | API endpoint (Cloudflare Worker or direct API)

```
---

🚀 Step 4: Enable GitHub Actions

Open repository

Go to Actions tab

Enable workflows if prompted

---

▶️ Step 5: Run the Bot

Manual Run:
1. Go to Actions
2. Select workflow
3. Click Run workflow
4. Automatic Run:

Configured in workflow:
```
on:
  schedule:
    - cron: "0 */2 * * *"
```

(This runs every 2 hours)

---

🧾 Step 6: State Persistence

The bot prevents duplicates using posted.txt

Example:

123456

789012

345678

Each line represents a previously posted content ID.
