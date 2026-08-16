"""
Generate synthetic multi-store retail data: stores, products, and sales transactions.

Data is deliberately generated "dirty" in realistic ways (missing values,
duplicates, wrong data types, negative prices) so the downstream EDA and
cleaning steps (see Notebooks/04_silver_cleaning.py) have real problems to
solve — not a formality. Noise percentages are configurable via constants below.
"""

import os
import random
from datetime import datetime, timedelta

import pandas as pd
from dotenv import load_dotenv
from faker import Faker

load_dotenv()

fake = Faker("id_ID")
random.seed(42)
Faker.seed(42)

NUM_STORES = int(os.getenv("NUM_STORES", 30))
NUM_PRODUCTS = int(os.getenv("NUM_PRODUCTS", 200))
NUM_DAYS_HISTORY = int(os.getenv("NUM_DAYS_HISTORY", 90))

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")

STORE_TYPES = ["flagship", "regular", "kiosk"]
REGIONS = ["Jawa Timur", "Jawa Barat", "Jawa Tengah", "DKI Jakarta", "Bali", "Sumatra Utara"]
PAYMENT_METHODS = ["cash", "debit", "credit_card", "qris", "ewallet"]
CATEGORIES = ["Makanan", "Minuman", "Kebutuhan Rumah Tangga", "Perawatan Diri", "Elektronik Kecil"]


def generate_stores(n=NUM_STORES) -> pd.DataFrame:
    stores = []
    for store_id in range(1, n + 1):
        stores.append({
            "store_id": store_id,
            "store_name": f"Toko {fake.city()} {store_id}",
            "city": fake.city(),
            "region": random.choice(REGIONS),
            "store_type": random.choice(STORE_TYPES),
            "opened_date": fake.date_between(start_date="-5y", end_date="-30d"),
        })
    df = pd.DataFrame(stores)

    # noise: beberapa store_name kosong (simulasi input manual yang lupa diisi)
    dirty_idx = df.sample(frac=0.03, random_state=1).index
    df.loc[dirty_idx, "store_name"] = None
    return df


def generate_products(n=NUM_PRODUCTS) -> pd.DataFrame:
    products = []
    for product_id in range(1, n + 1):
        products.append({
            "product_id": product_id,
            "product_name": fake.catch_phrase(),
            "category": random.choice(CATEGORIES),
            "unit_price": round(random.uniform(2000, 250000), 2),
        })
    df = pd.DataFrame(products)

    # noise: beberapa unit_price negatif (simulasi salah input / refund tercatat salah)
    dirty_idx = df.sample(frac=0.02, random_state=2).index
    df.loc[dirty_idx, "unit_price"] = -df.loc[dirty_idx, "unit_price"]

    # noise: beberapa unit_price disimpan sebagai string dengan format salah
    # (cast ke object dulu supaya pandas mengizinkan campuran float & string di kolom yang sama)
    df["unit_price"] = df["unit_price"].astype(object)
    dirty_idx2 = df.sample(frac=0.02, random_state=3).index
    df.loc[dirty_idx2, "unit_price"] = df.loc[dirty_idx2, "unit_price"].apply(
        lambda x: f"Rp {x:,.0f}"
    )
    return df


def generate_transactions(stores_df: pd.DataFrame, products_df: pd.DataFrame,
                           days=NUM_DAYS_HISTORY) -> pd.DataFrame:
    transactions = []
    transaction_id = 1
    start_date = datetime.today().date() - timedelta(days=days)

    store_ids = stores_df["store_id"].tolist()
    product_ids = products_df["product_id"].tolist()
    price_lookup = dict(zip(products_df["product_id"], products_df["unit_price"]))

    for day_offset in range(days):
        current_date = start_date + timedelta(days=day_offset)
        # jumlah transaksi per hari bervariasi per toko (bukan flat, biar realistis)
        for store_id in store_ids:
            daily_tx_count = random.randint(5, 40)
            for _ in range(daily_tx_count):
                product_id = random.choice(product_ids)
                unit_price = price_lookup[product_id]
                # kalau unit_price hasil noise (string/negatif), pakai fallback angka wajar
                try:
                    price_val = float(str(unit_price).replace("Rp", "").replace(",", "").strip())
                    price_val = abs(price_val)
                except ValueError:
                    price_val = round(random.uniform(2000, 250000), 2)

                quantity = random.randint(1, 5)
                transactions.append({
                    "transaction_id": transaction_id,
                    "store_id": store_id,
                    "product_id": product_id,
                    "transaction_date": current_date,
                    "quantity": quantity,
                    "unit_price": price_val,
                    "total_amount": round(quantity * price_val, 2),
                    "payment_method": random.choice(PAYMENT_METHODS),
                })
                transaction_id += 1

    df = pd.DataFrame(transactions)

    # noise: duplikat transaksi (simulasi double-submit dari POS)
    dup_sample = df.sample(frac=0.01, random_state=4)
    df = pd.concat([df, dup_sample], ignore_index=True)

    # noise: beberapa quantity kosong/null (simulasi sensor/POS error)
    dirty_idx = df.sample(frac=0.01, random_state=5).index
    df.loc[dirty_idx, "quantity"] = None

    return df


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    stores_df = generate_stores()
    products_df = generate_products()
    transactions_df = generate_transactions(stores_df, products_df)

    stores_df.to_csv(os.path.join(OUTPUT_DIR, "stores.csv"), index=False)
    products_df.to_csv(os.path.join(OUTPUT_DIR, "products.csv"), index=False)
    transactions_df.to_csv(os.path.join(OUTPUT_DIR, "transactions.csv"), index=False)

    print(f"Generated {len(stores_df)} stores -> data/raw/stores.csv")
    print(f"Generated {len(products_df)} products -> data/raw/products.csv")
    print(f"Generated {len(transactions_df)} transactions -> data/raw/transactions.csv")


if __name__ == "__main__":
    main()
