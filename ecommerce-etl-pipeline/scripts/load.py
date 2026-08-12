"""
Load task for the scrapeme.live ETL pipeline.

Takes the cleaned product data (pulled from XCom) and upserts it into
the postgres-target database. Uses ON CONFLICT on sku so re-running
the DAG for the same products updates existing rows instead of
creating duplicates (idempotency requirement).
"""

import json
import logging
import os

import psycopg2

logger = logging.getLogger(__name__)


def get_connection():
    return psycopg2.connect(
        host=os.environ.get("ETL_DB_HOST", "postgres-target"),
        port=os.environ.get("ETL_DB_PORT", "5432"),
        dbname=os.environ.get("ETL_DB_NAME", "ecommerce_data"),
        user=os.environ.get("ETL_DB_USER", "etl_user"),
        password=os.environ.get("ETL_DB_PASSWORD", "etl_password"),
    )


UPSERT_PRODUCT_SQL = """
    INSERT INTO products (
        sku, title, description, product_url, image_url,
        price_current, price_original, stock_quantity, in_stock, category,
        scraped_at, updated_at
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
    ON CONFLICT (sku) DO UPDATE SET
        title = EXCLUDED.title,
        description = EXCLUDED.description,
        product_url = EXCLUDED.product_url,
        image_url = EXCLUDED.image_url,
        price_current = EXCLUDED.price_current,
        price_original = EXCLUDED.price_original,
        stock_quantity = EXCLUDED.stock_quantity,
        in_stock = EXCLUDED.in_stock,
        category = EXCLUDED.category,
        updated_at = NOW();
"""


def load_product(cursor, product):
    cursor.execute(UPSERT_PRODUCT_SQL, (
        product["sku"],
        product["title"],
        product["description"],
        product["product_url"],
        product["image_url"],
        product["price_current"],
        product["price_original"],
        product["stock_quantity"],
        product["in_stock"],
        product["category"],
    ))


def load(**context):
    """Airflow task entrypoint. Pulls cleaned products from XCom and
    upserts each one into Postgres inside a single transaction."""
    ti = context["ti"]
    cleaned_json = ti.xcom_pull(key="cleaned_products", task_ids="transform_task")
    cleaned_products = json.loads(cleaned_json) if cleaned_json else []

    if not cleaned_products:
        logger.warning("No products to load - skipping")
        return 0

    conn = get_connection()
    loaded_count = 0

    try:
        with conn:
            with conn.cursor() as cursor:
                for product in cleaned_products:
                    load_product(cursor, product)
                    loaded_count += 1
        logger.info("Load complete: %d products upserted", loaded_count)
    except Exception as e:
        logger.error("Load failed, transaction rolled back: %s", e)
        raise
    finally:
        conn.close()

    return loaded_count