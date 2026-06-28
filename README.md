# Valorant Auto Poster (Discord + GitHub Actions)

This project is an automated Discord posting system that runs on GitHub Actions.
It fetches images directly from booru APIs (rule34 + gelbooru), validates them,
filters duplicates, and posts them to a Discord channel using a webhook.

---

# 🚀 Features

- Fully automated scheduled posting via GitHub Actions
- Discord webhook integration
- **Multi-source**: rule34 (primary) + gelbooru (fallback)
- **Direct API calls** — no Cloudflare Worker / proxy needed
- **Hard explicit-rating validation** (only `rating:explicit` is posted)
- **Comic / stretched-image filtering** (aspect ratio + tag based)
- Persistent duplicate prevention (`posted.txt`, source-prefixed IDs)
- Smart weighted tag memory (`engine_memory.json`)
- Retry + fallback logic across sources
- Free hosting (no VPS required)

---

# 🧠 How It Works

1. GitHub Actions triggers `main.py` on a schedule
2. Script picks a weighted search tag (`valorant rating:explicit <tag>`)
3. Requests a batch of posts directly from rule34 (then gelbooru on failure)
4. Validates each post: explicit rating, sane aspect ratio, not a comic page
5. Skips anything already in `posted.txt`
6. Sends the chosen image as an embed to the Discord webhook
7. Saves the source-prefixed post ID and pushes updated state back to the repo

---

# 📦 Project Structure
```
.
├── main.py             # Main bot engine
├── posted.txt          # Already posted IDs (e.g. r34:12345, gel:678)
├── engine_memory.json  # Tag performance memory
├── requirements.txt    # Python dependencies
└── .github/
    └── workflows/
        └── post.yml    # GitHub Actions workflow
```
---

# ⚙️ Requirements

- GitHub account
- Python 3.10+
- Discord webhook URL
- Free API credentials for rule34 (and optionally gelbooru)

---

# 🔐 Step 1: Create Discord Webhook

1. Open your Discord server
2. Go to channel settings
3. Click **Integrations → Webhooks**
4. Create webhook and copy its URL

---

# 🔑 Step 2: Get booru API keys

Both sites now require a free `api_key` + `user_id` for API access.

**rule34.xxx** (required):
1. Register / log in at https://rule34.xxx
2. Account → **Options** → **API Access Credentials**
3. Copy the `api_key` and `user_id`

**gelbooru.com** (optional fallback):
1. Register / log in at https://gelbooru.com
2. **My Account → Options → API Access Credentials**
3. Copy the `api_key` and `user_id`

> If you skip gelbooru, the bot just runs on rule34 alone.

---

# 🔐 Step 3: Configure GitHub Secrets

Go to: **GitHub → Repository → Settings → Secrets and variables → Actions**

Add:

| Name          | Description                          | Required |
|---------------|--------------------------------------|----------|
| `WEBHOOK_URL` | Discord webhook URL                  | ✅ yes   |
| `R34_API_KEY` | rule34 api_key                       | ✅ yes   |
| `R34_USER_ID` | rule34 user_id                       | ✅ yes   |
| `GEL_API_KEY` | gelbooru api_key                     | optional |
| `GEL_USER_ID` | gelbooru user_id                     | optional |

> The old `WORKER_URL` secret is no longer used and can be deleted.

---

# 🚀 Step 4: Enable GitHub Actions

1. Open the repository
2. Go to the **Actions** tab
3. Enable workflows if prompted

---

# ▶️ Step 5: Run the Bot

**Manual run:**
1. Go to **Actions**
2. Select the workflow
3. Click **Run workflow**

**Automatic run** — configured in the workflow:
```
on:
  schedule:
    - cron: "0 */12 * * *"
```
(This runs every 12 hours.)

---

# 🧾 Step 6: State Persistence

The bot prevents duplicates using `posted.txt`. Each line is a previously
posted content ID, prefixed by its source:

```
r34:12345
gel:67890
9143516        # legacy danbooru IDs (bare numbers) still respected
```
