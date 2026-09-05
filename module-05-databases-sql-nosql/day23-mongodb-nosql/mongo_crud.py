# Day 23 - MongoDB & NoSQL Concepts

import os
import json
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_HOST = os.getenv("MONGO_HOST")
MONGO_PORT = os.getenv("MONGO_PORT")
MONGO_USER = os.getenv("MONGO_USER")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")
MONGO_DB = os.getenv("MONGO_DB")

CONNECTION_STRING = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/"


def get_client():
    return MongoClient(CONNECTION_STRING)


def load_scraped_products(collection, filepath="products.json"):
    """Load Day 16's scraped product JSON into a MongoDB collection."""
    if not os.path.exists(filepath):
        print(f"{filepath} not found. Run Day 16's scraper.py first.")
        return

    with open(filepath, "r") as f:
        products = json.load(f)

    collection.delete_many({})  # clear existing data for a clean, repeatable load
    result = collection.insert_many(products)
    print(f"Inserted {len(result.inserted_ids)} documents.")


def create_product(collection, product):
    """CREATE: insert a single document."""
    result = collection.insert_one(product)
    return result.inserted_id


def read_products_by_price_range(collection, min_price, max_price):
    """READ: query operators - $gte and $lte for a price range."""
    return list(collection.find({
        "price_numeric": {"$gte": min_price, "$lte": max_price}
    }))


def update_product_price(collection, name, new_price):
    """UPDATE: modify a field on a matching document."""
    result = collection.update_one(
        {"name": name},
        {"$set": {"price_numeric": new_price}}
    )
    return result.modified_count


def delete_product(collection, name):
    """DELETE: remove a document by name."""
    result = collection.delete_one({"name": name})
    return result.deleted_count


def add_numeric_price_field(collection):
    """Helper: parse the scraped 'price' string into a numeric field for querying."""
    for doc in collection.find():
        price_str = doc.get("price", "")
        cleaned = price_str.replace("£", "").replace(",", "").strip()
        try:
            price_numeric = float(cleaned)
        except ValueError:
            price_numeric = None

        collection.update_one(
            {"_id": doc["_id"]},
            {"$set": {"price_numeric": price_numeric}}
        )


def aggregate_price_stats(collection):
    """Aggregation pipeline: average, min, and max price across all products."""
    pipeline = [
        {"$match": {"price_numeric": {"$ne": None}}},
        {"$group": {
            "_id": None,
            "avg_price": {"$avg": "$price_numeric"},
            "min_price": {"$min": "$price_numeric"},
            "max_price": {"$max": "$price_numeric"},
            "total_products": {"$sum": 1},
        }}
    ]
    return list(collection.aggregate(pipeline))


def main():
    client = get_client()
    db = client[MONGO_DB]
    collection = db["products"]

    load_scraped_products(collection)
    add_numeric_price_field(collection)

    print("\n--- CREATE: adding a new product ---")
    new_id = create_product(collection, {
        "name": "Test Product",
        "price": "£19.99",
        "price_numeric": 19.99,
        "url": "https://example.com/test-product"
    })
    print(f"Inserted new product with id: {new_id}")

    print("\n--- READ: products between £10 and £20 ---")
    for product in read_products_by_price_range(collection, 10, 20):
        print(product["name"], "-", product["price"])

    print("\n--- UPDATE: changing Test Product's price ---")
    updated_count = update_product_price(collection, "Test Product", 24.99)
    print(f"Documents updated: {updated_count}")

    print("\n--- DELETE: removing Test Product ---")
    deleted_count = delete_product(collection, "Test Product")
    print(f"Documents deleted: {deleted_count}")

    print("\n--- AGGREGATION: price statistics ---")
    stats = aggregate_price_stats(collection)
    if stats:
        print(stats[0])

    collection.create_index("name")
    print("\nIndex created on 'name' field.")

    client.close()


if __name__ == "__main__":
    main()