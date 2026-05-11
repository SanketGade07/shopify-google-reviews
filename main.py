import json
import os
import time
import requests


# =========================
# ENV VARIABLES
# =========================

APIFY_TOKEN = os.getenv("APIFY_TOKEN", "").strip()
GOOGLE_MAPS_URL = os.getenv("GOOGLE_MAPS_URL", "").strip()

ACTOR_ID = "Xb8osYTtOjlsgI6k9"


# =========================
# VALIDATION
# =========================

if not APIFY_TOKEN:
    raise Exception("Missing APIFY_TOKEN")

if not GOOGLE_MAPS_URL:
    raise Exception("Missing GOOGLE_MAPS_URL")


# =========================
# HEADERS
# =========================

headers = {
    "Authorization": f"Bearer {APIFY_TOKEN}",
    "Content-Type": "application/json"
}


# =========================
# ACTOR INPUT
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


# =========================
# START ACTOR
# =========================

start_url = f"https://api.apify.com/v2/acts/{ACTOR_ID}/runs"

response = requests.post(
    start_url,
    headers=headers,
    json=run_input
)

response.raise_for_status()

run_data = response.json()

run_id = run_data["data"]["id"]

print(f"Actor started successfully")
print(f"Run ID: {run_id}")


# =========================
# WAIT FOR COMPLETION
# =========================

status_url = f"https://api.apify.com/v2/actor-runs/{run_id}"

dataset_id = None

while True:

    status_response = requests.get(
        status_url,
        headers=headers
    )

    status_response.raise_for_status()

    status_data = status_response.json()

    status = status_data["data"]["status"]

    print(f"Current status: {status}")

    if status == "SUCCEEDED":
        dataset_id = status_data["data"]["defaultDatasetId"]
        print("Actor completed successfully")
        break

    if status in ["FAILED", "ABORTED", "TIMED-OUT"]:
        raise Exception(f"Actor failed with status: {status}")

    time.sleep(5)


# =========================
# FETCH DATASET ITEMS
# =========================

items_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items"

items_response = requests.get(
    items_url,
    headers=headers
)

items_response.raise_for_status()

reviews = items_response.json()

print(f"Fetched {len(reviews)} reviews")


# =========================
# CLEAN REVIEWS
# =========================

clean_reviews = []

for review in reviews[:8]:

    clean_review = {
        "name": review.get("name", "Customer"),
        "rating": review.get("stars", 5),
        "text": review.get("text", ""),
        "profilePhoto": review.get("reviewerPhotoUrl", "")
    }

    clean_reviews.append(clean_review)


# =========================
# SAVE JSON FILE
# =========================

with open("reviews.json", "w", encoding="utf-8") as file:

    json.dump(
        clean_reviews,
        file,
        ensure_ascii=False,
        indent=2
    )


print("reviews.json updated successfully")
print(f"Saved {len(clean_reviews)} reviews")