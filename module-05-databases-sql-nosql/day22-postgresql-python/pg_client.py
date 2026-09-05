# Day 22 - PostgreSQL & Python Integration: pg_client.py

import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

PG_HOST = os.getenv("PG_HOST")
PG_PORT = os.getenv("PG_PORT")
PG_DATABASE = os.getenv("PG_DATABASE")
PG_USER = os.getenv("PG_USER")
PG_PASSWORD = os.getenv("PG_PASSWORD", "")

CONNECTION_STRING = f"postgresql+psycopg2://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DATABASE}"


def get_engine():
    return create_engine(CONNECTION_STRING)


def get_customers_by_city(engine, city):
    """Parameterized query - safe from SQL injection."""
    query = text("SELECT * FROM customers WHERE city = :city")
    return pd.read_sql(query, engine, params={"city": city})


def get_orders_above_amount(engine, min_amount):
    """Another parameterized query, using a numeric parameter."""
    query = text("SELECT * FROM orders WHERE order_total >= :min_amount ORDER BY order_total DESC")
    return pd.read_sql(query, engine, params={"min_amount": min_amount})


def get_customer_order_summary(engine):
    """Join query read directly into a DataFrame."""
    query = text("""
        SELECT c.full_name, c.city, c.tags, c.metadata,
               COUNT(o.order_id) AS order_count,
               COALESCE(SUM(o.order_total), 0) AS total_spent
        FROM customers c
        LEFT JOIN orders o ON c.customer_id = o.customer_id
        GROUP BY c.customer_id, c.full_name, c.city, c.tags, c.metadata
        ORDER BY total_spent DESC
    """)
    return pd.read_sql(query, engine)


def generate_report(engine):
    """Combine multiple queries into a simple text report."""
    summary_df = get_customer_order_summary(engine)

    print("=== Customer Order Summary Report ===\n")
    print(summary_df.to_string(index=False))

    print(f"\nTotal customers: {len(summary_df)}")
    print(f"Total revenue (all statuses): ${summary_df['total_spent'].sum():.2f}")
    print(f"Average spend per customer: ${summary_df['total_spent'].mean():.2f}")


def main():
    engine = get_engine()

    print("--- Customers in Karachi ---")
    print(get_customers_by_city(engine, "Karachi"))

    print("\n--- Orders >= $60 ---")
    print(get_orders_above_amount(engine, 60))

    print("\n--- Full Report ---")
    generate_report(engine)


if __name__ == "__main__":
    main()