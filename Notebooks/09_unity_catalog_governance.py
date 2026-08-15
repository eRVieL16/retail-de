# Databricks notebook source
# MAGIC %md
# MAGIC # Step 9 — Unity Catalog: 2 Schema (sales, inventory) + Grant
# MAGIC Roadmap ref: LEVEL MID step 9.
# MAGIC Governance dasar — latihan konsep walau baru 1 orang yang pakai. Ini dijalankan
# MAGIC lewat SQL di SQL Warehouse (bisa dari notebook ini dengan `%sql`, atau langsung SQL editor).

# COMMAND ----------

dbutils.widgets.text("catalog", "workspace", "Catalog")
CATALOG = dbutils.widgets.get("catalog")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Buat 2 schema

# COMMAND ----------

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.sales")
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.inventory")
display(spark.sql(f"SHOW SCHEMAS IN {CATALOG}"))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Grant sederhana per schema
# MAGIC Untuk project solo, principal yang di-grant bisa berupa akun kamu sendiri (demo konsep)
# MAGIC atau group dummy — yang penting statement-nya benar dan didokumentasikan alasannya.

# COMMAND ----------

def grant_schema_access(catalog: str, schema: str, principal: str, privilege: str = "SELECT") -> None:
    """
    Grant privilege ke principal pada schema tertentu.
    privilege umum: SELECT, USE SCHEMA, MODIFY.
    """
    raise NotImplementedError(
        f"TODO: spark.sql(f'GRANT {{privilege}} ON SCHEMA {{catalog}}.{{schema}} TO `{{principal}}`')"
    )

# COMMAND ----------

# MAGIC %md
# MAGIC ## Verifikasi grant

# COMMAND ----------

# display(spark.sql(f"SHOW GRANTS ON SCHEMA {CATALOG}.sales"))
# display(spark.sql(f"SHOW GRANTS ON SCHEMA {CATALOG}.inventory"))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Catatan
# MAGIC Ingat: testing grant dengan akun owner/admin selalu terlihat berhasil (owner selalu
# MAGIC punya akses penuh). Untuk skala solo project, cukup dokumentasikan grant statement-nya
# MAGIC di sini dan jelaskan alasan pembagian schema-nya di `docs/decisions/`.
# MAGIC
# MAGIC - Principal yang di-grant dan alasannya: `TODO`
# MAGIC - Privilege yang diberikan per schema: `TODO`
