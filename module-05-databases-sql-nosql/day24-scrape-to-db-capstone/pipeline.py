#Day 24 - Phase 1 Capstone: scrape -> transform -> load to Postgres

import os
import time
import logging
import requests
import pandas as pd
from bs4 import BeautifulSoup
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("capstone_pipeline.log"), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

CONFIG = {
    "source_url": "https://scrapeme.live/shop/",
    "user_agent": "Mozilla/5.0 (compatible; TMC-Internship-Capstone/1.0)",
    "request_delay": 1.5,
    "batch_size": 100,
}

PG_HOST = os.getenv("CAPSTONE_PG_HOST")
PG_PORT = os.getenv("CAPSTONE_PG_PORT")
PG_DATABASE = os.getenv("CAPSTONE_PG_DATABASE")
PG_USER = os.getenv("CAPSTONE_PG_USER")
PG_PASSWORD = os.getenv("CAPSTONE_PG_PASSWORD")

CONNECTION_STRING = f"postgresql+psycopg2://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DATABASE}"

# Extract

def fetch_page(url):
    headers = {"User-Agent": CONFIG["user_agent"]}
    response = requests.get(url, headers=headers, timeout=10)
    if response.status_code != 200:
        logger.warning(f"Failed to fetch {url} (status {response.status_code})")
        return None
    return BeautifulSoup(response.text, "html.parser")

def get_total_pages(soup):
    page_links = soup.select("a.page-numbers")
    page_numbers = [int(a.get_text()) for a in page_links if a.get_text().isdigit()]
    return max(page_numbers) if page_numbers else 1

def parse_products(soup):
    products = []
    for item in soup.select("li.product"):
        name_tag = item.select_one("h2")
        price_tag = item.select_one("span.price")
        link_tag = item.select_one("a.woocommerce-LoopProduct-link")
        products.append({
            "name": name_tag.get_text(strip=True) if name_tag else None,
            "price": price_tag.get_text(strip=True) if price_tag else None,
            "url": link_tag["href"] if link_tag else None,
        })
    return products

def extract():
    logger.info("Starting extraction from source...")
    first_page = fetch_page(CONFIG["source_url"])
    if first_page is None:
        return []

    total_pages = get_total_pages(first_page)
    logger.info(f"Found {total_pages} page(s) to scrape.")

    all_products = parse_products(first_page)

    for page_num in range(2, total_pages + 1):
        time.sleep(CONFIG["request_delay"])
        soup = fetch_page(f"{CONFIG['source_url']}page/{page_num}/")
        if soup:
            all_products.extend(parse_products(soup))

    logger.info(f"Extracted {len(all_products)} raw records.")
    return all_products

# Transform

def transform(raw_products):
    logger.info("Transforming data...")
    df = pd.DataFrame(raw_products)

    df = df.dropna(subset=["name"])
    df["price"] = df["price"].str.replace("£", "", regex=False).str.replace(",", "", regex=False)
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df["price"] = df["price"].fillna(df["price"].mean()).round(2)
    df = df.drop_duplicates(subset=["name"])

    logger.info(f"Transformed {len(df)} valid, deduplicated rows.")
    return df

# Load - batched upsert

def load(df, engine, batch_size=100):
    """
    Load rows in batches, upserting on the unique 'name' column.
    Re-running the pipeline updates existing products rather than
    duplicating them - this is what makes the load idempotent.
    """
    records = df.to_dict("records")
    total = len(records)
    logger.info(f"Loading {total} records in batches of {batch_size}...")

    upsert_sql = text("""
        INSERT INTO products (name, price, url)
        VALUES (:name, :price, :url)
        ON CONFLICT (name)
        DO UPDATE SET
            price = EXCLUDED.price,
            url = EXCLUDED.url,
            last_scraped_at = CURRENT_TIMESTAMP
    """)

    with engine.begin() as conn:
        for i in range(0, total, batch_size):
            batch = records[i:i + batch_size]
            conn.execute(upsert_sql, batch)
            logger.info(f"Loaded batch {i // batch_size + 1} ({len(batch)} records)")

    logger.info("Load complete.")

# Orchestration

def run_pipeline():
    logger.info("=== Phase 1 Capstone Pipeline started ===")

    engine = create_engine(CONNECTION_STRING)

    raw_data = extract()
    if not raw_data:
        logger.error("No data extracted. Aborting pipeline.")
        return

    clean_df = transform(raw_data)
    load(clean_df, engine, batch_size=CONFIG["batch_size"])

    with engine.connect() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM products")).scalar()
        logger.info(f"Final row count in 'products' table: {count}")

    logger.info("=== Phase 1 Capstone Pipeline finished ===")

if __name__ == "__main__":
    run_pipeline()