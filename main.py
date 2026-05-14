import requests
import random
import os
import time

WEBHOOK = os.getenv("WEBHOOK_URL")
WORKER_URL = os.getenv("WORKER_URL")

if not WEBHOOK or not WORKER_URL:
    print("Missing WEBHOOK_URL or WORKER_URL")
    exit()

# -------- SAFE DANBOORU TAGS --------

BASE_TAGS = ["valorant"]

RATINGS = [
    "rating:questionable",
    "rating:explicit"
]

# реальные Danbooru-теги (НЕ “boobs”, НЕ “pussy”)
SAFE_TAGS = [
    "female_focus",
    "breasts",
    "cleavage",
    "lingerie",
    "swimsuit",
    "bikini",
    "thighs",
    "panties",
    "nude",
    "topless",
    "cosplay",
    "fanart"
]

FALLBACK_TAGS = [
    "breasts",
    "cleavage",
    "swimsuit",
    "bikini",
    "lingerie"
]

# -------- HELPERS --------

def build_tag():
    base = random.choice(BASE_TAGS)
    rating = random.choice(RATINGS)
    extra = random.choice(SAFE_TAGS)
    return f"{base} {rating} {extra}"

def fetch_post(tag):
    resp = requests.get(
        WORKER_URL,
        params={"tags": tag},
        timeout=30
    )

    if resp.status_code != 200:
        return None

    try:
        data = resp.json()
    except:
        return None

    image = data.get("large_file_url") or data.get("file_url")

    if not image:
        return None

    return {
        "id": data.get("id"),
        "image": image
    }

# -------- MAIN LOOP (FIXED RETRY LOGIC) --------

MAX_ATTEMPTS = 8

post = None
used_tags = set()

for i in range(MAX_ATTEMPTS):
    tag = build_tag()

    # avoid repeating same tag
    if tag in used_tags:
        continue

    used_tags.add(tag)

    print(f"[{i+1}] Searching:", tag)

    post = fetch_post(tag)

    if post:
        break

    time.sleep(1)

# -------- FALLBACK --------

if not post:
    print("Primary search failed, trying fallback...")

    for tag in FALLBACK_TAGS:
        tag_query = f"valorant {tag}"
        print("Fallback:", tag_query)

        post = fetch_post(tag_query)

        if post:
            break

# -------- FINAL CHECK --------

if not post:
    print("No image found at all")
    exit()

image_url = post["image"]

# -------- DISCORD --------

payload = {
    "embeds": [
        {
            "title": "Valorant NSFW",
            "description": "Auto-post generated",
            "image": {"url": image_url}
        }
    ]
}

r = requests.post(WEBHOOK, json=payload, timeout=30)

if r.status_code not in [200, 204]:
    print("Discord error:", r.text)
    exit()

print("Posted successfully:", image_url)