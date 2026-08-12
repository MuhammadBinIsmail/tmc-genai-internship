"""
Extract task for the scrapeme.live ETL pipeline.

Walks the paginated product listing (scrapeme.live/shop/) to collect
product detail page URLs, then visits each product page individually
to scrape its title, description, price, image, stock status, SKU,
and category. Raw results are passed to the transform task via XCom.
"""

import time
import random
import json
import logging

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

BASE_URL = "https://scrapeme.live/shop/"
MAX_PAGES = 5  # bump this up to scrape more products; 48 = full catalog (755 items)
REQUEST_DELAY_RANGE = (1, 3)  # seconds, randomized delay between requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}


def _polite_delay():
    time.sleep(random.uniform(*REQUEST_DELAY_RANGE))


def _get_with_retries(url, max_retries=3):
    """GET a URL with basic retry/backoff. Raises on final failure so the
    Airflow task itself can retry via its own retry config."""
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            logger.warning("Attempt %d/%d failed for %s: %s", attempt, max_retries, url, e)
            if attempt == max_retries:
                raise
            time.sleep(2 ** attempt)  # exponential backoff


def get_product_links(max_pages=MAX_PAGES):
    """Walk the paginated shop listing and collect product detail page URLs."""
    product_links = []

    for page_num in range(1, max_pages + 1):
        url = BASE_URL if page_num == 1 else f"{BASE_URL}page/{page_num}/"
        logger.info("Fetching listing page %d: %s", page_num, url)

        response = _get_with_retries(url)
        soup = BeautifulSoup(response.text, "html.parser")

        links_on_page = soup.select("li.product a.woocommerce-LoopProduct-link")
        if not links_on_page:
            logger.info("No products found on page %d, stopping pagination", page_num)
            break

        for link in links_on_page:
            href = link.get("href")
            if href:
                product_links.append(href)

        _polite_delay()

    logger.info("Collected %d product links total", len(product_links))
    return product_links


def scrape_product(url):
    """Scrape a single product detail page. Returns a raw dict of fields,
    or None if the page failed to parse (caller decides how to handle)."""
    try:
        response = _get_with_retries(url)
        soup = BeautifulSoup(response.text, "html.parser")

        title_el = soup.select_one("h1.product_title")
        price_el = soup.select_one("p.price")
        desc_el = soup.select_one("div.woocommerce-product-details__short-description")
        stock_el = soup.select_one("p.stock")
        sku_el = soup.select_one("span.sku")
        image_el = soup.select_one("div.woocommerce-product-gallery img")
        category_el = soup.select_one("span.posted_in a")

        return {
            "url": url,
            "title": title_el.get_text(strip=True) if title_el else None,
            "price_raw": price_el.get_text(strip=True) if price_el else None,
            "description": desc_el.get_text(strip=True) if desc_el else None,
            "stock_raw": stock_el.get_text(strip=True) if stock_el else None,
            "sku": sku_el.get_text(strip=True) if sku_el else None,
            "image_url": image_el.get("src") if image_el else None,
            "category": category_el.get_text(strip=True) if category_el else None,
        }
    except Exception as e:
        logger.error("Failed to scrape product page %s: %s", url, e)
        return None


def extract(**context):
    """Airflow task entrypoint. Scrapes listing pages + product pages,
    then pushes the raw results to XCom for the transform task."""
    product_links = get_product_links()

    raw_products = []
    for i, link in enumerate(product_links, start=1):
        logger.info("Scraping product %d/%d: %s", i, len(product_links), link)
        product_data = scrape_product(link)
        if product_data:
            raw_products.append(product_data)
        _polite_delay()

    logger.info("Extract complete: %d/%d products scraped successfully",
                len(raw_products), len(product_links))

    ti = context["ti"]
    ti.xcom_push(key="raw_products", value=json.dumps(raw_products))
    return len(raw_products)