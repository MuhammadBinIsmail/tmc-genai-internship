"""
E-commerce ETL DAG - scrapes scrapeme.live, cleans the data, and loads
it into the postgres-target database.

Three tasks, run in sequence:
    create_tables_task -> extract_task -> transform_task -> load_task
"""

import os
import sys
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

# scripts/ is mounted into the container at /opt/airflow/scripts (see
# docker-compose.yaml), so it needs to be on the path to import from.
sys.path.insert(0, "/opt/airflow/scripts")

from extract import extract
from transform import transform
from load import load, get_connection


def create_tables(**context):
    """Runs sql/create_tables.sql against postgres-target. Uses
    CREATE TABLE IF NOT EXISTS, so this is safe to run on every DAG run."""
    with open("/opt/airflow/sql/create_tables.sql") as f:
        schema_sql = f.read()

    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cursor:
                cursor.execute(schema_sql)
    finally:
        conn.close()


default_args = {
    "owner": "muhammad-bin-ismail",
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
}

with DAG(
    dag_id="ecommerce_etl_dag",
    description="Scrape scrapeme.live, clean, and load into Postgres",
    default_args=default_args,
    start_date=datetime(2025, 1, 1),
    schedule=None,  # manual trigger; change to e.g. '@daily' for a schedule
    catchup=False,
    tags=["etl", "scraping", "ecommerce"],
) as dag:

    create_tables_task = PythonOperator(
        task_id="create_tables_task",
        python_callable=create_tables,
    )

    extract_task = PythonOperator(
        task_id="extract_task",
        python_callable=extract,
    )

    transform_task = PythonOperator(
        task_id="transform_task",
        python_callable=transform,
    )

    load_task = PythonOperator(
        task_id="load_task",
        python_callable=load,
    )

    create_tables_task >> extract_task >> transform_task >> load_task