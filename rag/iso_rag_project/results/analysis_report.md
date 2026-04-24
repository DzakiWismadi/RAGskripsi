# RAG Experiment Analysis Report
**Generated:** 2026-02-27
**Dataset:** 200 audit findings (135 unique sentences × variations)
**Model:** CybersecurityRiskAnalyst 8B Q4_0 (Ollama)

---

## 1. Overall Performance Summary

| Metric | Baseline | RAG | Improvement |
|--------|----------|-----|-------------|
| **Control Accuracy** | 4/200 (2.0%) | 132/200 (66.0%) | **+64%** |
| **Failures** | 3 | 7 | — |
| **Avg Response Time** | ~42s | ~55s | +13s overhead |

### RAG Pipeline Breakdown

| Category | Count | % |
|----------|-------|---|
| **Correct** | 132 | 66.0% |
| **Wrong (correct in top-3)** | 34 | 17.0% |
| **Wrong (NOT in top-3)** | 27 | 13.5% |
| **Failures** | 7 | 3.5% |
| **Total** | 200 | 100% |

### Retrieval Quality
- **Recall@3:** 168/200 (84.0%) — Ground truth was in retrieved top-3

---

## 2. Full Results Table (200 Rows)

| # | Sentence (truncated) | GT | Baseline | B✓ | RAG | R✓ | InTop3 | Top3 Retrieved |
|---|----------------------|-----|----------|-----|-----|-----|--------|----------------|
| 1 | Organisasi telah menetapkan kebijakan... | A.5.1 | A.5.1 | Y | A.5.1 | Y | Y | A.5.1;A.5.4;A.6.3 |
| 2 | Belum ada pembagian tugas dan tanggung... | A.5.2 | A.5.1 | N | A.6.5 | N | N | A.6.5;A.6.6;A.5.36 |
| 3 | Setiap departemen memiliki penanggung... | A.5.2 | A.5.1 | N | A.5.2 | Y | Y | A.5.2;A.5.1;A.6.3 |
| 4 | Fungsi pengembangan dan operasional TI... | A.5.3 | A.7.3 | N | A.5.3 | Y | Y | A.5.37;A.5.30;A.5.3 |
| 5 | Organisasi telah memisahkan tugas... | A.5.3 | A.5.2 | N | A.5.3 | Y | Y | A.5.11;A.5.3;A.5.14 |
| 6 | Manajemen belum menunjukkan komitmen... | A.5.4 | A.5.1 | N | FAIL | N | N | A.5.35;A.5.1;A.5.36 |
| 7 | Direksi secara aktif mendukung program... | A.5.4 | A.5.1 | N | A.5.1 | N | N | A.5.24;A.5.1;A.5.8 |
| 8 | Daftar kontak otoritas terkait seperti... | A.5.5 | A.5.1 | N | A.5.5 | Y | Y | A.5.5;A.5.6;A.5.22 |
| 9 | Organisasi tidak memiliki kontak darurat... | A.5.5 | A.5.2 | N | A.5.6 | N | N | A.5.6;A.5.35;A.6.8 |
| 10 | Organisasi tidak memiliki kontak darurat... | A.5.5 | A.5.13 | N | A.5.6 | N | N | A.5.6;A.5.35;A.6.8 |
| 11 | Tim keamanan aktif berpartisipasi dalam... | A.5.6 | A.6.2 | N | A.5.6 | Y | Y | A.5.6;A.6.3;A.5.8 |
| 12 | Tim keamanan aktif berpartisipasi dalam... | A.5.6 | A.6.1 | N | A.5.6 | Y | Y | A.5.6;A.6.3;A.5.8 |
| 13 | Organisasi tidak mengikuti forum atau... | A.5.6 | A.5.12 | N | A.5.6 | Y | Y | A.5.6;A.5.35;A.8.20 |
| 14 | Organisasi tidak mengikuti forum atau... | A.5.6 | A.5.3 | N | A.5.6 | Y | Y | A.5.6;A.5.35;A.8.20 |
| 15 | Organisasi secara rutin mengumpulkan... | A.5.7 | A.8.2 | N | A.5.7 | Y | Y | A.5.7;A.8.16;A.8.8 |
| 16 | Organisasi secara rutin mengumpulkan... | A.5.7 | A.8.3 | N | A.5.7 | Y | Y | A.5.7;A.8.16;A.8.8 |
| 17 | Tidak ada proses formal untuk mengumpulkan... | A.5.7 | A.5.1 | N | A.5.7 | Y | Y | A.5.7;A.6.6;A.5.1 |
| 18 | Tidak ada proses formal untuk mengumpulkan... | A.5.7 | A.5.2 | N | A.5.7 | Y | Y | A.5.7;A.6.6;A.5.1 |
| 19 | Setiap proyek TI baru wajib melalui... | A.5.8 | A.5.1 | N | A.5.8 | Y | Y | A.5.8;A.5.7;A.8.8 |
| 20 | Proyek pengembangan aplikasi dilakukan... | A.5.8 | A.5.2 | N | A.5.8 | Y | Y | A.5.8;A.8.26;A.8.28 |
| 21 | Register aset informasi lengkap telah... | A.5.9 | A.7.1 | N | A.5.37 | N | Y | A.5.37;A.5.9;A.5.13 |
| 22 | Register aset informasi lengkap telah... | A.5.9 | A.5.1 | N | A.5.37 | N | Y | A.5.37;A.5.9;A.5.13 |
| 23 | Organisasi belum memiliki inventarisasi... | A.5.9 | A.5.1 | N | A.5.9 | Y | Y | A.5.9;A.5.11;A.5.19 |
| 24 | Organisasi belum memiliki inventarisasi... | A.5.9 | A.5.1 | N | A.5.9 | Y | Y | A.5.9;A.5.11;A.5.19 |
| 25 | Kebijakan penggunaan email dan internet... | A.5.10 | A.5.1 | N | A.5.1 | N | Y | A.5.10;A.5.1;A.5.4 |
| 26 | Kebijakan penggunaan email dan internet... | A.5.10 | A.5.1 | N | A.5.1 | N | Y | A.5.10;A.5.1;A.5.4 |
| 27 | Proses pengembalian laptop dan kartu... | A.5.11 | A.7.1 | N | A.5.37 | N | Y | A.8.13;A.5.11;A.5.37 |
| 28 | Proses pengembalian laptop dan kartu... | A.5.11 | A.8.5 | N | A.8.13 | N | Y | A.8.13;A.5.11;A.5.37 |
| 29 | Informasi diklasifikasikan ke dalam... | A.5.12 | A.5.1 | N | A.5.12 | Y | Y | A.5.12;A.5.13;A.6.6 |
| 30 | Informasi diklasifikasikan ke dalam... | A.5.12 | A.5.3 | N | A.5.12 | Y | Y | A.5.12;A.5.13;A.6.6 |
| 31-200 | *(see full CSV for all rows)* | ... | ... | ... | ... | ... | ... | ... |

**Legend:** GT = Ground Truth, B✓ = Baseline Correct, R✓ = RAG Correct, InTop3 = GT was in retrieved top-3

---

## 3. RAG Pipeline Error Analysis

### 3.1 Wrong Predictions Where GT Was in Top-3 (34 cases)

**Problem:** LLM had the correct control in retrieved context but chose wrong one.

| # | GT | RAG Predicted | Issue | Top3 Retrieved |
|---|-----|--------------|-------|----------------|
| 1-2 | A.5.9 | A.5.37 | Asset register vs operational procedures | A.5.37;A.5.9;A.5.13 |
| 3-4 | A.5.10 | A.5.1 | Email policy vs general security policy | A.5.10;A.5.1;A.5.4 |
| 5-6 | A.5.11 | A.5.37 / A.8.13 | Asset return vs disposal vs backup | A.8.13;A.5.11;A.5.37 |
| 7 | A.5.14 | A.8.15 | Data transfer vs logging | A.8.15;A.5.14;A.5.33 |
| 8 | A.5.17 | A.8.5 | MFA vs privilege access | A.8.5;A.8.21;A.5.17 |
| 9 | A.5.22 | A.5.24 | Supplier audit vs incident management | A.5.24;A.5.22;A.8.25 |
| 10 | A.5.30 | A.8.13 | RTO/RPO vs backup procedures | A.8.13;A.5.30;A.5.37 |
| 11-12 | A.6.2 | A.6.6 | Contract terms vs NDAs | A.6.2;A.5.20;A.6.6 |
| 13 | A.6.4 | A.5.1 | Discipline procedures vs policy | A.6.4;A.5.36;A.5.1 |
| 14 | A.6.5 | A.5.11 | Offboarding vs asset return | A.5.11;A.5.14;A.6.5 |
| 15-16 | A.6.8 | A.6.3 | Reporting portal vs training | A.6.8;A.6.3;A.7.4 |
| 17 | A.7.1 | A.7.4 | Physical perimeter vs CCTV | A.7.4;A.7.3;A.7.1 |
| 18 | A.7.4 | A.7.3 | CCTV vs physical security | A.7.3;A.7.4;A.6.8 |
| 19-20 | A.7.10 | A.7.14 | Media destruction vs disposal | A.7.14;A.8.10;A.7.10 |

**Pattern:** Heavily related controls often cause confusion. The LLM sometimes picks a semantically close but incorrect control.

---

### 3.2 Wrong Predictions Where GT Was NOT in Top-3 (27 cases)

**Problem:** Retrieval failed to find the correct control.

| # | GT | RAG Predicted | Retrieved Instead | Issue |
|---|-----|--------------|-------------------|-------|
| 1 | A.5.2 | A.6.5 | A.6.5;A.6.6;A.5.36 | "pembagian tugas" → termination context |
| 2 | A.5.4 | A.5.1 | A.5.24;A.5.1;A.5.8 | Management commitment → policy |
| 3-4 | A.5.5 | A.5.6 | A.5.6;A.5.35;A.6.8 | Contact authorities → professional forums |
| 5 | A.5.14 | A.8.5 | A.8.5;A.8.12;A.5.17 | Email encryption → MFA context |
| 6 | A.5.17 | A.8.24 | A.8.24;A.8.28;A.6.6 | Password → encryption policies |
| 7 | A.5.22 | A.5.20 | A.5.21;A.5.20;A.6.2 | Supplier monitoring → supplier agreements |
| 8 | A.5.24 | A.5.36 | A.6.6;A.5.35;A.5.36 | Incident procedures → compliance review |
| 9 | A.5.27 | A.5.26 | A.5.26;A.8.16;A.8.15 | Post-incident → incident response |
| 10 | A.5.29 | A.8.29 | A.8.29;A.8.26;A.8.16 | InfoSec in strategy → ICT continuity |
| 11-12 | A.7.1 | A.7.2 | A.7.3;A.7.2;A.8.3 | Physical access → office areas |
| 13-14 | A.7.8 | A.8.6 / A.7.10 | A.8.6;A.5.37;A.6.8 | Server room → capacity monitoring |
| 15-16 | A.7.9 | A.8.1 | A.8.1;A.8.5;A.7.14 | Laptop security → device management |
| 17-18 | A.7.11 | A.8.29 | A.8.29;A.5.37;A.8.19 | UPS power → ICT continuity |
| 19-20 | A.8.1 | A.8.9 | A.8.9;A.8.27;A.8.7 | MDM → configuration management |
| 21-22 | A.8.2 | A.8.18 / A.5.18 | A.5.18;A.8.3;A.8.18 | Admin access → privileged access |
| 23-25 | A.8.24 | A.8.5 / A.8.1 | A.8.5;A.7.14;A.8.28 | Encryption → MFA / device mgmt |
| 26 | A.7.1 | A.7.3 | A.7.3;A.7.9;A.7.2 | Physical security not applicable |
| 27 | A.8.22 | A.5.23 | A.5.23;A.8.21;A.8.20 | Network segregation → cloud services |

**Pattern:** Semantic similarity in Indonesian language sometimes retrieves wrong context. "Kontak" retrieves A.5.6 (forums) instead of A.5.5 (authorities). Keywords like "pembagian" trigger wrong associations.

---

## 4. Most Common Control Switches

| Switch | Count | Explanation |
|--------|-------|-------------|
| A.5.5 → A.5.6 | 2x | Authorities contact vs professional forums |
| A.5.9 → A.5.37 | 2x | Asset inventory vs operational procedures |
| A.5.10 → A.5.1 | 2x | Email/internet policy vs general policy |
| A.6.2 → A.6.6 | 2x | Contract terms vs NDAs |
| A.6.8 → A.6.3 | 2x | Reporting portal vs training |
| A.7.1 → A.7.2 | 2x | Physical perimeter vs office areas |
| A.7.9 → A.8.1 | 2x | Laptop security vs device management |
| A.7.10 → A.7.14 | 2x | Media storage vs disposal |
| A.7.11 → A.8.29 | 2x | Power supply vs continuity |
| A.8.1 → A.8.9 | 2x | Endpoint security vs configuration |
| A.8.7 → A.8.19 | 2x | Anti-malware vs software installation |
| A.8.11 → A.8.33 | 2x | Data masking vs test data |
| A.8.14 → A.8.9 | 2x | High availability vs configuration |
| A.8.24 → A.8.5 | 2x | Encryption vs MFA |
| A.8.31 → A.5.22 | 2x | Dev environment vs change management |

---

## 5. Key Findings for Thesis

### 5.1 RAG Effectiveness
- **66% accuracy** vs 2% baseline — **32x improvement**
- **84% Recall@3** — Retrieval finds correct control in top-3 most of the time
- **13.5%** errors are due to retrieval failure (embedding mismatch)
- **17%** errors are due to LLM selection (correct context, wrong choice)

### 5.2 Error Categories

| Error Type | % | Cause | Mitigation |
|------------|---|-------|------------|
| Retrieval failure | 13.5% | Embedding semantic mismatch | Hybrid search, reranking |
| LLM selection | 17% | Ambiguous/retrieved controls | Better prompts, reranking |
| System failure | 3.5% | Client connection error | Retry mechanism |

### 5.3 Heavily Confused Control Groups

1. **A.5.x Policies** — A.5.1, A.5.4, A.5.10 often confused (general policy terms)
2. **A.6.x HR Security** — A.6.2, A.6.6, A.6.3 (contracts vs NDAs vs training)
3. **A.7.x Physical** — A.7.1, A.7.2, A.7.3, A.7.4 (overlapping security zones)
4. **A.8.x Technical** — A.8.1, A.8.5, A.8.9, A.8.24 (access, MFA, config, encryption)

---

## 6. Recommendations

### For Thesis Discussion:
1. **RAG significantly improves control mapping** (66% vs 2%)
2. **Retrieval quality is the bottleneck** (84% Recall@3 leaves room for improvement)
3. **CPU-only constraints work** — 7B model with RAG is viable
4. **Error analysis shows systematic confusion** in semantically related controls

### For Future Work:
1. Implement hybrid search (keyword + semantic)
2. Add cross-encoder reranker for top-5 → top-1
3. Improve prompt engineering to reduce LLM selection errors
4. Add domain-specific Indonesian cybersecurity embeddings
