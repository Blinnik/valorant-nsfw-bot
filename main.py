import requests
import random
import os
import time
import json

# ============================================================
#  Valorant NSFW Bot  v3.0
#  - Multi-source (rule34 primary, gelbooru fallback)
#  - Direct API calls (no Cloudflare worker needed)
#  - Hard explicit-rating validation
#  - Comic / stretched-image filtering
# ============================================================

WEBHOOK = os.getenv("WEBHOOK_URL")
if not WEBHOOK:
    print("Missing WEBHOOK_URL")
    exit(1)

# -------- SOURCES --------
# Each booru now requires a free api_key + user_id (get them in your
# account settings on the site). gelbooru is optional: if its keys are
# missing it is simply skipped.

R34_KEY = os.getenv("R34_API_KEY")
R34_USER = os.getenv("R34_USER_ID")
GEL_KEY = os.getenv("GEL_API_KEY")
GEL_USER = os.getenv("GEL_USER_ID")

SOURCES = []

if R34_KEY and R34_USER:
    SOURCES.append({
        "name": "rule34",
        "prefix": "r34",
        "kind": "list",          # response is a JSON array
        "max_tags": 4,           # rule34 allows many tags
        "url": "https://api.rule34.xxx/index.php",
        "params": {
            "page": "dapi", "s": "post", "q": "index", "json": "1",
            "limit": "100", "api_key": R34_KEY, "user_id": R34_USER,
        },
    })

if GEL_KEY and GEL_USER:
    SOURCES.append({
        "name": "gelbooru",
        "prefix": "gel",
        "kind": "dict",          # response is {"post": [...]} (or [])
        "max_tags": 2,           # gelbooru is stricter on tag count
        "url": "https://gelbooru.com/index.php",
        "params": {
            "page": "dapi", "s": "post", "q": "index", "json": "1",
            "limit": "100", "api_key": GEL_KEY, "user_id": GEL_USER,
        },
    })

if not SOURCES:
    print("No source configured. Set R34_API_KEY+R34_USER_ID "
          "and/or GEL_API_KEY+GEL_USER_ID")
    exit(1)

# -------- CORE TAGS --------

BASE = "valorant"
RATING_TAG = "rating:explicit"   # request only explicit from the source

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
    "female_focus",
]

# -------- MEMORY --------

MEM_FILE = "engine_memory.json"
POSTED_FILE = "posted.txt"


def load_json(path, default):
    if os.path.exists(path):
        try:
            return json.load(open(path, "r"))
        except Exception:
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
    weights = [max(memory.get(t, 1), 0.01) for t in TAG_POOL]
    return random.choices(TAG_POOL, weights=weights, k=1)[0]


def build_tags(src, extra=True):
    parts = [BASE, RATING_TAG]
    if extra and src["max_tags"] > len(parts):
        parts.append(pick_tag())
    return " ".join(parts[:src["max_tags"]])


# -------- VALIDATION --------

# Tags that mark comic / multi-panel pages (the "stretched" posts).
BAD_TAGS = {
    "comic", "manga", "4koma", "doujinshi", "comic_strip",
    "comic_page", "multiple_views",
}

MAX_ASPECT = 2.4   # reject anything taller/wider than this ratio


def is_explicit(rating):
    return rating in ("e", "explicit")


def valid(post):
    if not is_explicit(post["rating"]):
        return False
    w, h = post["w"], post["h"]
    if w and h:
        ratio = max(w, h) / min(w, h)
        if ratio > MAX_ASPECT:
            return False
    if set(post["tags"].split()) & BAD_TAGS:
        return False
    return True


# -------- API --------

def normalize(src, raw):
    if src["kind"] == "dict" and isinstance(raw, dict):
        raw = raw.get("post", [])
    if not isinstance(raw, list):
        return []

    out = []
    for p in raw:
        if not isinstance(p, dict):
            continue
        url = p.get("file_url") or p.get("large_file_url")
        pid = p.get("id")
        if not url or pid is None:
            continue
        out.append({
            "id": str(pid),
            "url": url,
            "rating": str(p.get("rating") or "").lower(),
            "w": int(p.get("width") or 0),
            "h": int(p.get("height") or 0),
            "tags": str(p.get("tags") or p.get("tag_string") or "").lower(),
        })
    return out


def fetch(src, tags):
    params = dict(src["params"])
    params["tags"] = tags
    try:
        r = requests.get(
            src["url"],
            params=params,
            timeout=30,
            headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"},
        )
        if r.status_code != 200:
            print(f"  [{src['name']}] HTTP {r.status_code}")
            return []
        return normalize(src, r.json())
    except Exception as e:
        print(f"  [{src['name']}] error: {e}")
        return []


def pick_unseen(src, batch):
    random.shuffle(batch)
    for p in batch:
        if not valid(p):
            continue
        if f"{src['prefix']}:{p['id']}" in posted:
            continue
        return p
    return None


# -------- ENGINE LOOP --------

TRIES_PER_SOURCE = 6

post = None
chosen_src = None
chosen_tags = None

for src in SOURCES:
    for attempt in range(TRIES_PER_SOURCE):
        tags = build_tags(src)
        print(f"[{src['name']}] try {attempt + 1}: {tags}")

        candidate = pick_unseen(src, fetch(src, tags))
        if candidate:
            post, chosen_src, chosen_tags = candidate, src, tags
            break

        # punish a fruitless tag combo
        for t in tags.split():
            memory[t] = memory.get(t, 1) * 0.9
        time.sleep(1)

    if post:
        break

# -------- FALLBACK: broadest explicit query per source --------

if not post:
    print("Fallback mode...")
    for src in SOURCES:
        tags = build_tags(src, extra=False)
        candidate = pick_unseen(src, fetch(src, tags))
        if candidate:
            post, chosen_src, chosen_tags = candidate, src, tags
            break

if not post:
    print("No image found")
    exit(1)

# -------- REWARD SUCCESSFUL TAGS --------

for t in chosen_tags.split():
    memory[t] = memory.get(t, 0) + 2

# -------- SAVE STATE --------

posted_id = f"{chosen_src['prefix']}:{post['id']}"

with open(POSTED_FILE, "a") as f:
    f.write(posted_id + "\n")

save_json(MEM_FILE, memory)

# -------- DISCORD --------

payload = {
    "embeds": [
        {
            "title": "Valorant NSFW",
            "description": f"Source: {chosen_src['name']} | ID: {post['id']}",
            "image": {"url": post["url"]},
        }
    ]
}

r = requests.post(WEBHOOK, json=payload)

if r.status_code not in (200, 204):
    print("Discord error:", r.text)
    exit(1)

print(f"Posted [{posted_id}]: {post['url']}")
