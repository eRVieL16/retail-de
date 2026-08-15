# Databricks notebook source
# MAGIC %md
# MAGIC # Step 1 — Workspace Setup & Verifikasi
# MAGIC Roadmap ref: LEVEL MID step 1.
# MAGIC Notebook ini bukan buat proses data — cuma checklist verifikasi bahwa workspace
# MAGIC sudah siap dipakai sebelum lanjut ke step 2 (upload data).
# MAGIC
# MAGIC Update `PROGRESS.md` baris #1 setelah semua cell di bawah lolos.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Checklist manual (dicek di UI, bukan lewat notebook)
# MAGIC - [ ] Sudah daftar Databricks Free Edition, workspace aktif
# MAGIC - [ ] Login berhasil, masuk ke halaman workspace utama
# MAGIC - [ ] Menu **Catalog** muncul di sidebar kiri (tanda Unity Catalog aktif)
# MAGIC - [ ] Ada minimal 1 SQL Warehouse tersedia (cek menu **SQL Warehouses**)
# MAGIC - [ ] Personal Access Token sudah dibuat (**Settings > Developer > Access tokens**)
# MAGIC - [ ] Token disimpan di `.env` lokal (bukan di-commit ke git)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Verifikasi terprogram
# MAGIC Jalankan cell di bawah di dalam workspace Databricks (bukan lokal) — ini konfirmasi
# MAGIC bahwa notebook attached ke compute yang benar dan Unity Catalog aktif.

# COMMAND ----------

# Cek catalog yang tersedia — kalau ini gagal / kosong, Unity Catalog belum siap
catalogs_df = spark.sql("SHOW CATALOGS")
display(catalogs_df)

# COMMAND ----------

# Cek schema di catalog default (ganti sesuai nama catalog yang mau dipakai project ini)
CATALOG_NAME = "workspace"  # TODO: sesuaikan kalau catalog default beda

spark.sql(f"USE CATALOG {CATALOG_NAME}")
display(spark.sql("SHOW SCHEMAS"))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Catatan
# MAGIC Isi manual setelah selesai:
# MAGIC - Nama catalog yang dipakai project ini: `TODO`
# MAGIC - Nama SQL Warehouse yang aktif: `TODO`
# MAGIC - Tanggal workspace siap: `TODO`
