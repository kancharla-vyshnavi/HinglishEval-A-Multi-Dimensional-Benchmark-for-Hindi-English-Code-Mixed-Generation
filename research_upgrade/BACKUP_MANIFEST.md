# HinglishEval: Backup Manifest

**Manifest Date:** `2026-10-13 20:25:34 UTC`  
**Purpose:** Formal catalog of all protected checkpoints, datasets, and human ratings snapshots.

---

## 1. Protected Archive Catalog

| Backup Identifier | Source Location | Destination Archive Path | Contents & Record Counts |
| :--- | :--- | :--- | :--- |
| **Annotator B Snapshot** | `research_upgrade/human_validation/` | `research_upgrade/archive/annotator_b/` | 15 ratings in `ratings_snapshot_with_b_15.db`, `annotator_B_ratings.csv`, `annotator_B_rating_sheet.csv`, `annotator_B_pending_ratings.csv` |
| **Annotator A Master Table** | `research_upgrade/human_validation/ratings.db` | `research_upgrade/tables/human_ratings_annotator_a_500.csv` | Exactly 500 verified ratings, 0 nulls, 125 samples per model |
| **Original Paper Preservation** | Repository Root | `paper.md` (Root) | Original untouched manuscript (27,087 bytes) preserved |
| **Task 4 Judge Checkpoint** | `research_upgrade/tables/` | `judge_qwen25_3b_4000_results.jsonl` | 488 dual-judge records preserved on disk |
| **Original Benchmark Prompts** | `data/benchmarks/` | `data/benchmarks/hinglish_bench_.csv` | 1,000 benchmark prompts strictly preserved |
| **Original Generations** | `outputs/controlled_1000/` | `outputs/controlled_1000/benchmark_generations_.csv` | 4,000 model generations strictly preserved |

---

## 2. Retention Guarantee

- **Zero Overwrite Rule:** No experimental run or script modifies or deletes files in `data/`, `models/`, or `outputs/`.
- **Reproducibility Guarantee:** All original data needed to reproduce prior findings remains in its original repository path.
