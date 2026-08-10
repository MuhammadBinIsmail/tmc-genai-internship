# Airflow Hello World

A minimal Apache Airflow setup used to verify that the local Docker-based
Airflow environment is working correctly before starting the main
ETL assignment (see `../ecommerce-etl-pipeline`).

## What this proves

- Docker Desktop + `docker-compose` can run Airflow's full stack
  (webserver, scheduler, triggerer, worker, Postgres, Redis) locally.
- A custom DAG placed in `dags/` is picked up by the scheduler.
- Tasks execute successfully and task dependencies (`>>`) work as expected.

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- ~4GB RAM available for Docker

## Setup & Run

1. Copy the example env file:
```bash
   cp .env.example .env
```

2. Initialize Airflow (creates metadata DB + admin user):
```bash
   docker compose up airflow-init
```

3. Start all services:
```bash
   docker compose up -d
```

4. Check all containers are healthy:
```bash
   docker compose ps
```

5. Open the UI: [http://localhost:8080](http://localhost:8080)
   - Username: `airflow`
   - Password: `airflow`

6. In the DAGs list, find `hello_world_dag`, unpause it (toggle), then
   trigger it manually (▶️ button). Both tasks (`say_hello`, `say_goodbye`)
   should turn green.

## Shut down

```bash
docker compose down
```

To also wipe the metadata database (clean slate):
```bash
docker compose down -v
```

## DAG structure

`dags/hello_world_dag.py` — two `PythonOperator` tasks chained sequentially:
say_hello >> say_goodbye
