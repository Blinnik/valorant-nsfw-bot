import requests
import random
import os
import json

WEBHOOK = os.getenv("WEBHOOK_URL")

BASE_TAGS = [
    "valorant",
    "valorant_(series)"
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
    "nude"
]

base = random.choice(BASE_TAGS)

rating = random.choice(RATINGS)

extra = random.sample(NSFW_TAGS, 3)

tag = f"{base} {rating} {' '.join(extra)}"

print(f"Searching tags: {tag}")

# Gelbooru API
url = (
    "https://gelbooru.com/index.php"
    "?page=dapi"
    "&s=post"
    "&q=index"
    "&json=1"
    "&limit=100"
    f"&tags={tag}"
)

response = requests.get(url, timeout=30)

try:
    data = response.json()
except json.JSONDecodeError:
    print("Failed to parse JSON")
    exit()

if "post" not in data:
    print("No posts found")
    exit()

posts = data["post"]

# Загружаем список уже опубликованных постов
posted = set()

if os.path.exists("posted.txt"):
    with open("posted.txt", "r", encoding="utf-8") as f:
        posted = set(f.read().splitlines())

random.shuffle(posts)

new_post = None

for post in posts:

    post_id = str(post.get("id"))

    if post_id in posted:
        continue

    image_url = post.get("file_url", "")

    # Только картинки
    if not image_url.endswith((".jpg", ".jpeg", ".png", ".gif")):
        continue

    # Иногда API отдаёт мусор
    if "video" in image_url:
        continue

    new_post = post
    break

if not new_post:
    print("No suitable new post found")
    exit()

image_url = new_post["file_url"]

# Discord Embed
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

response = requests.post(WEBHOOK, json=payload, timeout=30)

if response.status_code not in [200, 204]:
    print("Failed to send to Discord")
    print(response.text)
    exit()

# Сохраняем ID опубликованного поста
with open("posted.txt", "a", encoding="utf-8") as f:
    f.write(f"{new_post['id']}\n")

print("Posted successfully!")
print(image_url)