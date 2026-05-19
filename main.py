import requests
import random
import os
import time
import json

WEBHOOK = os.getenv("WEBHOOK_URL")
WORKER_URL = os.getenv("WORKER_URL")

if not WEBHOOK or not WORKER_URL:
    print("Missing env vars")
    exit()

# -------- CORE TAG SYSTEM --------

BASE = "valorant"

RATINGS = [
    "rating:questionable",
    "rating:explicit"
]

TAG_POOL = [
    "breasts",
    "cleavage",
    "thighs",
    "swimsuit",
    "bikini",
    "lingerie",
    "panties",
    "cosplay",
    "fanart",
    "female_focus"
]

# -------- MEMORY --------

MEM_FILE = "engine_memory.json"
POSTED_FILE = "posted.txt"

def load_json(path, default):
    if os.path.exists(path):
        try:
            return json.load(open(path, "r"))
        except:
            return default
    return default

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f)

memory = load_json(MEM_FILE, {})
posted = set()

if os.path.exists(POSTED_FILE):
    posted = set(open(POSTED_FILE).read().splitlines())

# -------- TAG SELECTION (SMART WEIGHTED) --------

def pick_tag():
    if not memory:
        return random.choice(TAG_POOL)

    items = list(TAG_POOL)
    weights = [memory.get(t, 1) for t in items]

    return random.choices(items, weights=weights, k=1)[0]

# -------- API --------

def fetch_post(tag):
    try:
        r = requests.get(
            WORKER_URL,
            params={"tags": tag},
            timeout=30
        )

        if r.status_code != 200:
            return None

        data = r.json()

        img = data.get("large_file_url") or data.get("file_url")
        pid = str(data.get("id"))

        if not img or pid in posted:
            return None

        return data

    except:
        return None

# -------- ENGINE LOOP --------

MAX_TRIES = 12
post = None
used_tags = set()

for i in range(MAX_TRIES):

    tag = f"{BASE} {random.choice(RATINGS)} {pick_tag()}"

    if tag in used_tags:
        continue

    used_tags.add(tag)

    print(f"[TRY {i+1}] {tag}")

    result = fetch_post(tag)

    if result:
        post = result

        # ---- reward successful tags ----
        for t in tag.split():
            memory[t] = memory.get(t, 0) + 2

        break

    # ---- punish failure ----
    for t in tag.split():
        memory[t] = memory.get(t, 1) * 0.9

    time.sleep(1)

# -------- FALLBACK LAYER --------

if not post:
    print("Fallback mode...")

    for t in TAG_POOL:
        tag = f"{BASE} {t}"
        post = fetch_post(tag)
        if post:
            break

if not post:
    print("No image found")
    exit()

# -------- FINAL VALIDATION --------

image_url = post.get("large_file_url") or post.get("file_url")
post_id = str(post.get("id"))

# -------- SAVE POSTED --------

with open(POSTED_FILE, "a") as f:
    f.write(post_id + "\n")

save_json(MEM_FILE, memory)

# -------- DISCORD --------

payload = {
    "embeds": [
        {
            "title": "Valorant NSFW",
            "description": f"Post ID: {post_id}",
            "image": {"url": image_url}
        }
    ]
}

r = requests.post(WEBHOOK, json=payload)

if r.status_code not in [200, 204]:
    print("Discord error:", r.text)
    exit()

print("Posted:", image_url)