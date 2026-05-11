import json
import os
import time
import requests


APIFY_TOKEN = os.getenv("APIFY_TOKEN")
GOOGLE_MAPS_URL = os.getenv("GOOGLE_MAPS_URL")


ACTOR_ID = "Xb8osYTtOjlsgI6k9"


if not APIFY_TOKEN:
    raise Exception("Missing APIFY_TOKEN")

if not GOOGLE_MAPS_URL:
    raise Exception("Missing GOOGLE_MAPS_URL")


headers = {
    "Authorization": f"Bearer {APIFY_TOKEN}",
    "Content-Type": "application/json"
}


# =========================
# START ACTOR
# =========================

run_input = {
    "startUrls": [
        {
            "url": GOOGLE_MAPS_URL
        }
    ],
    "maxReviews": 8,
    "reviewsSort": "newest"
}


start_url = f"https://api.apify.com/v2/acts/{ACTOR_ID}/runs"

response = requests.post(start_url, headers=headers, json=run_input)
response.raise_for_status()

run_data = response.json()

run_id = run_data["data"]["id"]

print(f"Run started: {run_id}")


# =========================
# WAIT FOR COMPLETION
# =========================

status_url = f"https://api.apify.com/v2/actor-runs/{run_id}"

while True:
    status_response = requests.get(status_url, headers=headers)
    status_response.raise_for_status()

    status_data = status_response.json()

    status = status_data["data"]["status"]

    print(f"Current status: {status}")

    if status == "SUCCEEDED":
        dataset_id = status_data["data"]["defaultDatasetId"]
        break

    if status in ["FAILED", "ABORTED", "TIMED-OUT"]:
        raise Exception(f"Actor failed with status: {status}")

    time.sleep(5)


# =========================
# FETCH DATASET ITEMS
# =========================

items_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items"

items_response = requests.get(items_url, headers=headers)
items_response.raise_for_status()

reviews = items_response.json()


# =========================
# CLEAN DATA
# =========================

clean_reviews = []

for review in reviews[:8]:
    clean_reviews.append({
        "rating": review.get("stars"),
        "text": review.get("text"),
        "profilePhoto": review.get("reviewerPhotoUrl")
    })


# =========================
# SAVE JSON FILE
# =========================

with open("reviews.json", "w", encoding="utf-8") as file:
    json.dump(clean_reviews, file, ensure_ascii=False, indent=2)


print("reviews.json updated successfully")