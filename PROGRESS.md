# PROGRESS — Level Mid

Tracking per-step sesuai `roadmap-data-engineer-databricks-first.md` bagian LEVEL MID.
Update tanggal + catatan singkat tiap kali satu step selesai — ini juga jadi bukti progres
kalau ditanya "berapa lama ngerjain ini" saat interview, dan jadi draft mentah untuk
LinkedIn post progress (pola yang sudah pernah dipakai untuk `retail-dbt`).

Status: `[ ]` belum | `[~]` sedang jalan | `[x]` selesai

| # | Step | Status | Tanggal selesai | Catatan / blocker |
|---|------|--------|------------------|---------------------|
| 1 | Daftar Databricks Free Edition, buat workspace | [ ] | | |
| 2 | Upload dataset Junior ke Unity Catalog Volume | [ ] | | |
| 3 | Bronze: PySpark read + `_ingested_at` + Delta table | [ ] | | |
| 4 | Silver: cleaning ulang di PySpark, bandingkan vs Pandas | [ ] | | |
| 5 | Aktifkan SQL Warehouse + pasang dbt-databricks | [ ] | | |
| 6 | Pindahkan logic dbt dari retail-dbt (staging/int/mart) | [ ] | | |
| 7 | dbt tests: not_null, unique, relationships | [ ] | | |
| 8 | Databricks Jobs: Bronze -> Silver -> dbt run -> dbt test | [ ] | | |
| 9 | Unity Catalog: 2 schema (sales, inventory) + grant | [ ] | | |
| 10 | Sumber kedua (inventory) + int_store_daily_summary | [ ] | | |
| 11 | Gold terpisah: mart_sales_performance, mart_inventory_status | [ ] | | |
| 12 | CI/CD: GitHub Actions untuk dbt build | [ ] | | |

## Log Mingguan

<!-- Isi tiap kali kerja (weekend-only). Format bebas, tapi konsisten. -->

### YYYY-MM-DD
- Dikerjakan:
- Kendala:
- Keputusan diambil:
- Next:

## Bahan Portofolio yang Terkumpul (isi progresif)

- [ ] Screenshot Unity Catalog schema/grant (untuk LinkedIn/README)
- [ ] Screenshot Databricks Jobs DAG
- [ ] Perbandingan runtime/hasil Pandas (Junior) vs PySpark (Mid) untuk step cleaning yang sama
- [ ] 1 paragraf "kenapa" per keputusan besar (masuk ke `docs/decisions/`)
