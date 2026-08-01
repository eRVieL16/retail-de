# Databricks notebook source
# MAGIC %md
# MAGIC # Step 2 — Upload Dataset Junior ke Unity Catalog Volume
# MAGIC Roadmap ref: LEVEL MID step 2.
# MAGIC Tujuan: pindahkan output `retail-de-junior` (CSV/Parquet hasil `clean.py`) ke Volume,
# MAGIC supaya bisa dibaca PySpark di step 3 (Bronze ingestion).
# MAGIC
# MAGIC Prasyarat: sudah tahu nama catalog & schema dari notebook 01.

# COMMAND ----------

dbutils.widgets.text("catalog", "workspace", "Catalog")
dbutils.widgets.text("schema", "sales", "Schema (landing)")
dbutils.widgets.text("volume", "landing_zone", "Volume name")

CATALOG = dbutils.widgets.get("catalog")
SCHEMA = dbutils.widgets.get("schema")
VOLUME = dbutils.widgets.get("volume")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Buat schema & volume (kalau belum ada)
# MAGIC Jalankan sekali saja — idempotent karena pakai `IF NOT EXISTS`.

# COMMAND ----------

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{SCHEMA}")
spark.sql(f"CREATE VOLUME IF NOT EXISTS {CATALOG}.{SCHEMA}.{VOLUME}")

volume_path = f"/Volumes/{CATALOG}/{SCHEMA}/{VOLUME}"
print(f"Volume path: {volume_path}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Upload file
# MAGIC Dua opsi, pilih salah satu:
# MAGIC 1. **Manual lewat UI** — buka Catalog Explorer, cari volume ini, klik Upload. Paling gampang untuk file kecil.
# MAGIC 2. **Terprogram** — kalau file sudah ada di lokasi lain yang bisa diakses notebook (mis. sudah di-copy ke DBFS workspace files sementara), pakai `dbutils.fs.cp`.

# COMMAND ----------

def upload_junior_output(local_or_staging_path: str, target_filename: str) -> str:
    """
    Copy 1 file hasil retail-de-junior ke volume ini.

    Args:
        local_or_staging_path: path sumber (workspace file, atau path yang sudah accessible dari cluster)
        target_filename: nama file tujuan di volume, mis. "sales_transaction_clean.csv"

    Returns:
        path lengkap file di volume setelah dicopy
    """
    raise NotImplementedError(
        "TODO: pakai dbutils.fs.cp(local_or_staging_path, f'{volume_path}/{target_filename}') "
        "atau upload manual lewat UI kalau path sumber tidak accessible dari cluster."
    )

# COMMAND ----------

# MAGIC %md
# MAGIC ## Verifikasi upload

# COMMAND ----------

display(dbutils.fs.ls(volume_path))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Catatan
# MAGIC - File yang diupload: `TODO` (nama file + jumlah baris untuk cross-check)
# MAGIC - Ukuran file: `TODO`
# MAGIC - Tanggal upload: `TODO`
