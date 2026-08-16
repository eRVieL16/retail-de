"""
Generate data sintetis inventory harian per toko.

Melengkapi generate_data.py yang sudah ada (stores, products, transactions) —
tabel ini belum pernah digenerate sebelumnya, jadi ditambahkan khusus untuk
kebutuhan Level Mid (roadmap step 10: sumber kedua).

Pola noise sengaja disamakan dengan generate_data.py (missing value, duplikat,
kemungkinan tipe salah) supaya EDA & cleaning di Silver ada gunanya nyata —
tapi kamu yang tentukan noise spesifik apa yang relevan untuk inventory,
karena karakteristiknya beda dari transactions/products.

PENTING: script ini harus dijalankan SETELAH stores.csv dan products.csv ada,
karena inventory butuh store_id dan product_id yang valid (referential integrity)
supaya nanti bisa di-join tanpa orphan record yang nggak disengaja.
"""

import os
import random
from datetime import datetime, timedelta

import pandas as pd
from dotenv import load_dotenv

load_dotenv()

random.seed(42)

NUM_DAYS_HISTORY = int(os.getenv("NUM_DAYS_HISTORY", 90))

RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
OUTPUT_DIR = RAW_DIR


def load_reference_data() -> tuple[pd.DataFrame, list]:
    """
    Baca stores.csv & products.csv yang sudah ada, supaya inventory yang
    digenerate tidak punya store_id/product_id yang tidak ada di dimension
    table-nya. stores_df dikembalikan utuh (bukan cuma id) karena store_type
    dipakai untuk menentukan assortment (lihat assign_store_assortment).

    Returns:
        (stores_df, product_ids)
    """
    stores_df = pd.read_csv(os.path.join(RAW_DIR, "stores.csv"))
    products_df = pd.read_csv(os.path.join(RAW_DIR, "products.csv"))
    return stores_df, products_df["product_id"].tolist()


def assign_store_assortment(stores_df: pd.DataFrame, product_ids: list) -> dict:
    """
    Tentukan subset produk yang di-stock tiap toko, sekali per toko (bukan per hari).
    Proporsi tergantung store_type — mensimulasikan flagship stock lebih lengkap
    daripada kiosk. Ini BUKAN noise/error, ini desain bisnis: kombinasi
    store-product yang tidak muncul di sini memang sengaja tidak pernah ada
    datanya, beda dari missing value yang perlu di-flag saat cleaning.

    Returns:
        dict {store_id: [product_id, ...]}
    """
    assortment_ratio = {
        "flagship": (0.80, 0.95),
        "regular": (0.60, 0.80),
        "kiosk": (0.30, 0.50),
    }

    assortment = {}
    for _, row in stores_df.iterrows():
        low, high = assortment_ratio[row["store_type"]]
        ratio = random.uniform(low, high)
        n_products = max(1, int(len(product_ids) * ratio))
        assortment[row["store_id"]] = random.sample(product_ids, n_products)
    return assortment


def generate_inventory(stores_df: pd.DataFrame, product_ids: list, days: int = NUM_DAYS_HISTORY) -> pd.DataFrame:
    """
    Generate snapshot inventory harian per toko, hanya untuk produk yang memang
    di-stock toko tersebut (lihat assign_store_assortment).

    Noise yang disengaja:
    - stock negatif (~1.5%): simulasi backorder yang tercatat dengan
      last_restock_date di masa depan relatif ke snapshot_date — sistem sempat
      mengurangi stock sebelum barang benar-benar diterima. Kasus nyata dari
      pengalaman kerja, bukan noise generik.
    """
    assortment = assign_store_assortment(stores_df, product_ids)

    records = []
    start_date = datetime.today().date() - timedelta(days=days)

    for day_offset in range(days):
        current_date = start_date + timedelta(days=day_offset)
        for store_id, store_products in assortment.items():
            for product_id in store_products:
                stock_qty = random.randint(0, 200)
                reorder_point = random.randint(10, 30)
                # last_restock_date: biasanya beberapa hari sebelum snapshot,
                # kadang lama tidak restock (stock lama)
                days_since_restock = random.randint(0, 30)
                last_restock_date = current_date - timedelta(days=days_since_restock)

                records.append({
                    "store_id": store_id,
                    "product_id": product_id,
                    "snapshot_date": current_date,
                    "stock_qty": stock_qty,
                    "reorder_point": reorder_point,
                    "last_restock_date": last_restock_date,
                })

    df = pd.DataFrame(records)

    # noise: stock negatif akibat backorder salah tanggal (last_restock_date
    # di-set ke masa depan relatif snapshot_date, dan stock_qty jadi negatif
    # karena sistem sudah mengurangi stock untuk barang yang belum sampai)
    dirty_idx = df.sample(frac=0.015, random_state=6).index
    df.loc[dirty_idx, "stock_qty"] = -df.loc[dirty_idx, "stock_qty"].abs() - random.randint(1, 20)
    future_offset_days = pd.to_timedelta(
        [random.randint(1, 5) for _ in range(len(dirty_idx))], unit="D"
    )
    df.loc[dirty_idx, "last_restock_date"] = (
        pd.to_datetime(df.loc[dirty_idx, "snapshot_date"]) + future_offset_days.values
    ).dt.date

    return df


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    stores_df, product_ids = load_reference_data()
    inventory_df = generate_inventory(stores_df, product_ids)

    inventory_df.to_csv(os.path.join(OUTPUT_DIR, "inventory.csv"), index=False)
    print(f"Generated {len(inventory_df)} inventory records -> data/raw/inventory.csv")


if __name__ == "__main__":
    main()