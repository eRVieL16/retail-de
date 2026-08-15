# Databricks notebook source
# MAGIC %md
# MAGIC # Step 7 — dbt Tests: not_null, unique, relationships
# MAGIC Roadmap ref: LEVEL MID step 7.
# MAGIC Sama seperti step 6, kerjaan sebenarnya ada di `dbt/models/**/*.yml` (schema tests),
# MAGIC dieksekusi lewat `dbt test` dari lokal. Notebook ini untuk investigasi manual kalau
# MAGIC ada test yang gagal dan perlu dicek datanya langsung.

# COMMAND ----------

dbutils.widgets.text("catalog", "workspace", "Catalog")
dbutils.widgets.text("schema", "sales", "Schema")
dbutils.widgets.text("table", "stg_sales", "Table to investigate")

CATALOG = dbutils.widgets.get("catalog")
SCHEMA = dbutils.widgets.get("schema")
TABLE = dbutils.widgets.get("table")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Investigasi manual kalau test gagal
# MAGIC Pola umum: `dbt test` gagal -> lihat nama test yang gagal di output CLI -> tulis ulang
# MAGIC query-nya di sini untuk lihat baris yang bermasalah.

# COMMAND ----------

def find_null_violations(catalog: str, schema: str, table: str, column: str):
    """Cek baris yang null padahal seharusnya not_null — untuk debug test yang gagal."""
    raise NotImplementedError(
        f"TODO: return spark.sql(f'SELECT * FROM {{catalog}}.{{schema}}.{{table}} "
        f"WHERE {{column}} IS NULL')"
    )

# COMMAND ----------

def find_duplicate_keys(catalog: str, schema: str, table: str, key_column: str):
    """Cek baris duplikat berdasarkan kolom yang seharusnya unique."""
    raise NotImplementedError(
        "TODO: group by key_column, having count(*) > 1"
    )

# COMMAND ----------

# MAGIC %md
# MAGIC ## Ringkasan test (isi setelah `dbt test` jalan dari lokal)
# MAGIC | Model | Test | Status | Catatan |
# MAGIC |---|---|---|---|
# MAGIC | TODO | not_null | TODO | |
# MAGIC | TODO | unique | TODO | |
# MAGIC | TODO | relationships | TODO | |
