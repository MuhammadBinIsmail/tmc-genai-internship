# Day 19 - Automation & Orchestration

import sys
import os
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

# Makes Day 18's pipeline functions importable from this DAG
sys.path.append(os.path.join(os.path.dirname(__file__), "day18_pipeline"))

from etl_pipeline import (
    extract_products,
    extract_github_repos,
    transform_products,
    transform_repos,
    load_to_sqlite,
    CONFIG,
)

default_args = {
    "owner": "intern",
    "retries": 3,
    "retry_delay": timedelta(minutes=2),
}

def run_extract(**context):
    products = extract_products()
    repos = extract_github_repos()
    context["ti"].xcom_push(key="raw_products", value=products)
    context["ti"].xcom_push(key="raw_repos", value=repos)

def run_transform(**context):
    raw_products = context["ti"].xcom_pull(key="raw_products", task_ids="extract_task")
    raw_repos = context["ti"].xcom_pull(key="raw_repos", task_ids="extract_task")

    products_df = transform_products(raw_products)
    repos_df = transform_repos(raw_repos)

    context["ti"].xcom_push(key="products_df", value=products_df.to_json())
    context["ti"].xcom_push(key="repos_df", value=repos_df.to_json())

def run_load(**context):
    import pandas as pd

    products_json = context["ti"].xcom_pull(key="products_df", task_ids="transform_task")
    repos_json = context["ti"].xcom_pull(key="repos_df", task_ids="transform_task")

    products_df = pd.read_json(products_json)
    repos_df = pd.read_json(repos_json)

    load_to_sqlite(products_df, "products", CONFIG["db_path"])
    load_to_sqlite(repos_df, "github_repos", CONFIG["db_path"])

with DAG(
    dag_id="scheduled_etl_pipeline",
    default_args=default_args,
    description="Daily scheduled run of the Day 18 ETL pipeline",
    schedule="@daily",
    start_date=datetime(2026, 7, 6),
    catchup=False,
    tags=["etl", "module4"],
) as dag:

    extract_task = PythonOperator(
        task_id="extract_task",
        python_callable=run_extract,
    )

    transform_task = PythonOperator(
        task_id="transform_task",
        python_callable=run_transform,
    )

    load_task = PythonOperator(
        task_id="load_task",
        python_callable=run_load,
    )

    extract_task >> transform_task >> load_task