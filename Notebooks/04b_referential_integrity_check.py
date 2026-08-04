# Databricks notebook source
# MAGIC %md
# MAGIC # Referential Integrity Check — Antar Silver Table
# MAGIC Dijalankan setelah semua Silver table (`stg_products`, `stg_transactions`,
# MAGIC `stg_stores`, `stg_inventory`) selesai, SEBELUM masuk ke dbt (step 5+).
# MAGIC
# MAGIC Ini bukan transformasi data — ini validasi lintas tabel, untuk memastikan
# MAGIC join di `int_store_daily_summary` (dbt, step 10) nanti tidak diam-diam
# MAGIC kehilangan baris (inner join) tanpa kamu sadari kenapa.
# MAGIC
# MAGIC **Konsep:** `left_anti` join mencari baris di tabel kiri yang TIDAK punya
# MAGIC pasangan di tabel kanan -- ini yang disebut orphan record.

# COMMAND ----------

from pyspark.sql import functions as F

dbutils.widgets.text("catalog", "de_project", "Catalog")
dbutils.widgets.text("silver_schema", "silver", "Schema (silver)")

CATALOG = dbutils.widgets.get("catalog")
SILVER_SCHEMA = dbutils.widgets.get("silver_schema")

stg_stores = spark.table(f"{CATALOG}.{SILVER_SCHEMA}.stg_stores")
stg_products = spark.table(f"{CATALOG}.{SILVER_SCHEMA}.stg_products")
stg_transactions = spark.table(f"{CATALOG}.{SILVER_SCHEMA}.stg_transactions")
stg_inventory = spark.table(f"{CATALOG}.{SILVER_SCHEMA}.stg_inventory")

# COMMAND ----------

def check_orphan(child_df, parent_df, join_key: str, child_name: str, parent_name: str):
    orphan = child_df.join(parent_df, on=join_key, how="left_anti")
    cnt = orphan.count()
    print(f"[{child_name} -> {parent_name} via {join_key}] orphan rows: {cnt}")
    return orphan

# COMMAND ----------

# MAGIC %md
# MAGIC ## transactions -> stores / products

# COMMAND ----------

orphan_store_in_tx = check_orphan(stg_transactions, stg_stores, "store_id", "transactions", "stores")
orphan_product_in_tx = check_orphan(stg_transactions, stg_products, "product_id", "transactions", "products")

# COMMAND ----------

# MAGIC %md
# MAGIC ## inventory -> stores / products

# COMMAND ----------

orphan_store_in_inv = check_orphan(stg_inventory, stg_stores, "store_id", "inventory", "stores")
orphan_product_in_inv = check_orphan(stg_inventory, stg_products, "product_id", "inventory", "products")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Interpretasi hasil
# MAGIC - Orphan di `stores` harus 0 di semua kasus -- stg_stores tidak pernah drop baris
# MAGIC   (cuma flag), jadi tidak ada alasan orphan muncul dari sisi stores.
# MAGIC - Orphan di `products` KEMUNGKINAN tidak 0 -- stg_products drop 4 baris (null
# MAGIC   price) dari 200 baris asli. Kalau ada transactions/inventory yang
# MAGIC   mereferensikan 4 product_id yang di-drop itu, orphan count > 0 di sini.
# MAGIC   Ini BUKAN bug, ini konsekuensi dari keputusan cleaning yang sudah diambil.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Kalau ada orphan dari products -- investigasi mana yang kena

# COMMAND ----------

if orphan_product_in_tx.count() > 0:
    display(orphan_product_in_tx.select("product_id").distinct())

if orphan_product_in_inv.count() > 0:
    display(orphan_product_in_inv.select("product_id").distinct())

# COMMAND ----------

# MAGIC %md
# MAGIC ## Catatan & keputusan
# MAGIC Isi setelah lihat hasil di atas:
# MAGIC - Jumlah orphan product di transactions: `TODO`
# MAGIC - Jumlah orphan product di inventory: `TODO`
# MAGIC - product_id yang di-drop dari products dan konsekuensinya: `TODO`
# MAGIC - Keputusan untuk int_store_daily_summary nanti: inner join (otomatis exclude
# MAGIC   orphan) atau left join + flag? -> `TODO`, dokumentasikan di
# MAGIC   `docs/decisions/int_store_daily_summary_join_strategy.md`
