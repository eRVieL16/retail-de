# Databricks notebook source
# MAGIC %md
# MAGIC # Step 6 — Pindahkan Logic dbt dari retail-dbt
# MAGIC Roadmap ref: LEVEL MID step 6.
# MAGIC **Catatan penting:** step ini kerjanya di folder `dbt/` (file `.sql` model), BUKAN di notebook
# MAGIC Databricks — dbt-databricks jalan dari lokal/CI, bukan dari dalam notebook.
# MAGIC Notebook ini cuma untuk verifikasi hasil setelah `dbt run` dieksekusi dari lokal.
# MAGIC
# MAGIC Kerjaan sebenarnya:
# MAGIC 1. Copy struktur `staging/ intermediate/ mart/` dari `retail-dbt/models/` ke `dbt/models/` project ini
# MAGIC 2. Untuk tiap model, cek fungsi SQL yang dipakai — beberapa fungsi string/date beda nama
# MAGIC    antara adapter lama dan Spark SQL (lihat materi belajar bagian dbt-databricks)
# MAGIC 3. Update `sources.yml`: source sekarang menunjuk ke Silver table di Unity Catalog
# MAGIC    (`catalog` + `schema` sebagai key terpisah, bukan digabung)
# MAGIC 4. `dbt run` dari lokal

# COMMAND ----------

# MAGIC %md
# MAGIC ## Verifikasi hasil (dijalankan di sini setelah `dbt run` sukses dari lokal)

# COMMAND ----------

dbutils.widgets.text("catalog", "workspace", "Catalog")
dbutils.widgets.text("schema", "sales", "Schema (dbt target)")

CATALOG = dbutils.widgets.get("catalog")
SCHEMA = dbutils.widgets.get("schema")

display(spark.sql(f"SHOW TABLES IN {CATALOG}.{SCHEMA}"))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Catatan
# MAGIC - Model yang perlu penyesuaian fungsi SQL (beda dari adapter lama): `TODO`
# MAGIC - Tanggal `dbt run` pertama kali sukses tanpa error: `TODO`
