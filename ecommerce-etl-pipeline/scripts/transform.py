"""
Transform task for the scrapeme.live ETL pipeline.

Takes the raw scraped product data (pulled from XCom) and cleans it:
whitespace normalization, price parsing into numeric values, stock
quantity extraction, and graceful handling of missing/out-of-stock
fields. Cleaned data is pushed back to XCom for the load task.
"""

import json
import logging
import re

logger = logging.getLogger(__name__)


def clean_text(value):
    """Strip extra whitespace and normalize None/empty values."""
    if not value:
        return None
    cleaned = re.sub(r"\s+", " ", value).strip()
    return cleaned if cleaned else None


def parse_price(price_raw):
    """
    scrapeme.live prices look like '£63.00' for a normal price, or
    '£63.00£50.00' (original + sale price glued together) when on sale.
    Returns (current_price, original_price) as floats, original_price
    is None when there's no sale.
    """
    if not price_raw:
        return None, None

    # Extract all numbers that look like prices (with optional decimals)
    matches = re.findall(r"[\d,]+\.\d{2}", price_raw)
    prices = [float(m.replace(",", "")) for m in matches]

    if len(prices) == 0:
        return None, None
    if len(prices) == 1:
        return prices[0], None
    # Two prices found: first is original (strikethrough), second is current
    return prices[-1], prices[0]


def parse_stock(stock_raw):
    """
    scrapeme.live shows stock as e.g. '45 in stock' or 'Out of stock'.
    Returns (quantity, in_stock_bool). Missing/unparseable stock is
    handled gracefully rather than raising - quantity becomes None.
    """
    if not stock_raw:
        return None, None

    stock_lower = stock_raw.lower()
    if "out of stock" in stock_lower:
        return 0, False

    match = re.search(r"(\d+)\s*in stock", stock_lower)
    if match:
        return int(match.group(1)), True

    # Stock text present but in an unexpected format - don't fail the
    # pipeline, just record that we couldn't determine the quantity.
    logger.warning("Could not parse stock text: %r", stock_raw)
    return None, None


def transform_product(raw_product):
    """Clean a single raw product dict into the structured format that
    matches the products table schema. Returns None if the product is
    missing required fields (sku, title) since those can't be recovered."""
    sku = clean_text(raw_product.get("sku"))
    title = clean_text(raw_product.get("title"))

    if not sku or not title:
        logger.warning("Skipping product with missing sku/title: %s", raw_product.get("url"))
        return None

    price_current, price_original = parse_price(raw_product.get("price_raw"))
    stock_quantity, in_stock = parse_stock(raw_product.get("stock_raw"))

    return {
        "sku": sku,
        "title": title,
        "description": clean_text(raw_product.get("description")),
        "product_url": raw_product.get("url"),
        "image_url": raw_product.get("image_url"),
        "price_current": price_current,
        "price_original": price_original,
        "stock_quantity": stock_quantity,
        "in_stock": in_stock,
        "category": clean_text(raw_product.get("category")),
    }


def transform(**context):
    """Airflow task entrypoint. Pulls raw products from XCom, cleans
    each one, and pushes the cleaned list back to XCom for load."""
    ti = context["ti"]
    raw_json = ti.xcom_pull(key="raw_products", task_ids="extract_task")
    raw_products = json.loads(raw_json) if raw_json else []

    cleaned_products = []
    skipped_count = 0

    for raw_product in raw_products:
        cleaned = transform_product(raw_product)
        if cleaned:
            cleaned_products.append(cleaned)
        else:
            skipped_count += 1

    logger.info(
        "Transform complete: %d cleaned, %d skipped due to missing required fields",
        len(cleaned_products), skipped_count,
    )

    ti.xcom_push(key="cleaned_products", value=json.dumps(cleaned_products))
    return len(cleaned_products)