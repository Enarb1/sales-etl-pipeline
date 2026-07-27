# Sales ETL Pipeline

An Apache Airflow pipeline (built with the [Astronomer](https://www.astronomer.io/) CLI) that extracts raw sales and product data from Amazon S3, cleans and validates it, merges and enriches it, and produces a set of business-facing sales aggregations — all written back to S3 as Parquet.

## Overview

The pipeline is defined in [`dags/etl_pipline.py`](dags/etl_pipline.py) as a single Airflow DAG (`etl_pipline`) that runs on a daily schedule. Each stage is an Airflow task backed by reusable Python modules under `include/`.

**Pipeline stages:**

1. **Extract** — lists all raw files (`.csv`, `.json`, `.parquet`) in the configured S3 raw-data folder and builds a map of dataset name → S3 path.
2. **Clean** — validates each dataset against an input schema, applies dataset-specific cleaning rules, validates the output, and writes cleaned Parquet files to S3.
   - `sales_north`: drops rows with missing region/timestamp or invalid price/quantity, normalizes region casing, computes `total_sales` (price × quantity).
   - `product_metadata`: normalizes brand/category casing, drops duplicate or incomplete product records.
3. **Merge** — inner-joins the cleaned sales and product datasets on `product_id`.
4. **Enrich** — adds derived time features (`month`, `week`, `weekday`, `hour`) and buckets each sale into `Low` / `Medium` / `High` based on `total_sales`.
5. **Aggregate** — computes four downstream analytics tables from the enriched dataset:
   - **Hourly sales trend** — peak sales hour per region/category.
   - **Sales/product trend** — ranks products by revenue and sales volume into `Bestseller` / `Average` / `Low Performer` buckets.
   - **Seasonal sales pattern** — quarterly sales totals by category.
   - **Revenue concentration** — each region's share of total revenue and cumulative share.

Every stage validates its input and output against schemas defined with [Pandera](https://pandera.readthedocs.io/) (see `include/validations/`), and all intermediate and final outputs are stored as Parquet files in S3.

## Project Structure

```
.
├── dags/
│   └── etl_pipline.py          # Airflow DAG definition
├── include/
│   ├── config/
│   │   ├── config.yaml         # AWS/Snowflake connection IDs, bucket, folder paths
│   │   ├── settings.py         # Loads config.yaml into importable constants
│   │   └── logger.py           # Shared logger setup
│   ├── etl/
│   │   ├── extract/            # S3 raw data discovery
│   │   └── transform/          # Cleaning, merging, enrichment, aggregations
│   ├── utils/                  # S3 hook/storage helpers, dataframe I/O helpers
│   └── validations/            # Pandera input/output schemas and validators
├── tests/
│   └── dags/                   # DAG-level tests (e.g. DAG integrity checks)
├── Dockerfile                  # Astro Runtime image
├── requirements.txt            # Python dependencies
└── packages.txt                # OS-level packages (empty by default)
```

## Requirements

- [Docker](https://www.docker.com/)
- [Astronomer CLI (`astro`)](https://www.astronomer.io/docs/astro/cli/install-cli)
- An AWS account/S3 bucket for raw and processed data
- (Optional) A Snowflake account, if you extend the pipeline to load into Snowflake — the connection is configured but not yet used in the DAG

## Configuration

Connection IDs, bucket name, and folder paths are defined in [`include/config/config.yaml`](include/config/config.yaml):

```yaml
aws:
  conn_id: aws_conn_id
  bucket_name: datawarehouse-etl-softuni
  prefix: exam_prep/
  folders:
    raw_data: raw-data/
    processed_data: processed-data/

snowflake:
  conn_id: my_snowflake_conn
  database: SALES_DB
```

Update these values to point at your own bucket/prefix, then create matching connections in Airflow (via the UI, CLI, or `airflow_settings.yaml`):

| Connection ID | Type | Used for |
|---|---|---|
| `aws_conn_id` | Amazon Web Services | Reading/writing S3 data |
| `my_snowflake_conn` | Snowflake | Reserved for future Snowflake integration |

Raw input files are expected in `s3://<bucket_name>/<prefix><raw_data>/`, named `sales_north.*` and `product_metadata.*`.

## Running Locally

1. Install the [Astronomer CLI](https://www.astronomer.io/docs/astro/cli/install-cli).
2. Set your AWS connection in `airflow_settings.yaml` (or via the Airflow UI once running) using the `aws_conn_id` value from `config.yaml`.
3. Start the local Airflow environment:

   ```bash
   astro dev start
   ```

   This spins up Postgres, Scheduler, DAG Processor, API Server, and Triggerer in Docker. Once ready, the Airflow UI opens at [http://localhost:8080](http://localhost:8080).

4. Trigger the `etl_pipline` DAG from the UI, or unpause it to let the daily schedule take over.

To stop the environment:

```bash
astro dev stop
```

## Testing

DAG-level tests live in `tests/dags/`. Run them with:

```bash
astro dev pytest
```

## Deploying

To deploy to an Astronomer Deployment:

```bash
astro deploy
```

See the [Astronomer deployment docs](https://www.astronomer.io/docs/astro/deploy-code/) for details.

## Tech Stack

- **Orchestration:** Apache Airflow (Astro Runtime, TaskFlow API)
- **Data processing:** pandas
- **Validation:** Pandera
- **Storage:** Amazon S3 (via `s3fs`, `boto3`, `apache-airflow-providers-amazon`)
- **Planned:** Snowflake loading (`apache-airflow-providers-snowflake`, `snowflake-connector-python`)