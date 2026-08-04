# Databricks notebook source
# MAGIC %md
# MAGIC # Silver Cleaning — Semua Tabel
# MAGIC Roadmap ref: LEVEL MID step 4.
# MAGIC Satu notebook, section per tabel — karena tiap tabel punya keputusan cleaning
# MAGIC yang BEDA (bukan pola generik seperti Bronze), tiap section di sini punya
# MAGIC fungsi cleaning sendiri dan link ke `docs/decisions/` masing-masing.
# MAGIC
# MAGIC Prinsip yang dipegang konsisten di semua tabel:
# MAGIC - Setiap keputusan (drop/impute/flag) harus ada dasarnya, bukan tebakan
# MAGIC - Verifikasi row count sebelum-sesudah tiap kali
# MAGIC - Kalau ragu antara drop vs flag vs impute, pertimbangkan: apakah nilainya
# MAGIC   bisa diverifikasi dari kolom lain? Kalau bisa -> impute. Kalau tidak ada
# MAGIC   cara verifikasi tapi baris masih berguna untuk join -> flag. Kalau tidak
# MAGIC   ada dasar sama sekali -> drop.

# COMMAND ----------

from pyspark.sql import functions as F

dbutils.widgets.text("catalog", "de_project", "Catalog")
dbutils.widgets.text("bronze_schema", "bronze", "Schema (bronze)")
dbutils.widgets.text("silver_schema", "silver", "Schema (silver)")

CATALOG = dbutils.widgets.get("catalog")
BRONZE_SCHEMA = dbutils.widgets.get("bronze_schema")
SILVER_SCHEMA = dbutils.widgets.get("silver_schema")

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{SILVER_SCHEMA}")

# COMMAND ----------

def write_silver(df, table_name: str, bronze_count: int) -> None:
    """Tulis ke Silver + cetak ringkasan row count untuk verifikasi cepat."""
    df.write.format("delta").mode("overwrite") \
        .option("overwriteSchema", "true") \
        .saveAsTable(f"{CATALOG}.{SILVER_SCHEMA}.{table_name}")

    silver_count = spark.table(f"{CATALOG}.{SILVER_SCHEMA}.{table_name}").count()
    print(f"[{table_name}] bronze={bronze_count} silver={silver_count} diff={bronze_count - silver_count}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. `products` -> `stg_products`
# MAGIC **Keputusan:** drop null price (tidak ada dasar verifikasi) + flag negative price
# MAGIC (magnitude wajar, kemungkinan salah input tanda, tapi tidak ada kolom lain untuk
# MAGIC memverifikasi -- lihat `docs/decisions/silver_products_negative_price.md`)

# COMMAND ----------

def dedup_products(df):
    return df.dropDuplicates(["product_id"])

def drop_null_price(df):
    return df.filter(F.col("price").isNotNull())

def clean_category_text(df):
    return df.withColumn("category", F.trim(F.initcap(F.col("category"))))

def flag_negative_price(df):
    return df.withColumn("is_price_suspect", F.col("price") < 0)

bronze_products = spark.table(f"{CATALOG}.{BRONZE_SCHEMA}.products")
bronze_products_count = bronze_products.count()

silver_products = (
    bronze_products
    .transform(dedup_products)
    .transform(drop_null_price)
    .transform(clean_category_text)
    .transform(flag_negative_price)
)

write_silver(silver_products, "stg_products", bronze_products_count)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. `transactions` -> `stg_transactions`
# MAGIC **Keputusan:** dedup duplikat murni (baris identik 100%) + impute quantity null
# MAGIC via `total_amount / unit_price` (terverifikasi selalu bilangan bulat bersih di
# MAGIC 611 baris -- lihat `docs/decisions/silver_transactions_quantity_imputation.md`)

# COMMAND ----------

def dedup_transactions(df):
    return df.dropDuplicates(["transaction_id"])

def impute_missing_quantity(df):
    return df.withColumn(
        "quantity",
        F.when(F.col("quantity").isNull(),
               F.round(F.col("total_amount") / F.col("unit_price")))
         .otherwise(F.col("quantity"))
    )

bronze_transactions = spark.table(f"{CATALOG}.{BRONZE_SCHEMA}.transactions")
bronze_transactions_count = bronze_transactions.count()

silver_transactions = (
    bronze_transactions
    .transform(dedup_transactions)
    .transform(impute_missing_quantity)
)

write_silver(silver_transactions, "stg_transactions", bronze_transactions_count)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. `stores` -> `stg_stores`
# MAGIC **Keputusan:** flag + isi placeholder "Unknown" untuk store_name null (store_id
# MAGIC tetap valid untuk join, drop terlalu mahal untuk cuma 30 baris total --
# MAGIC lihat `docs/decisions/silver_stores_name_missing.md`). Tidak ada dedup --
# MAGIC EDA sudah konfirmasi 0 duplikat store_id.

# COMMAND ----------

def flag_and_fill_missing_name(df):
    return df.withColumn(
        "is_name_missing", F.col("store_name").isNull()
    ).withColumn(
        "store_name", F.coalesce(F.col("store_name"), F.lit("Unknown"))
    )

bronze_stores = spark.table(f"{CATALOG}.{BRONZE_SCHEMA}.stores")
bronze_stores_count = bronze_stores.count()

silver_stores = bronze_stores.transform(flag_and_fill_missing_name)

write_silver(silver_stores, "stg_stores", bronze_stores_count)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. `inventory` -> `stg_inventory`
# MAGIC **Keputusan:** flag backorder anomaly berdasarkan ATURAN LOGIS
# MAGIC (`last_restock_date > snapshot_date`), bukan threshold `stock_qty < 0` --
# MAGIC aturan logis menangkap akar masalah, lebih robust untuk kasus lain di masa
# MAGIC depan yang mungkin juga menghasilkan stock negatif dengan sebab berbeda
# MAGIC (lihat `docs/decisions/silver_inventory_backorder_anomaly.md`). Tidak ada
# MAGIC dedup -- EDA sudah konfirmasi 0 duplikat composite key.

# COMMAND ----------

def flag_backorder_anomaly(df):
    return df.withColumn(
        "is_backorder_anomaly",
        F.col("last_restock_date") > F.col("snapshot_date")
    )

bronze_inventory = spark.table(f"{CATALOG}.{BRONZE_SCHEMA}.inventory")
bronze_inventory_count = bronze_inventory.count()

silver_inventory = bronze_inventory.transform(flag_backorder_anomaly)

write_silver(silver_inventory, "stg_inventory", bronze_inventory_count)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Ringkasan akhir

# COMMAND ----------

for tbl in ["stg_products", "stg_transactions", "stg_stores", "stg_inventory"]:
    cnt = spark.table(f"{CATALOG}.{SILVER_SCHEMA}.{tbl}").count()
    print(f"{tbl}: {cnt} baris")
