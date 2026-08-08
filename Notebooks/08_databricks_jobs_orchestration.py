# Databricks notebook source
# MAGIC %md
# MAGIC # Step 8 — Databricks Jobs: Bronze -> Silver -> dbt run -> dbt test
# MAGIC Roadmap ref: LEVEL MID step 8.
# MAGIC Job dikonfigurasi lewat UI (**Workflows > Jobs**) atau JSON, bukan ditulis sebagai satu
# MAGIC notebook besar. Notebook ini adalah **task 1 dan 2** dari job (Bronze, Silver) yang
# MAGIC dipanggil terpisah sebagai notebook task; task dbt run/test pakai task type "dbt" bawaan Jobs UI.
# MAGIC
# MAGIC Struktur job yang dituju:
# MAGIC ```
# MAGIC [task: bronze_ingestion]  (notebook 03)
# MAGIC         |
# MAGIC         v
# MAGIC [task: silver_cleaning]   (notebook 04)
# MAGIC         |
# MAGIC         v
# MAGIC [task: dbt_run]           (task type: dbt)
# MAGIC         |
# MAGIC         v
# MAGIC [task: dbt_test]          (task type: dbt)
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ## Checklist setup Job
# MAGIC - [ ] Buat Job baru di **Workflows > Jobs > Create Job**
# MAGIC - [ ] Task 1: notebook `03_bronze_ingestion`, set widget params sesuai kebutuhan
# MAGIC - [ ] Task 2: notebook `04_silver_cleaning`, **depends on** task 1
# MAGIC - [ ] Task 3: dbt task (`dbt run`), **depends on** task 2
# MAGIC - [ ] Task 4: dbt task (`dbt test`), **depends on** task 3
# MAGIC - [ ] Cek diagram DAG di UI sebelum run pertama — pastikan urutan dependency benar,
# MAGIC       bukan cuma urutan bikin task (lihat catatan kesalahan umum di materi belajar)
# MAGIC - [ ] Run manual sekali (Run now) untuk validasi sebelum bikin schedule

# COMMAND ----------

# MAGIC %md
# MAGIC ## Export konfigurasi Job (untuk didokumentasikan / versioning)
# MAGIC Setelah job jadi, export JSON-nya lewat UI (**Job details > ... > Edit as JSON**),
# MAGIC simpan sebagai `jobs/mid_pipeline_job.json` di repo — supaya konfigurasi job juga
# MAGIC ter-versioning, bukan cuma hidup di UI.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Catatan
# MAGIC - Job ID: `TODO`
# MAGIC - Runtime total (Bronze->Silver->dbt run->dbt test): `TODO`
# MAGIC - Tanggal run pertama sukses: `TODO`
