# Databricks notebook source
# MAGIC %md
# MAGIC # Bronze Ingestion — Semua Tabel
# MAGIC Roadmap ref: LEVEL MID step 3.
# MAGIC Satu notebook untuk semua tabel Bronze — polanya seragam (baca CSV dengan schema
# MAGIC eksplisit, tambah metadata `_ingested_at`/`_source_file`, tulis Delta), jadi cukup
# MAGIC 1 file dengan section per tabel, bukan file terpisah per tabel.
# MAGIC
# MAGIC **Pelajaran penting dari proses sebelumnya (jangan diulang):**
# MAGIC 1. Urutan `StructField` HARUS persis sama dengan urutan kolom fisik CSV —
# MAGIC    `header=True` cuma skip baris pertama, bukan matching by name.
# MAGIC 2. Cek dulu urutan kolom asli sebelum susun schema: `spark.read.csv(path, header=True, inferSchema=False).columns`
# MAGIC 3. Pakai `_metadata.file_path`, BUKAN `input_file_name()` — sudah deprecated di compute Unity Catalog.
# MAGIC 4. Kalau tipe kolom sumber desimal (mis. `"2.0"`), jangan pakai `IntegerType()` — silent fail jadi null.

# COMMAND ----------

from pyspark.sql import functions as F
from pyspark.sql.types import (
    StructType, StructField, StringType, IntegerType, DoubleType, DateType
)

dbutils.widgets.text("catalog", "de_project", "Catalog")
dbutils.widgets.text("landing_schema", "default", "Schema (landing volume)")
dbutils.widgets.text("volume", "raw", "Volume name")
dbutils.widgets.text("bronze_schema", "bronze", "Schema (bronze)")

CATALOG = dbutils.widgets.get("catalog")
LANDING_SCHEMA = dbutils.widgets.get("landing_schema")
VOLUME = dbutils.widgets.get("volume")
BRONZE_SCHEMA = dbutils.widgets.get("bronze_schema")

VOLUME_PATH = f"/Volumes/{CATALOG}/{LANDING_SCHEMA}/{VOLUME}"
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{BRONZE_SCHEMA}")

# COMMAND ----------

def ingest_bronze(file_name: str, schema: StructType, table_name: str) -> None:
    """
    Pola generik ingestion Bronze: baca CSV dengan schema eksplisit, tambah
    metadata ingestion, tulis sebagai Delta table. Dipakai untuk semua tabel
    di bawah — bukan berarti prosesnya identik makna bisnisnya, tapi mekanisme
    ingestion Bronze memang seharusnya seragam per desain medallion architecture.
    """
    df = spark.read.csv(f"{VOLUME_PATH}/{file_name}", header=True, schema=schema)

    df_bronze = (
        df.withColumn("_ingested_at", F.current_timestamp())
          .withColumn("_source_file", F.col("_metadata.file_path"))
    )

    df_bronze.write.format("delta").mode("overwrite") \
        .saveAsTable(f"{CATALOG}.{BRONZE_SCHEMA}.{table_name}")

    src_count = df.count()
    bronze_count = spark.table(f"{CATALOG}.{BRONZE_SCHEMA}.{table_name}").count()
    status = "OK" if src_count == bronze_count else "MISMATCH -- CEK ULANG"
    print(f"[{table_name}] source={src_count} bronze={bronze_count} [{status}]")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. `products`

# COMMAND ----------

products_schema = StructType([
    StructField("product_id", IntegerType(), False),
    StructField("product_name", StringType(), True),
    StructField("category", StringType(), True),
    StructField("price", DoubleType(), True),
])

ingest_bronze("products.csv", products_schema, "products")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. `transactions`
# MAGIC Urutan kolom fisik (dikonfirmasi dari CSV asli): transaction_id, store_id,
# MAGIC product_id, transaction_date, quantity, unit_price, total_amount, payment_method.
# MAGIC `quantity` pakai DoubleType karena sumbernya desimal ("2.0"), bukan integer bersih.

# COMMAND ----------

transactions_schema = StructType([
    StructField("transaction_id", IntegerType(), False),
    StructField("store_id", IntegerType(), True),
    StructField("product_id", IntegerType(), True),
    StructField("transaction_date", DateType(), True),
    StructField("quantity", DoubleType(), True),
    StructField("unit_price", DoubleType(), True),
    StructField("total_amount", DoubleType(), True),
    StructField("payment_method", StringType(), True),
])

ingest_bronze("transactions.csv", transactions_schema, "transactions")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. `stores`

# COMMAND ----------

stores_schema = StructType([
    StructField("store_id", IntegerType(), False),
    StructField("store_name", StringType(), True),
    StructField("city", StringType(), True),
    StructField("region", StringType(), True),
    StructField("store_type", StringType(), True),
    StructField("opened_date", DateType(), True),
])

ingest_bronze("stores.csv", stores_schema, "stores")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. `inventory`

# COMMAND ----------

inventory_schema = StructType([
    StructField("store_id", IntegerType(), False),
    StructField("product_id", IntegerType(), False),
    StructField("snapshot_date", DateType(), True),
    StructField("stock_qty", IntegerType(), True),
    StructField("reorder_point", IntegerType(), True),
    StructField("last_restock_date", DateType(), True),
])

ingest_bronze("inventory.csv", inventory_schema, "inventory")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Ringkasan
# MAGIC | Tabel | Row Count | Catatan |
# MAGIC |---|---|---|
# MAGIC | products | 200 | |
# MAGIC | transactions | 61142 | |
# MAGIC | stores | 30 | |
# MAGIC | inventory | 366750 | |
# MAGIC
# MAGIC Semua status harus `[OK]` di output cell masing-masing di atas sebelum lanjut ke Silver.
