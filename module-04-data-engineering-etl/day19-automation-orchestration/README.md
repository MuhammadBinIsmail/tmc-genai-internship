# Day 19 · Automation & Orchestration + Module 4 Review

**🎯 Objective:** Run pipelines automatically on a schedule.

## Scheduling Approach

This ETL pipeline (built Day 18) is orchestrated with **Apache Airflow**, running in
the same Dockerized environment set up earlier in the internship (`airflow-hello-world/`).
Airflow was chosen over a simpler `cron` job or Python `schedule` library because it
gives task-level retries, dependency management (extract → transform → load), and a
UI for monitoring runs — closer to how this would actually run in production.

*(For a lighter-weight alternative without Airflow, the same pipeline could be
scheduled with `cron` — e.g. `0 2 * * * /path/to/venv/bin/python etl_pipeline.py` —
or Python's `schedule` library for an always-running script. Airflow was used here
since the infrastructure was already in place from the Module 4 ETL project.)*

## DAG Structure

`scheduled_etl_pipeline` runs daily (`@daily`) with three tasks: