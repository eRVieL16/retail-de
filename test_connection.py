"""
test_connection.py
Uji koneksi langsung ke Databricks SQL Warehouse, terpisah dari dbt.
Tujuan: kalau ada error, cepat tahu apakah masalahnya di kredensial/network
(ketauan di sini) atau di config dbt (baru lanjut cek profiles.yml).

Install dulu:
    pip install databricks-sql-connector python-dotenv

Jalankan:
    python test_connection.py
"""

import os
import sys
from dotenv import load_dotenv
from databricks import sql

load_dotenv()

REQUIRED_VARS = [
    "DBT_DATABRICKS_HOST",
    "DBT_DATABRICKS_HTTP_PATH",
    "DBT_DATABRICKS_TOKEN",
]


def check_env() -> dict:
    missing = [v for v in REQUIRED_VARS if not os.getenv(v)]
    if missing:
        print(f"[FAIL] Env var belum diset: {', '.join(missing)}")
        print("       Copy .env.example -> .env, isi value asli, lalu load_dotenv().")
        sys.exit(1)
    return {v: os.getenv(v) for v in REQUIRED_VARS}


def test_connection(creds: dict) -> None:
    print(f"[INFO] Connecting to {creds['DBT_DATABRICKS_HOST']} ...")
    try:
        with sql.connect(
            server_hostname=creds["DBT_DATABRICKS_HOST"],
            http_path=creds["DBT_DATABRICKS_HTTP_PATH"],
            access_token=creds["DBT_DATABRICKS_TOKEN"],
        ) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT current_catalog(), current_schema(), 1 + 1 AS check_val")
                row = cursor.fetchone()
                print(f"[OK] Connected. catalog={row[0]} schema={row[1]} check={row[2]}")

                # Cek warehouse bisa lihat catalog/schema yang akan dipakai Bronze/Silver/Gold
                cursor.execute("SHOW CATALOGS")
                catalogs = [r[0] for r in cursor.fetchall()]
                print(f"[OK] Catalogs visible: {catalogs}")
    except Exception as e:
        print(f"[FAIL] Connection error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    creds = check_env()
    test_connection(creds)
