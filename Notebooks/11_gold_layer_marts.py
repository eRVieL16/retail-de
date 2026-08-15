# Databricks notebook source
# MAGIC %md
# MAGIC # Step 11 — Gold Terpisah: mart_sales_performance, mart_inventory_status
# MAGIC Roadmap ref: LEVEL MID step 11.
# MAGIC Sama seperti step 6/7: model Gold seharusnya ditulis sebagai dbt model
# MAGIC (`dbt/models/mart/mart_sales_performance.sql`, `mart_inventory_status.sql`), BUKAN
# MAGIC ditulis manual di notebook — supaya konsisten dengan testing & lineage dbt.
# MAGIC Notebook ini untuk verifikasi hasil setelah `dbt run` membuat kedua mart tersebut.

# COMMAND ----------

dbutils.widgets.text("catalog", "workspace", "Catalog")
dbutils.widgets.text("schema", "sales", "Schema (mart)")

CATALOG = dbutils.widgets.get("catalog")
SCHEMA = dbutils.widgets.get("schema")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Verifikasi mart_sales_performance

# COMMAND ----------

# display(spark.sql(f"SELECT * FROM {CATALOG}.{SCHEMA}.mart_sales_performance LIMIT 20"))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Verifikasi mart_inventory_status

# COMMAND ----------

# display(spark.sql(f"SELECT * FROM {CATALOG}.{SCHEMA}.mart_inventory_status LIMIT 20"))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Sanity check: apakah pemisahan Gold ini masuk akal?
# MAGIC Cek: apakah masing-masing mart punya konsumen yang jelas beda (mis. dashboard sales
# MAGIC vs alert inventory)? Kalau selalu di-query bareng oleh consumer yang sama, pertimbangkan
# MAGIC apakah perlu digabung — dokumentasikan alasannya di `docs/decisions/` kalau tetap dipisah.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Catatan
# MAGIC - Konsumen mart_sales_performance: `TODO`
# MAGIC - Konsumen mart_inventory_status: `TODO`
# MAGIC - Alasan dipisah (bukan 1 mart gabungan): `TODO`
