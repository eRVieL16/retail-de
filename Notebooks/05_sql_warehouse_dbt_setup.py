# Databricks notebook source
# MAGIC %md
# MAGIC # Step 5 — Aktifkan SQL Warehouse + Pasang dbt-databricks
# MAGIC Roadmap ref: LEVEL MID step 5.
# MAGIC Bagian ini kerjanya lebih banyak di **luar notebook** (lokal: `profiles.yml`, `.env`,
# MAGIC `test_connection.py` yang sudah dibuat sebelumnya). Notebook ini isinya checklist +
# MAGIC verifikasi ringan yang bisa dicek dari sisi Databricks.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Checklist (dikerjakan di luar notebook)
# MAGIC - [ ] SQL Warehouse 2X-Small aktif (cek status **Running** di UI)
# MAGIC - [ ] Catat `http_path` dari **SQL Warehouses > [nama] > Connection details**
# MAGIC - [ ] `.env` lokal terisi: `DBT_DATABRICKS_HOST`, `DBT_DATABRICKS_HTTP_PATH`, `DBT_DATABRICKS_TOKEN`
# MAGIC - [ ] `python test_connection.py` di lokal sukses (row `check_val = 2`)
# MAGIC - [ ] `pip install dbt-databricks` sukses di lokal
# MAGIC - [ ] `dbt debug` di folder `dbt/` project ini sukses (semua check hijau)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Verifikasi dari sisi Databricks
# MAGIC Jalankan di notebook ini (bukan lokal) untuk cross-check bahwa apa yang dilihat dbt
# MAGIC dari lokal sama dengan apa yang ada di workspace.

# COMMAND ----------

dbutils.widgets.text("catalog", "workspace", "Catalog")
CATALOG = dbutils.widgets.get("catalog")

display(spark.sql(f"SHOW SCHEMAS IN {CATALOG}"))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Catatan
# MAGIC - Nama warehouse yang dipakai dbt: `TODO`
# MAGIC - Catalog default yang dipakai dbt (harus sama dengan `catalog` di `profiles.yml`): `TODO`
# MAGIC - Tanggal `dbt debug` pertama kali sukses: `TODO`
