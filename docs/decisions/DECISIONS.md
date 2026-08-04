# Architecture & Data Decisions — retail-de-mid

Format tiap section: Context → Options → Decision → Consequence.

---

## 1. Negative Price Products (Silver — stg_products)

**Context**
Kolom `price` di `bronze.products` punya 4 baris null dan beberapa baris
bernilai negatif. Tidak ada kolom lain yang bisa dipakai untuk merekonstruksi
harga yang benar.

**Options**
- A. Drop semua baris bermasalah (null + negative)
- B. Impute null dengan rata-rata/median kategori
- C. Drop null, flag negative + biarkan nilainya (placeholder kolom baru)

**Decision**
Opsi C — drop 4 baris null price (tidak ada dasar rekonstruksi), flag baris
negative price via kolom baru `is_price_suspect` tanpa mengubah nilainya.

**Consequence**
`stg_products` turun dari 200 jadi 196 baris. Baris dengan `is_price_suspect
= true` tetap ikut proses downstream, consumer (dbt mart) bisa memilih
exclude berdasarkan flag ini kalau perlu.

---

## 2. Quantity Imputation (Silver — stg_transactions)

**Context**
611 baris di `bronze.transactions` punya `quantity` null, tapi kolom
`total_amount` dan `unit_price` tersedia dan valid untuk baris yang sama.

**Options**
- A. Drop baris dengan quantity null
- B. Impute quantity = `round(total_amount / unit_price)`
- C. Flag saja, biarkan null

**Decision**
Opsi B — impute via `round(total_amount / unit_price)`, karena hasilnya bisa
diverifikasi secara matematis dari kolom lain yang sudah ada dan valid.

**Consequence**
605 baris duplikat murni juga di-dedup pada langkah yang sama. Total
`stg_transactions` = 60537 baris (dari 61142 bronze). Tidak ada kolom flag
tambahan karena imputasi ini dianggap reliable, bukan asumsi.

---

## 3. Name Missing Stores (Silver — stg_stores)

**Context**
1 baris di `bronze.stores` punya `store_name` null. Tidak ada kolom lain
yang bisa dipakai untuk merekonstruksi nama toko tersebut.

**Options**
- A. Drop baris tersebut
- B. Flag + isi placeholder `"Unknown"`

**Decision**
Opsi B — flag via kolom baru `is_name_missing`, isi `store_name` dengan
`"Unknown"`. Baris tetap dipertahankan karena `store_id`-nya kemungkinan
masih dipakai di tabel transactions/inventory (baris tidak esensial untuk
di-drop, tapi diperlukan untuk join).

**Consequence**
`stg_stores` tetap 30 baris. Consumer downstream perlu aware kalau
`store_name = "Unknown"` bukan data asli, harus cek `is_name_missing`
sebelum dipakai di reporting yang customer-facing.

---

## 4. Backorder Anomaly (Silver — stg_inventory)

**Context**
5501 baris di `bronze.inventory` punya `last_restock_date > snapshot_date`
— secara logika tidak mungkin (restock tercatat terjadi setelah tanggal
snapshot pengecekan stok).

**Options**
- A. Drop baris anomali
- B. Flag saja tanpa mengubah data, biarkan konsumen memutuskan

**Decision**
Opsi B — flag via kolom baru `is_backorder_anomaly`. Baris tidak di-drop
karena datanya (stock_qty, reorder_point) tetap valid dan berguna, hanya
`last_restock_date`-nya yang mencurigakan — bukan alasan cukup untuk buang
seluruh baris.

**Consequence**
`stg_inventory` tetap 366750 baris (sama dengan bronze). Mart yang
menggunakan restock date perlu filter berdasarkan flag ini.

---

## 5. Referential Integrity — Transactions & Inventory (Silver → dbt)

**Context**
Referential integrity check (step 4b, `04b_referential_integrity_check.py`)
menemukan:
- `transactions`: 1191 orphan rows (1.97%), 4 distinct orphan `product_id`
- `inventory`: 8280 orphan rows (2.26%), 4 distinct orphan `product_id`

Investigasi: 4 `product_id` yang sama persis dengan 4 produk yang di-drop
dari `stg_products` di Decision #1 (null price).

**Options**
- A. Left join, biarkan orphan masuk dengan product info null
- B. Inner join, auto-exclude orphan
- C. Investigasi ulang & restore 4 produk yang di-drop

**Decision**
Opsi B — inner join untuk `int_store_daily_summary` di dbt. Orphan rows
bukan data quality issue baru, sudah merupakan konsekuensi langsung dari
Decision #1 yang sudah didokumentasikan dan disengaja.

**Consequence**
`int_store_daily_summary` dan mart turunannya (`mart_sales_performance`,
`mart_inventory_status`) tidak menyertakan transaksi/inventory untuk 4
produk yang di-drop. Total exclude ~1.97-2.26% baris dari sumbernya —
diterima karena root cause sudah diverifikasi, bukan silent data loss.

---

## 6. Skip dbt Staging Layer (dbt architecture)

**Context**
Pola umum dbt project (termasuk `retail-dbt`, project AE sebelumnya) selalu
punya staging layer sendiri (`stg_*` di dbt) yang melakukan cleaning ringan
sebelum masuk ke intermediate/mart.

Di `retail-de-mid`, PySpark Silver layer sudah melakukan pekerjaan yang
setara: dedup, casting, dan flagging anomali (lihat Decision #1-4).

**Options**
- A. Tetap buat staging layer dbt sendiri (duplikasi logic dengan Silver)
- B. Skip staging dbt, `sources.yml` langsung reference `silver.stg_*`,
  dbt model dimulai dari `intermediate`

**Decision**
Opsi B — skip staging layer dbt. `_intermediate__sources.yml` point
langsung ke `de_project.silver.stg_*`.

**Consequence**
Struktur dbt project ini beda dari `retail-dbt` (yang punya staging dbt).
Perbedaan ini disengaja dan didokumentasikan supaya tidak disalahartikan
sebagai langkah yang terlewat saat direview. Trade-off: cleaning logic
splitted antara PySpark dan dbt, bukan terpusat di satu tempat — perlu
disebutkan eksplisit di README kalau ada yang membaca project ini sebagai
referensi.
