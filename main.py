import requests
import random
import os

WEBHOOK = os.getenv("WEBHOOK_URL")

WORKER_URL = os.getenv("WORKER_URL")

BASE_TAGS = ["valorant"]

RATINGS = ["rating:questionable", "rating:explicit"]

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
extra = random.sample(NSFW_TAGS, 1)

tag = f"{base} {rating} {' '.join(extra)}"

print("Searching tags:", tag)

# -------- CALL WORKER --------

resp = requests.get(
    WORKER_URL,
    params={"tags": tag},
    timeout=30
)

if resp.status_code != 200:
    print("Worker error:", resp.text)
    exit()

data = resp.json()

image_url = data.get("large_file_url") or data.get("file_url")

if not image_url:
    print("No image found")
    exit()

# -------- DISCORD --------

payload = {
    "embeds": [
        {
            "title": "Valorant NSFW",
            "description": f"Tags: {tag}",
            "image": {"url": image_url}
        }
    ]
}

r = requests.post(WEBHOOK, json=payload)

if r.status_code not in [200, 204]:
    print("Discord error:", r.text)
    exit()

print("Posted:", image_url)