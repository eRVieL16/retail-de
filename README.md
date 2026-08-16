# Retail Lakehouse Platform

**An end-to-end data engineering platform for multi-store retail operations**, built on
Databricks (PySpark, Delta Lake, dbt, Unity Catalog) with automated CI/CD.

![CI](https://github.com/eRVieL16/retail-de/actions/workflows/dbt-ci.yml/badge.svg)

This is a self-contained monorepo — every phase of the platform's evolution (current
foundation layer, and future streaming/governance/IaC work) lives here as it's built out,
rather than being split across separate repositories.

## Overview

Retail Lakehouse Platform simulates a multi-store retail operation (synthetic data,
20+ stores) and processes it through a full medallion architecture: raw ingestion,
cleaning with distributed processing, business-layer transformation, and orchestrated,
tested, CI-validated delivery to analytics-ready tables.

The domain — multi-store retail operations — is deliberate: it reflects real experience
working with 250+ store retail data, so the data quality issues modeled here (missing
prices, orphan foreign keys, backorder anomalies) are patterns actually seen in retail
data, not textbook-clean sample data.

*(Catatan: domain retail multi-toko dipilih karena merepresentasikan pengalaman kerja
nyata, bukan dataset contoh yang sudah bersih dari awal.)*

## Architecture

```
Faker (synthetic data generator)
        │
        ▼
Unity Catalog Volume  (landing zone)
        │
        ▼
  BRONZE  (Delta, raw + _ingested_at metadata)
        │  PySpark: dedup, type casting, referential integrity checks
        ▼
  SILVER  (Delta, cleaned + flagged anomalies — see docs/decisions/DECISIONS.md)
        │  dbt-databricks: intermediate → mart
        ▼
  GOLD    (Delta, business-ready marts)
        │  mart_sales_performance · mart_inventory_status
        ▼
  Databricks Jobs orchestrates: Bronze → Silver → dbt run → dbt test
  GitHub Actions validates every push to main: dbt build (run + test)
```

## Tech Stack

| Layer | Tools |
|---|---|
| Compute | Databricks Free Edition (serverless PySpark) |
| Storage | Delta Lake, Unity Catalog Volumes |
| Transformation | PySpark (Bronze/Silver), dbt-databricks (Silver→Gold) |
| Governance | Unity Catalog (schema-level separation: `sales`, `inventory`) |
| Orchestration | Databricks Jobs (Workflows) |
| CI/CD | GitHub Actions |
| Testing | dbt generic tests (`not_null`, `unique`, `relationships`) |
| Data generation | Python (Faker) |

## Project Structure

```
retail-lakehouse-platform/
├── Notebooks/                 # PySpark ingestion & transformation, run as Databricks notebooks
│   ├── 01_workspace_setup.py
│   ├── 02_upload_volume.py
│   ├── 03_bronze_ingestion.py
│   ├── 04_silver_cleaning.py
│   ├── 04b_referential_integrity_check.py
│   ├── 05_sql_warehouse_dbt_setup.py
│   ├── 06_dbt_migrate_logic.py
│   ├── 07_dbt_tests.py
│   ├── 08_databricks_jobs_orchestration.py
│   ├── 09_unity_catalog_governance.py
│   ├── 10_second_source_inventory.py
│   ├── 11_gold_layer_marts.py
│   ├── 12_cicd_github_actions.py
│   └── generate_inventory.py  # synthetic data generator (Faker)
├── dbt/                       # dbt-databricks project: intermediate + marts (no staging layer — see decision #6)
│   ├── dbt_project.yml
│   ├── profiles.yml
│   ├── packages.yml
│   ├── macros/
│   │   └── generate_schema_name.sql
│   └── models/
│       ├── intermediate/
│       └── marts/
│           ├── sales/
│           └── inventory/
├── scripts/
│   ├── generate_data.py       # stores, products, transactions
│   └── generate_inventory.py  # inventory (depends on stores.csv, products.csv)
├── data/
│   └── raw/                   # output CSV
├── docs/
│   └── decisions/
│       └── DECISIONS.md       # every non-trivial data/architecture decision, Context → Options → Decision → Consequence
├── .github/
│   └── workflows/
│       └── dbt-ci.yml         # CI: dbt build on every push to main
├── test_connection.py
└── PROGRESS.md                # milestone tracking (working doc, Indonesian)
```

## Data Quality — Real Decisions, Not Defaults

Every non-obvious cleaning decision is documented in
[`docs/decisions/DECISIONS.md`](docs/decisions/DECISIONS.md) using a
Context → Options → Decision → Consequence format. Highlights:

- **Missing prices**: 4 rows with null price dropped (no basis for reconstruction);
  negative prices flagged, not silently corrected, so downstream consumers decide.
- **Missing quantity**: imputed via `round(total_amount / unit_price)` — verifiable
  from existing valid columns, not guessed.
- **Backorder anomaly**: 5,501 rows where `last_restock_date > snapshot_date`
  (logically impossible) — flagged, not dropped, because the rest of the row is
  still usable.
- **Orphan foreign keys**: ~2% of transactions/inventory rows reference products
  that were dropped for missing price. Traced to root cause, then excluded via
  inner join at the intermediate layer — a documented consequence, not silent
  data loss.

## Governance

Unity Catalog schemas are split by business domain (`sales`, `inventory`) rather than
one catalog-wide schema — mirroring how access boundaries typically work in a real
organization (inventory team doesn't need access to sales financial data, and vice
versa). Role-based `GRANT`s are designed but not yet executable: Databricks Free
Edition has no Account Console access, which is required for account-level groups.
This is a platform constraint, not a skipped step — the grant SQL is ready to run
the moment this moves to a paid tier.

## CI/CD

Every push to `main` triggers `dbt build --target dev` (run + test) via GitHub
Actions, validated against the live Databricks SQL Warehouse. Current status: all
3 models build, all 10 tests pass.

## Getting Started

```bash
# 1. Set up credentials
cp .env.example .env   # fill in Databricks host, token, warehouse path

# 2. Verify connection
python test_connection.py

# 3. Generate synthetic data (stores, products, transactions, then inventory)
python scripts/generate_data.py
python scripts/generate_inventory.py
# then run Notebooks/02_upload_volume.py in Databricks

# 4. Run Bronze -> Silver (as Databricks notebooks)
# 03_bronze_ingestion.py, then 04_silver_cleaning.py

# 5. Build & test the dbt layer
cd dbt
dbt deps --profiles-dir .
dbt build --target dev --profiles-dir .
```

Orchestration (Bronze → Silver → dbt run → dbt test) is also registered as a
Databricks Job — run manually from the Workflows UI, or let CI validate the
dbt layer on every push.

## Design Rationale

*(5 poin di bawah adalah alasan di balik keputusan arsitektur besar — bukan daftar
tools, tapi urutan mikir dan trade-off yang diambil.)*

**1. Why PySpark instead of Pandas**
Pandas is fine for data that fits in memory on a single machine, but that's not
a realistic constraint for retail operations data at scale. Moving to PySpark here
is a deliberate choice to work in a paradigm built for distributed, growing data —
not just what's convenient for a small synthetic dataset.

**2. Why Unity Catalog Volume, not DBFS**
DBFS is the legacy storage layer, kept mostly for backward compatibility. Unity
Catalog Volume is the fully governed replacement — access control and audit logging
integrated at the storage layer — and it's the only option fully supported on
Databricks Free Edition. This decision is as much a platform constraint as an
architectural preference.

**3. Bronze → Silver → Gold schema design**
- **Bronze**: raw ingestion + `_ingested_at` metadata, no cleaning — an unmodified
  audit trail of what arrived.
- **Silver**: PySpark cleaning — dedup, type validation, referential integrity
  checks (see decision log for specifics).
- **Gold**: split by business consumer, not one big table — `mart_sales_performance`
  and `mart_inventory_status` each answer one clear question.

**4. Why dbt-databricks for the transformation layer**
SQL + Jinja transformation logic is portable across dbt adapters — the adapter
handles connection and SQL dialect, not the modeling approach itself. Using
dbt here keeps the transformation layer testable, documented, and consistent
with how a real analytics engineering team would structure business logic.

**5. Governance: two schemas instead of one**
Splitting `sales` and `inventory` into separate schemas — even with a single user —
practices the access-boundary pattern that matters once role-based grants are
actually enforced (see Governance section above).

## Roadmap

This repository is designed to grow in place — future phases build on the same
foundation rather than starting a new repo:

- **Phase 2 (planned)**: local Kafka + Flink streaming, sinking to Unity Catalog
  Volume, consumed by Lakeflow Declarative Pipelines into Gold.
- **Phase 2 (planned)**: parallel AWS free-tier track — S3 + Glue Data Catalog via
  Terraform, provisioned independently, documented as a future Unity Catalog
  external location integration.
- **Phase 2 (planned)**: advanced Unity Catalog governance — row-filter / column-mask
  on sensitive columns, and role-based grants once executed on a paid tier.

See `docs/decisions/` for how each phase's trade-offs get documented as they land.
