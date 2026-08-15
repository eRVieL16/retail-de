# Databricks notebook source
# MAGIC %md
# MAGIC # Step 10 — Sumber Kedua (Inventory) + int_store_daily_summary
# MAGIC Roadmap ref: LEVEL MID step 10.
# MAGIC Ulangi pola Bronze -> Silver dari notebook 03-04, tapi untuk data inventory harian.
# MAGIC Ditutup dengan 1 tabel intermediate yang menggabungkan sales + inventory per toko per hari.

# COMMAND ----------

from pyspark.sql import functions as F

dbutils.widgets.text("catalog", "workspace", "Catalog")
dbutils.widgets.text("landing_schema", "inventory", "Schema (landing volume)")
dbutils.widgets.text("volume", "landing_zone", "Volume name")
dbutils.widgets.text("bronze_schema", "bronze", "Schema (bronze)")
dbutils.widgets.text("silver_schema", "silver", "Schema (silver)")

CATALOG = dbutils.widgets.get("catalog")
LANDING_SCHEMA = dbutils.widgets.get("landing_schema")
VOLUME = dbutils.widgets.get("volume")
BRONZE_SCHEMA = dbutils.widgets.get("bronze_schema")
SILVER_SCHEMA = dbutils.widgets.get("silver_schema")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Bronze: inventory
# MAGIC Sama pola dengan notebook 03 — schema eksplisit, tambah `_ingested_at`, tulis Delta.

# COMMAND ----------

def get_inventory_schema():
    """Schema eksplisit untuk raw inventory harian per toko."""
    raise NotImplementedError("TODO: sama pola seperti get_sales_transaction_schema() di notebook 03")

# COMMAND ----------

def ingest_bronze_inventory(volume_path: str, schema) -> None:
    """Baca raw inventory dari volume, tulis sebagai bronze.inventory_daily."""
    raise NotImplementedError("TODO: sama pola seperti write_bronze_table() di notebook 03")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Silver: stg_inventory
# MAGIC Cleaning sesuai kebutuhan data inventory (bisa beda dari sales — misal validasi stock >= 0).

# COMMAND ----------

def clean_inventory(df):
    """Cleaning khusus inventory — cek validasi qty non-negatif, dedup per toko-produk-tanggal."""
    raise NotImplementedError(
        "TODO: contoh -> df.filter(F.col('stock_qty') >= 0)"
        ".dropDuplicates(['store_id', 'product_id', 'snapshot_date'])"
    )

# COMMAND ----------

# MAGIC %md
# MAGIC ## Konsolidasi: int_store_daily_summary
# MAGIC Gabungkan stg_sales + stg_inventory per toko per hari. Ini biasanya lebih pas ditulis
# MAGIC sebagai model dbt (`dbt/models/intermediate/int_store_daily_summary.sql`) daripada di
# MAGIC notebook, supaya konsisten dengan pola staging->intermediate->mart dari `retail-dbt`.
# MAGIC Bagian di bawah untuk eksplorasi/validasi logic sebelum ditulis ulang sebagai model dbt.

# COMMAND ----------

def build_store_daily_summary_preview(sales_df, inventory_df):
    """
    Preview join sales + inventory per store per day, sebelum logic-nya dipindah ke dbt model.
    Join key: store_id + tanggal.
    """
    raise NotImplementedError(
        "TODO: join sales_df dan inventory_df on ['store_id', 'date'], "
        "agregasi sesuai kebutuhan mart_sales_performance & mart_inventory_status"
    )

# COMMAND ----------

# MAGIC %md
# MAGIC ## Catatan
# MAGIC - Perbedaan validasi Silver antara sales vs inventory: `TODO`
# MAGIC - Keputusan: logic konsolidasi ditulis di notebook atau langsung dbt model? `TODO` -> link `docs/decisions/`
