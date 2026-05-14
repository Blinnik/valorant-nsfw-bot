import requests
import random
import os
import time

WEBHOOK = os.getenv("WEBHOOK_URL")

if not WEBHOOK:
    print("WEBHOOK_URL not set")
    exit()

# -------- TAGS --------

BASE_TAGS = [
    "valorant",
]

RATINGS = [
    "rating:questionable",
    "rating:explicit"
]

NSFW_TAGS = [
    "cosplay",
    "fanart",
    "bikini",
    "lingerie",
    "swimsuit",
    "thighs",
    "underboob",
    "sideboob",
    "cleavage",
    "see-through",
    "leotard",
    "cameltoe",
    "topless",
    "nude",
    "boobs",
    "vagina",
    "tits",
    "titties",
    "vagina",
    "pussy",
    "cum",
    "sex",
    "ass",
    "anal"
]

base = random.choice(BASE_TAGS)
rating = random.choice(RATINGS)
extra = random.sample(NSFW_TAGS, 2)

tag = f"{base} {rating} {' '.join(extra)}"

print("Searching tags:", tag)

# -------- DANBOORU API --------

url = "https://danbooru.donmai.us/posts.json"

params = {
    "tags": tag,
    "limit": 50,
    "random": True
}

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, params=params, headers=headers, timeout=30)

if response.status_code != 200:
    print("HTTP ERROR:", response.status_code)
    print(response.text[:300])
    exit()

try:
    posts = response.json()
except Exception as e:
    print("JSON parse error:", e)
    print(response.text[:300])
    exit()

if not posts:
    print("No posts found")
    exit()

# -------- LOAD POSTED --------

posted = set()

if os.path.exists("posted.txt"):
    with open("posted.txt", "r", encoding="utf-8") as f:
        posted = set(f.read().splitlines())

random.shuffle(posts)

# -------- PICK POST --------

new_post = None

for post in posts:
    post_id = str(post.get("id"))
    image_url = post.get("file_url")

    if not post_id or not image_url:
        continue

    if post_id in posted:
        continue

    # only images
    if not image_url.endswith((".jpg", ".jpeg", ".png", ".gif")):
        continue

    new_post = post
    break

if not new_post:
    print("No suitable post found")
    exit()

image_url = new_post["file_url"]
post_id = str(new_post["id"])

# -------- DISCORD --------

payload = {
    "embeds": [
        {
            "title": "Valorant NSFW",
            "description": f"Tags: {tag}",
            "image": {
                "url": image_url
            }
        }
    ]
}

resp = requests.post(WEBHOOK, json=payload, timeout=30)

if resp.status_code not in [200, 204]:
    print("Discord error:", resp.text)
    exit()

# -------- SAVE --------

with open("posted.txt", "a", encoding="utf-8") as f:
    f.write(post_id + "\n")

print("Posted successfully!")
print(image_url)