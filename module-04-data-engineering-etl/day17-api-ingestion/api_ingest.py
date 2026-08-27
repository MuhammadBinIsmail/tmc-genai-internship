# Day 17 - APIs & Data Ingestion

import os
import json
import time
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
BASE_URL = "https://api.github.com/orgs/python/repos"
STAGING_DIR = "staging"
MAX_RETRIES = 3
PER_PAGE = 30

def build_headers():
    headers = {"Accept": "application/vnd.github+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    return headers

def fetch_with_retry(url, headers, params=None):
    """Fetch a URL with exponential backoff on failure, including network errors."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
        except requests.exceptions.RequestException as e:
            wait_time = 2 ** attempt
            print(f"Attempt {attempt} failed (network error: {e}). Retrying in {wait_time}s...")
            time.sleep(wait_time)
            continue

        if response.status_code == 200:
            return response

        if response.status_code == 403:
            print("Rate limit likely hit. Stopping retries for this request.")
            return None

        wait_time = 2 ** attempt
        print(f"Attempt {attempt} failed (status {response.status_code}). Retrying in {wait_time}s...")
        time.sleep(wait_time)

    print(f"Failed to fetch {url} after {MAX_RETRIES} attempts.")
    return None

def get_next_page_url(response):
    """Parse the Link header to find the next page URL, if one exists."""
    link_header = response.headers.get("Link")
    if not link_header:
        return None

    links = link_header.split(", ")
    for link in links:
        if 'rel="next"' in link:
            return link[link.find("<") + 1: link.find(">")]

    return None

def ingest_all_pages(url):
    """Fetch every page of results, following pagination via the Link header."""
    headers = build_headers()
    all_records = []
    page_num = 1
    params = {"per_page": PER_PAGE}

    while url:
        print(f"Fetching page {page_num}...")
        response = fetch_with_retry(url, headers, params if page_num == 1 else None)

        if response is None:
            break

        data = response.json()
        all_records.extend(data)

        save_raw_response(data, page_num)

        url = get_next_page_url(response)
        page_num += 1

    return all_records

def save_raw_response(data, page_num):
    """Save each raw API page response to a staging directory before processing."""
    os.makedirs(STAGING_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d")
    filename = f"{STAGING_DIR}/github_repos_page{page_num}_{timestamp}.json"

    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Saved raw response to {filename}")

def main():
    records = ingest_all_pages(BASE_URL)
    print(f"\nIngested {len(records)} total records across all pages.")

if __name__ == "__main__":
    main()