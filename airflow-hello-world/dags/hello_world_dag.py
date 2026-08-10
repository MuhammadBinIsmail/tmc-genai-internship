"""
Hello World DAG
----------------
Purpose: Verify that the local Airflow setup (Docker + docker-compose)
is working correctly end-to-end before starting the main ETL assignment.

Author: Muhammad Bin Ismail
Project: TMC GenAI Internship - Data Engineering Track
"""

from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator


def say_hello():
    """Simple task to confirm PythonOperator execution works."""
    print("Hello World! Airflow is running correctly on Docker (Mac M3).")
    return "Hello World task completed successfully."


def say_goodbye():
    """Second task to confirm task dependencies / ordering work."""
    print("Goodbye! DAG run finished.")


with DAG(
    dag_id="hello_world_dag",
    description="A simple Hello World DAG to verify Airflow setup",
    start_date=datetime(2025, 1, 1),
    schedule=None,          # Manual trigger only - no automatic schedule
    catchup=False,          # Don't backfill past runs
    tags=["setup", "hello-world", "verification"],
) as dag:

    task_hello = PythonOperator(
        task_id="say_hello",
        python_callable=say_hello,
    )

    task_goodbye = PythonOperator(
        task_id="say_goodbye",
        python_callable=say_goodbye,
    )

    # Task dependency: say_hello runs first, then say_goodbye
    task_hello >> task_goodbye
