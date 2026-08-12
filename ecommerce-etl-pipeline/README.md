# 🛍️ E-commerce ETL Pipeline

An Apache Airflow pipeline that scrapes product data from a live e-commerce store, cleans and validates it, and loads it into PostgreSQL — built end-to-end with idempotency, retry handling, and scraping etiquette baked in.

**TMC GenAI Internship — Data Engineering Module**

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Airflow](https://img.shields.io/badge/Airflow-2.10.4-017CEE)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13-336791)

---

## 📋 Overview

This pipeline automates product data collection to support catalog and pricing analysis. It runs as a 4-task Airflow DAG:

```
create_tables_task → extract_task → transform_task → load_task
```

| Task | Purpose |
|---|---|
| `create_tables_task` | Creates the target schema if it doesn't already exist |
| `extract_task` | Scrapes listing + product detail pages |
| `transform_task` | Cleans text, parses prices/stock, handles missing data |
| `load_task` | Upserts cleaned records into Postgres (idempotent) |

---

## 🎯 Target site

**[scrapeme.live](https://scrapeme.live/shop/)** — a public WooCommerce demo store built specifically for scraping practice.

### Why this site, and not the more obvious choice

I initially targeted `demo.opencart.com`, a real OpenCart e-commerce demo, since it more literally matches "e-commerce platform" from the brief. I dropped it after checking its `robots.txt`, which **disallows automated access** — scraping it would violate the assignment's own etiquette requirement. `scrapeme.live` explicitly permits scraping, is widely used in the industry for scraping tutorials, and still has real e-commerce mechanics: SKUs, live stock counts, categories, and an add-to-cart flow.

**Trade-off:** its products don't have size/color variant options. The schema (`product_variants` table) is built to support them regardless — it simply stays empty here, which is itself a demonstration of graceful handling of missing data rather than a pipeline defect.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│              Docker Compose Stack             │
│                                                 │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐ │
│  │  Airflow  │  │  Airflow  │  │  Airflow  │ │
│  │ Webserver │  │ Scheduler │  │  Worker   │ │
│  │  :8081    │  │           │  │           │ │
│  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘ │
│        └──────────────┼──────────────┘        │
│                        │                        │
│         ┌──────────────┼──────────────┐        │
│         ▼              ▼              ▼        │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐ │
│  │  Postgres │  │   Redis   │  │  Postgres │ │
│  │ (Airflow  │  │  (Celery  │  │  -target  │ │
│  │ metadata) │  │  broker)  │  │  :5433    │ │
│  └───────────┘  └───────────┘  └─────┬─────┘ │
└──────────────────────────────────────┼─────────┘
                                        ▼
                                 scraped product
                                     data
```

Two independent Postgres instances by design: one is Airflow's internal bookkeeping (task state, DAG history), the other — `postgres-target` — is purely for scraped product data. Mixing the two is bad practice; keeping them apart also means the product database can be inspected, backed up, or reset without touching Airflow's own state.

Runs on **port 8081** (not 8080) so it doesn't conflict with the separate `airflow-hello-world` verification project in this same repo — both can run simultaneously.

---

## 📁 Project structure

```
ecommerce-etl-pipeline/
├── dags/
│   └── ecommerce_etl_dag.py      # DAG definition — orchestration only
├── scripts/
│   ├── extract.py                 # Scraping logic (requests + BeautifulSoup)
│   ├── transform.py               # Cleaning, price/stock parsing
│   └── load.py                    # Postgres upsert logic
├── sql/
│   └── create_tables.sql          # Schema: products, product_variants
├── tests/
│   └── test_transform.py          # Unit tests for transform logic
├── Dockerfile                     # Extends apache/airflow with scraping deps
├── docker-compose.yaml            # Full stack: Airflow + 2x Postgres + Redis
├── requirements.txt                # beautifulsoup4, requests, psycopg2-binary
├── .env.example
└── README.md
```

---

## 🔧 Tech stack

| Layer | Choice | Why |
|---|---|---|
| Orchestration | Apache Airflow 2.10.4 | Required by assignment; CeleryExecutor via Docker Compose |
| Scraping | `requests` + `BeautifulSoup4` | Static HTML site, no JS rendering needed |
| Storage | PostgreSQL 13 | JSONB support, `ON CONFLICT` upserts, industry-standard for structured product data |
| Containerization | Docker Compose | Reproducible across machines, avoids Apple Silicon dependency issues |

---

## 🚀 Setup & run

**Prerequisites:** Docker Desktop installed and running, ~4GB RAM available.

```bash
# 1. Copy environment template
cp .env.example .env

# 2. Build the custom image (installs scraping/DB dependencies)
docker compose build

# 3. Initialize Airflow (creates metadata DB + admin user)
docker compose up airflow-init

# 4. Start all services
docker compose up -d
docker compose ps    # confirm all 7 containers show "healthy"
```

Open **http://localhost:8081** — login `airflow` / `airflow` — unpause `ecommerce_etl_dag`, and trigger it manually. A full run takes **~8–10 minutes**, dominated by intentional scraping delays (see [Etiquette](#-scraping-etiquette) below).

---

## 🔍 Pipeline phases in detail

### 1. Extract (`scripts/extract.py`)

- Walks paginated listing pages (`MAX_PAGES = 5` by default → ~80 products out of 755 total; change this one variable to scrape more)
- Collects each product's detail-page URL, then visits it individually
- Pulls: title, description, price, image URL, stock text, SKU, category
- Every request goes through `_get_with_retries()` — 3 attempts with exponential backoff (1s → 2s → 4s) before giving up
- Raw results are passed to the next task via **XCom** (Airflow's inter-task data-passing mechanism)

### 2. Transform (`scripts/transform.py`)

- `clean_text()` — collapses whitespace, converts empty strings to `NULL`
- `parse_price()` — extracts numeric price(s) from strings like `£63.00`. Handles the WooCommerce sale-price pattern (`£100.00£75.00` → original + current) if a product is ever on sale
- `parse_stock()` — converts `"45 in stock"` → `(45, True)`, `"Out of stock"` → `(0, False)`, unrecognized text → `(None, None)` rather than crashing
- Products missing an SKU or title are dropped (unrecoverable); everything else degrades gracefully to `NULL`

### 3. Load (`scripts/load.py`)

- Upserts each product with `INSERT ... ON CONFLICT (sku) DO UPDATE`
- Entire batch runs inside a single transaction — one bad row rolls back the whole load rather than leaving partial data
- Connection details read from environment variables set in `docker-compose.yaml`, not hardcoded

---

## 🗄️ Data model

```sql
products
├── sku (unique)          ├── image_url
├── title                 ├── stock_quantity
├── description           ├── in_stock
├── product_url           ├── category
├── price_current          ├── scraped_at
├── price_original         └── updated_at

product_variants            (empty for this site — see note above)
├── product_sku (FK)
├── variant_type
├── variant_value
└── variant_stock
```

---

## ✅ Verified behaviors (not just claimed)

| Requirement | How it was tested |
|---|---|
| **Idempotency** | Ran the DAG twice on the same data. Row count stayed at **80 both times** — confirmed via SQL, not assumed. |
| **Retry on failure** | Deliberately stopped `postgres-target` mid-run. Airflow retried `create_tables_task` **3 times total** (1 original + 2 configured retries), each failing with the same clear connection error, exactly matching `retries: 2` in `default_args`. |
| **Sale-price parsing** | scrapeme.live has no products currently on sale, so this branch can't be proven against a live scrape. Verified instead with a unit test feeding synthetic "glued" price strings — see [Testing](#-testing). |
| **Graceful missing-data handling** | Confirmed via unit tests for `None`/empty/unparseable inputs across price, stock, and text cleaning. |

---

## 🧪 Testing

```bash
python3 tests/test_transform.py
```

10 unit tests covering:
- Single price vs. sale price (original + current) parsing
- Missing/unparseable price and stock text
- Text cleaning (whitespace, `None`, empty strings)

No `pytest` dependency required — runs with plain Python 3.

---

## ⚠️ Edge cases handled

- **Missing product fields** → stored as `NULL`, never crashes the pipeline
- **Out-of-stock products** → `stock_quantity = 0`, `in_stock = false`, still loaded (not skipped)
- **Unparseable stock text** → logged as a warning, quantity stored as `NULL` rather than guessing
- **Network failures during scraping** → retried 3x with exponential backoff before failing that request
- **Task-level failures** (e.g. DB unreachable) → Airflow retries the whole task 2x with a 2-minute delay
- **Re-running the DAG** → updates existing rows via SKU match, never duplicates

---

## 🌐 Scraping etiquette

- Randomized 1–3 second delay between every request (listing pages and product pages alike)
- Descriptive `User-Agent` header, not a bare script default
- Retry with exponential backoff instead of hammering on failure
- Scoped to 5 pages by default rather than the full 755-product catalog on every run

---

## 📚 Learning concepts applied

- **DAG design** — thin orchestration layer (`dags/`) vs. reusable logic (`scripts/`), the pattern used in real production Airflow projects
- **XCom** — passing data between isolated task processes without a shared filesystem
- **Idempotent upserts** — `ON CONFLICT DO UPDATE` as the standard pattern for safely re-running pipelines
- **Retry/backoff strategy** at two levels: within a single task (`_get_with_retries`) and at the Airflow task level (`default_args`)
- **Separation of concerns** — Airflow's own metadata DB vs. the application's target DB, never mixed
- **Containerized reproducibility** — anyone cloning this repo gets an identical environment via Docker, regardless of host OS

---

## 💡 What I'd improve with more time

- Add a `dbt`-style data quality check task after `load_task` (e.g. flag any product with `price_current IS NULL`)
- Parameterize `MAX_PAGES` as an Airflow Variable instead of a hardcoded constant, so it's adjustable from the UI without a code change
- Add a `pytest`-based test suite with fixtures instead of the current standalone script, for CI integration
- Schedule the DAG (`@daily`) instead of manual-trigger-only, with a `price_history` table to track changes over time — genuinely useful for the "pricing analysis" goal in the brief
- Add Slack/email alerting on task failure via Airflow's `on_failure_callback`

---

## 🛑 Shut down

```bash
docker compose down          # stop containers, keep data
docker compose down -v       # stop containers AND wipe the database
```

---

## 👤 Author

Muhammad Bin Ismail — TMC GenAI Internship, Data Engineering Track
