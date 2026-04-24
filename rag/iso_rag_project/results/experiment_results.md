# Experiment Results

> Auto-generated from `combined_results.csv` (30/135 rows)

## Progress

| Metric | Value |
|--------|-------|
| Total Rows | 135 |
| Completed | 30/135 (22.2%) |
| Total Runs | 3 |
| Total Time | 33.3 min |

## Accuracy Summary

| Metric | Baseline | RAG | Winner |
|--------|----------|-----|--------|
| Control Accuracy | 1/30 (3.3%) | 19/30 (63.3%) | RAG |
| Applicability Accuracy | 30/30 (100.0%) | 29/30 (96.7%) | Baseline |
| Status Accuracy | 30/30 (100.0%) | 27/30 (90.0%) | Baseline |
| Failures | 1 | — | — |

## Latency

| Metric | Baseline | RAG |
|--------|----------|-----|
| Avg Response Time | 45.7s | 57.6s |
| Total Time | 1371s | 1728s |

## Detailed Results — Control Prediction

| # | Input (truncated) | Ground Truth | Baseline Pred | B | RAG Pred | R | Retrieved Top-3 | B Time | R Time |
|---|-------------------|-------------|---------------|---|----------|---|-----------------|--------|--------|
| 1 | Organisasi telah menetapkan kebijakan keamanan informas... | A.5.1 | A.5.1 | Y | A.5.1 | Y | A.5.1, A.5.4, A.6.3 | 96.17s | 49.19s |
| 2 | Belum ada pembagian tugas dan tanggung jawab keamanan i... | A.5.2 | A.5.1 | N | A.6.5 | N | A.6.5, A.6.6, A.5.36 | 22.12s | 45.89s |
| 3 | Setiap departemen memiliki penanggung jawab keamanan in... | A.5.2 | A.5.1 | N | A.5.2 | Y | A.5.2, A.5.1, A.6.3 | 21.62s | 43.56s |
| 4 | Fungsi pengembangan dan operasional TI masih dilakukan ... | A.5.3 | A.7.3 | N | A.5.3 | Y | A.5.37, A.5.30, A.5.3 | 25.83s | 41.26s |
| 5 | Organisasi telah memisahkan tugas otorisasi pembayaran ... | A.5.3 | A.5.2 | N | A.5.3 | Y | A.5.11, A.5.3, A.5.14 | 26.57s | 45.97s |
| 6 | Manajemen belum menunjukkan komitmen terhadap keamanan ... | A.5.4 | A.5.1 | N | FAIL | N | A.5.35, A.5.1, A.5.36 | 27.08s | 50.83s |
| 7 | Direksi secara aktif mendukung program keamanan informa... | A.5.4 | A.5.1 | N | A.5.1 | N | A.5.24, A.5.1, A.5.8 | 16.39s | 46.47s |
| 8 | Daftar kontak otoritas terkait seperti BSSN dan kepolis... | A.5.5 | A.5.1 | N | A.5.5 | Y | A.5.5, A.5.6, A.5.22 | 15.46s | 80.36s |
| 9 | Organisasi tidak memiliki kontak darurat dengan pihak b... | A.5.5 | A.5.2 | N | A.5.6 | N | A.5.6, A.5.35, A.6.8 | 82.00s | 48.26s |
| 10 | Organisasi tidak memiliki kontak darurat dengan pihak b... | A.5.5 | A.5.13 | N | A.5.6 | N | A.5.6, A.5.35, A.6.8 | 98.84s | 50.15s |
| 11 | Tim keamanan aktif berpartisipasi dalam forum ISACA dan... | A.5.6 | A.6.2 | N | A.5.6 | Y | A.5.6, A.6.3, A.5.8 | 42.28s | 87.32s |
| 12 | Tim keamanan aktif berpartisipasi dalam forum ISACA dan... | A.5.6 | A.6.1 | N | A.5.6 | Y | A.5.6, A.6.3, A.5.8 | 51.86s | 90.31s |
| 13 | Organisasi tidak mengikuti forum atau komunitas keamana... | A.5.6 | A.5.12 | N | A.5.6 | Y | A.5.6, A.5.35, A.8.20 | 70.55s | 63.13s |
| 14 | Organisasi tidak mengikuti forum atau komunitas keamana... | A.5.6 | A.5.3 | N | A.5.6 | Y | A.5.6, A.5.35, A.8.20 | 59.75s | 61.82s |
| 15 | Organisasi secara rutin mengumpulkan dan menganalisis f... | A.5.7 | A.8.2 | N | A.5.7 | Y | A.5.7, A.8.16, A.8.8 | 33.45s | 53.68s |
| 16 | Organisasi secara rutin mengumpulkan dan menganalisis f... | A.5.7 | A.8.3 | N | A.5.7 | Y | A.5.7, A.8.16, A.8.8 | 35.19s | 49.68s |
| 17 | Tidak ada proses formal untuk mengumpulkan informasi te... | A.5.7 | A.5.1 | N | A.5.7 | Y | A.5.7, A.6.6, A.5.1 | 38.01s | 59.09s |
| 18 | Tidak ada proses formal untuk mengumpulkan informasi te... | A.5.7 | A.5.2 | N | A.5.7 | Y | A.5.7, A.6.6, A.5.1 | 40.16s | 68.94s |
| 19 | Setiap proyek TI baru wajib melalui penilaian risiko ke... | A.5.8 | A.5.1 | N | A.5.8 | Y | A.5.8, A.5.7, A.8.8 | 61.73s | 47.84s |
| 20 | Proyek pengembangan aplikasi dilakukan tanpa mempertimb... | A.5.8 | A.5.2 | N | A.5.8 | Y | A.5.8, A.8.26, A.8.28 | 56.20s | 41.67s |
| 21 | Register aset informasi lengkap telah dibuat dan mencak... | A.5.9 | A.7.1 | N | A.5.37 | N | A.5.37, A.5.9, A.5.13 | 21.52s | 43.29s |
| 22 | Register aset informasi lengkap telah dibuat dan mencak... | A.5.9 | A.5.1 | N | A.5.37 | N | A.5.37, A.5.9, A.5.13 | 29.22s | 42.35s |
| 23 | Organisasi belum memiliki inventarisasi lengkap atas as... | A.5.9 | A.5.1 | N | A.5.9 | Y | A.5.9, A.5.11, A.5.19 | 32.61s | 74.97s |
| 24 | Organisasi belum memiliki inventarisasi lengkap atas as... | A.5.9 | A.5.1 | N | A.5.9 | Y | A.5.9, A.5.11, A.5.19 | 56.90s | 57.89s |
| 25 | Kebijakan penggunaan email dan internet yang dapat dite... | A.5.10 | A.5.1 | N | A.5.1 | N | A.5.10, A.5.1, A.5.4 | 38.75s | 73.29s |
| 26 | Kebijakan penggunaan email dan internet yang dapat dite... | A.5.10 | A.5.1 | N | A.5.1 | N | A.5.10, A.5.1, A.5.4 | 57.58s | 64.58s |
| 27 | Proses pengembalian laptop dan kartu akses dilakukan se... | A.5.11 | A.7.1 | N | A.5.37 | N | A.8.13, A.5.11, A.5.37 | 46.24s | 84.88s |
| 28 | Proses pengembalian laptop dan kartu akses dilakukan se... | A.5.11 | A.8.5 | N | A.8.13 | N | A.8.13, A.5.11, A.5.37 | 63.92s | 51.32s |
| 29 | Informasi diklasifikasikan ke dalam empat tingkat: raha... | A.5.12 | A.5.1 | N | A.5.12 | Y | A.5.12, A.5.13, A.6.6 | 39.61s | 66.30s |
| 30 | Informasi diklasifikasikan ke dalam empat tingkat: raha... | A.5.12 | A.5.3 | N | A.5.12 | Y | A.5.12, A.5.13, A.6.6 | 63.27s | 43.59s |

## Detailed Results — Applicability & Status

| # | Control | GT Appl | B Appl | B | R Appl | R | GT Status | B Status | B | R Status | R |
|---|---------|---------|--------|---|--------|---|-----------|----------|---|----------|---|
| 1 | A.5.1 | Yes | Yes | Y | Yes | Y | Implemented | Implemented | Y | Implemented | Y |
| 2 | A.5.2 | Yes | Yes | Y | Yes | Y | Not Implemented | Not Implemented | Y | Not Implemented | Y |
| 3 | A.5.2 | Yes | Yes | Y | Yes | Y | Implemented | Implemented | Y | Implemented | Y |
| 4 | A.5.3 | Yes | Yes | Y | Yes | Y | Not Implemented | Not Implemented | Y | Partially Implemented | N |
| 5 | A.5.3 | Yes | Yes | Y | Yes | Y | Implemented | Implemented | Y | Implemented | Y |
| 6 | A.5.4 | Yes | Yes | Y | FAIL | N | Not Implemented | Not Implemented | Y | FAIL | N |
| 7 | A.5.4 | Yes | Yes | Y | Yes | Y | Implemented | Implemented | Y | Implemented | Y |
| 8 | A.5.5 | Yes | Yes | Y | Yes | Y | Implemented | Implemented | Y | Implemented | Y |
| 9 | A.5.5 | Yes | Yes | Y | Yes | Y | Not Implemented | Not Implemented | Y | Not Implemented | Y |
| 10 | A.5.5 | Yes | Yes | Y | Yes | Y | Not Implemented | Not Implemented | Y | Not Implemented | Y |
| 11 | A.5.6 | Yes | Yes | Y | Yes | Y | Implemented | Implemented | Y | Implemented | Y |
| 12 | A.5.6 | Yes | Yes | Y | Yes | Y | Implemented | Implemented | Y | Implemented | Y |
| 13 | A.5.6 | Yes | Yes | Y | Yes | Y | Not Implemented | Not Implemented | Y | Not Implemented | Y |
| 14 | A.5.6 | Yes | Yes | Y | Yes | Y | Not Implemented | Not Implemented | Y | Not Implemented | Y |
| 15 | A.5.7 | Yes | Yes | Y | Yes | Y | Implemented | Implemented | Y | Implemented | Y |
| 16 | A.5.7 | Yes | Yes | Y | Yes | Y | Implemented | Implemented | Y | Implemented | Y |
| 17 | A.5.7 | Yes | Yes | Y | Yes | Y | Not Implemented | Not Implemented | Y | Not Implemented | Y |
| 18 | A.5.7 | Yes | Yes | Y | Yes | Y | Not Implemented | Not Implemented | Y | Not Implemented | Y |
| 19 | A.5.8 | Yes | Yes | Y | Yes | Y | Implemented | Implemented | Y | Implemented | Y |
| 20 | A.5.8 | Yes | Yes | Y | Yes | Y | Not Implemented | Not Implemented | Y | Not Implemented | Y |
| 21 | A.5.9 | Yes | Yes | Y | Yes | Y | Implemented | Implemented | Y | Implemented | Y |
| 22 | A.5.9 | Yes | Yes | Y | Yes | Y | Implemented | Implemented | Y | Implemented | Y |
| 23 | A.5.9 | Yes | Yes | Y | Yes | Y | Not Implemented | Not Implemented | Y | Not Implemented | Y |
| 24 | A.5.9 | Yes | Yes | Y | Yes | Y | Not Implemented | Not Implemented | Y | Not Implemented | Y |
| 25 | A.5.10 | Yes | Yes | Y | Yes | Y | Implemented | Implemented | Y | Implemented | Y |
| 26 | A.5.10 | Yes | Yes | Y | Yes | Y | Implemented | Implemented | Y | Implemented | Y |
| 27 | A.5.11 | Yes | Yes | Y | Yes | Y | Implemented | Implemented | Y | Implemented | Y |
| 28 | A.5.11 | Yes | Yes | Y | Yes | Y | Implemented | Implemented | Y | Implemented | Y |
| 29 | A.5.12 | Yes | Yes | Y | Yes | Y | Implemented | Implemented | Y | Partially Implemented | N |
| 30 | A.5.12 | Yes | Yes | Y | Yes | Y | Implemented | Implemented | Y | Implemented | Y |

## Run History

| Run | Timestamp | Processed | Baseline Correct | RAG Correct | Fails | Time | Stop Reason |
|-----|-----------|-----------|-----------------|-------------|-------|------|-------------|
| 1 | 2026-02-26 16:32:29 | 8 | 1 | 5 | 1 | 663.9s | time_limit |
| 2 | 2026-02-26 19:57:06 | 6 | 0 | 5 | 0 | 701.8s | time_limit |
| 3 | 2026-02-26 20:19:18 | 6 | 0 | 3 | 0 | 630.7s | time_limit |
