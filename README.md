# Retail DE Mid — Medallion Architecture di Databricks Free Edition

Project ini adalah tahap **Mid** dari roadmap Data Engineer (lihat `roadmap-data-engineer-databricks-first.md`).
Melanjutkan `retail-de-junior`: pipeline yang sama dipindah ke lakehouse — Bronze/Silver/Gold,
PySpark native, dbt-databricks, orkestrasi via Databricks Jobs, governance dasar via Unity Catalog.

> **Catatan posisi:** project ini terpisah dari `retail-dbt` (portofolio Analytics Engineer).
> Fokus di sini adalah engineering layer (ingestion, orchestration, governance), bukan business modeling.

## Skenario

Sama seperti Junior: data sintetis retail multi-toko. Bedanya, di sini sumbernya diperlakukan
sebagai landing zone (Volume) yang disimulasikan seperti object storage, lalu diproses lewat
medallion architecture penuh.

## Arsitektur

<!-- Ganti dengan diagram nyata setelah pipeline jadi. Sementara isi manual: -->
```
[Junior output CSV] -> Unity Catalog Volume -> Bronze (Delta) -> Silver (Delta) -> dbt (staging/int/mart) -> Gold
                                                                                          |
                                                                          Databricks Jobs orchestrates all
```

## Struktur Project

```
retail-de-mid/
├── notebooks/          # eksplorasi Bronze/Silver dengan PySpark
├── src/                # ingestion script (bronze), transformasi silver (non-dbt)
├── dbt/                # project dbt-databricks: staging, intermediate, mart
├── jobs/                # definisi Databricks Job (JSON/YAML export)
├── docs/
│   ├── decisions/       # 1 file per keputusan desain penting (lihat format di bawah)
│   ├── data_dictionary.md
│   └── pandas_vs_pyspark_notes.md   # perbandingan cara mikir Junior vs Mid
├── .github/workflows/   # CI/CD: dbt build
└── PROGRESS.md          # tracking per-step, lihat roadmap
```

## Cara Menjalankan

<!-- Isi setelah environment jadi -->
1. Setup `.env` dari `.env.example` (kredensial Databricks)
2. `python test_connection.py` — verifikasi koneksi SQL Warehouse
3. Upload data Junior ke Unity Catalog Volume: `TODO`
4. Jalankan notebook Bronze ingestion: `TODO`
5. `cd dbt && dbt run && dbt test`
6. Import & jalankan Databricks Job: `TODO`

## Alur Berpikir

<!-- Ini bagian paling penting untuk portofolio — isi progresif per milestone, jangan tunggu selesai semua.
     Formatnya sama seperti Junior README: bukan daftar tools, tapi urutan keputusan dan alasannya. -->

1. **Kenapa pindah dari Pandas ke PySpark di sini** — TODO setelah Bronze/Silver selesai,
   bandingkan konkret: apa yang beda cara mikirnya, bukan cuma beda sintaks.
2. **Kenapa Unity Catalog Volume, bukan DBFS** — TODO, singkat: DBFS legacy, Volume yang didukung penuh Free Edition.
3. **Desain schema Bronze→Silver→Gold** — TODO, link ke `docs/data_dictionary.md`.
4. **Kenapa dbt-databricks dipertahankan dari retail-dbt, bukan ditulis ulang dari nol** — TODO.
5. **Governance dasar: kenapa 2 schema (`sales`, `inventory`), bukan 1** — TODO.

## Next Step (Level Senior)

Lihat roadmap `roadmap-data-engineer-databricks-first.md` — Senior menambahkan streaming (Kafka+Flink lokal),
Lakeflow Declarative Pipelines, dan jalur AWS paralel (S3+Glue+Terraform).
