# Day 18 - Building an ETL Pipeline: etl_pipeline.py

import os
import time
import sqlite3
import logging
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("etl_pipeline.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

CONFIG = {
    "products_url": "https://scrapeme.live/shop/",
    "github_url": "https://api.github.com/orgs/python/repos",
    "user_agent": "Mozilla/5.0 (compatible; TMC-Internship-ETL/1.0)",
    "request_delay": 1.5,
    "max_retries": 3,
    "db_path": "etl_data.db",
}

# Extract

def fetch_with_retry(url, headers=None, params=None):
    for attempt in range(1, CONFIG["max_retries"] + 1):
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                return response
            logger.warning(f"Attempt {attempt} failed (status {response.status_code}) for {url}")
        except requests.exceptions.RequestException as e:
            logger.warning(f"Attempt {attempt} failed (network error: {e}) for {url}")

        time.sleep(2 ** attempt)

    logger.error(f"Failed to fetch {url} after {CONFIG['max_retries']} attempts.")
    return None

def extract_products():
    """Extract product listings from scrapeme.live."""
    logger.info("Extracting product data...")
    headers = {"User-Agent": CONFIG["user_agent"]}
    response = fetch_with_retry(CONFIG["products_url"], headers=headers)

    if response is None:
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    items = soup.select("li.product")

    products = []
    for item in items:
        name_tag = item.select_one("h2")
        price_tag = item.select_one("span.price")
        products.append({
            "name": name_tag.get_text(strip=True) if name_tag else None,
            "price": price_tag.get_text(strip=True) if price_tag else None,
        })

    logger.info(f"Extracted {len(products)} products.")
    return products

def extract_github_repos():
    """Extract public repo data from the GitHub API."""
    logger.info("Extracting GitHub repo data...")
    response = fetch_with_retry(CONFIG["github_url"], params={"per_page": 30})

    if response is None:
        return []

    data = response.json()
    repos = [
        {
            "name": repo.get("name"),
            "stars": repo.get("stargazers_count"),
            "language": repo.get("language"),
            "created_at": repo.get("created_at"),
        }
        for repo in data
    ]

    logger.info(f"Extracted {len(repos)} repos.")
    return repos

# Transform

def transform_products(raw_products):
    """Clean and validate product data using pandas."""
    logger.info("Transforming product data...")
    df = pd.DataFrame(raw_products)

    if df.empty:
        logger.warning("No product data to transform.")
        return df

    df = df.dropna(subset=["name"])
    df["price"] = (
        df["price"]
        .str.replace("£", "", regex=False)
        .str.replace(",", "", regex=False)
    )
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df["price"] = df["price"].fillna(df["price"].mean()).round(2)

    logger.info(f"Transformed {len(df)} valid product rows.")
    return df

def transform_repos(raw_repos):
    """Clean and validate GitHub repo data using pandas."""
    logger.info("Transforming repo data...")
    df = pd.DataFrame(raw_repos)

    if df.empty:
        logger.warning("No repo data to transform.")
        return df

    df = df.dropna(subset=["name"])
    df["language"] = df["language"].fillna("Unknown")
    df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
    df["stars"] = df["stars"].fillna(0).astype(int)

    logger.info(f"Transformed {len(df)} valid repo rows.")
    return df

# Load

def load_to_sqlite(df, table_name, db_path):
    """Load a DataFrame into SQLite, replacing the table for a clean, idempotent re-run."""
    if df.empty:
        logger.warning(f"Skipping load for '{table_name}' - no data.")
        return

    conn = sqlite3.connect(db_path)
    try:
        df.to_sql(table_name, conn, if_exists="replace", index=False)
        logger.info(f"Loaded {len(df)} rows into '{table_name}' table.")
    finally:
        conn.close()

# Pipeline orchestration

def run_pipeline():
    logger.info("=== ETL Pipeline started ===")

    raw_products = extract_products()
    raw_repos = extract_github_repos()

    products_df = transform_products(raw_products)
    repos_df = transform_repos(raw_repos)

    load_to_sqlite(products_df, "products", CONFIG["db_path"])
    load_to_sqlite(repos_df, "github_repos", CONFIG["db_path"])

    logger.info("=== ETL Pipeline finished ===")

if __name__ == "__main__":
    run_pipeline()