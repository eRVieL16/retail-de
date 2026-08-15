# Databricks notebook source
# MAGIC %md
# MAGIC # Step 12 — CI/CD: GitHub Actions untuk dbt build
# MAGIC Roadmap ref: LEVEL MID step 12.
# MAGIC Ini murni kerjaan di luar Databricks (`.github/workflows/dbt_build.yml` di repo).
# MAGIC Notebook ini cuma checklist + catatan, bukan tempat eksekusi.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Checklist
# MAGIC - [ ] Buat `.github/workflows/dbt_build.yml`
# MAGIC - [ ] Tambah GitHub Secrets: `DATABRICKS_HOST`, `DATABRICKS_HTTP_PATH`, `DATABRICKS_TOKEN`
# MAGIC - [ ] Workflow trigger: `on: push` ke branch tertentu, atau `pull_request` untuk validasi sebelum merge
# MAGIC - [ ] Step workflow: checkout -> setup Python -> `pip install dbt-databricks` -> `dbt build`
# MAGIC   (catatan: `dbt build` = `dbt run` + `dbt test` dalam satu command, urutannya otomatis benar per-model)
# MAGIC - [ ] Test: push commit kecil, cek Actions tab, pastikan job hijau
# MAGIC - [ ] Test negatif: sengaja rusak 1 test dbt, cek workflow gagal seperti yang diharapkan

# COMMAND ----------

# MAGIC %md
# MAGIC ## Referensi skeleton workflow (ditulis di repo, bukan di sini)
# MAGIC ```yaml
# MAGIC name: dbt build
# MAGIC on:
# MAGIC   push:
# MAGIC     branches: [main]
# MAGIC jobs:
# MAGIC   dbt-build:
# MAGIC     runs-on: ubuntu-latest
# MAGIC     env:
# MAGIC       DBT_DATABRICKS_HOST: ${{ secrets.DATABRICKS_HOST }}
# MAGIC       DBT_DATABRICKS_HTTP_PATH: ${{ secrets.DATABRICKS_HTTP_PATH }}
# MAGIC       DBT_DATABRICKS_TOKEN: ${{ secrets.DATABRICKS_TOKEN }}
# MAGIC     steps:
# MAGIC       - uses: actions/checkout@v4
# MAGIC       - uses: actions/setup-python@v5
# MAGIC         with:
# MAGIC           python-version: "3.11"
# MAGIC       - run: pip install dbt-databricks
# MAGIC       - run: cd dbt && dbt build
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ## Catatan
# MAGIC - Tanggal workflow pertama kali hijau: `TODO`
# MAGIC - Link ke run Actions sebagai bukti (screenshot untuk portofolio): `TODO`
