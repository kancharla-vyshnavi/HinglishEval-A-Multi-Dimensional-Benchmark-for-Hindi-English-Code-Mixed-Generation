# HinglishEval: Complete Project Asset Inventory

**Audit Timestamp:** `2026-10-13 20:25:34 UTC`  
**Repository Working Directory:** `C:\Users\vyshu\OneDrive\Desktop\HinglishLLM`  
**Scope:** Full recursive inventory of datasets, checkpoints, benchmark artifacts, scripts, and tables.

---

## 1. Core Dataset & Benchmark Inventory

| Asset Name | Relative Path | Size | Description & Role | Integrity Status |
| :--- | :--- | :---: | :--- | :---: |
| **Full CPT Training Set** | `C:\Users\vyshu\Downloads\train.jsonl` | 32.3 MB | 277,431 code-mixed Hinglish sequences used for continued pre-training. | Verified (277,431 rows) |
| **CPT Validation Set** | `data/processed/cpt/validation.jsonl` | 1.70 MB | 14,601 holdout sequences for loss and perplexity evaluation. | Verified (14,601 rows) |
| **Original 1K Benchmark** | `data/benchmarks/hinglish_bench_.csv` | 438 KB | 1,000 diverse real-world Hinglish prompts across 8 communicative domains. | Verified (1,000 prompts) |
| **Proposed Leakage-Free Benchmark**| `research_upgrade/tables/proposed_leakage_free_benchmark_992.csv` | 425 KB | 992 prompts with 8 near-duplicate prompts isolated. | Verified (992 prompts) |
| **4K Benchmark Generations** | `outputs/controlled_1000/benchmark_generations_.csv` | 2.50 MB | Exactly 4,000 generated outputs across 4 models (1,000 each). | Verified (4,000 rows) |

---

## 2. Checkpoint & Adapter Inventory

| Model Identifier | Base Architecture | Adapter / Weights Path | Parameters | Verified Config |
| :--- | :--- | :--- | :---: | :--- |
| **HingGPT** | GPT-2 (124M) | HuggingFace Hub weights | 124 M | Full fine-tuning baseline |
| **Phi-3.5-mini** | Microsoft Phi-3.5-mini-instruct | `models/phi35_mini_cpt/checkpoint-17340/` | 3.8 B | QLoRA $r=8, \alpha=16$ |
| **Qwen2.5-3B** | Qwen2.5-3B-Instruct | `models/qwen25_3b_cpt/checkpoint-17340/` | 3.09 B | QLoRA $r=8, \alpha=16$ |
| **Qwen2.5-7B** | Qwen2.5-7B-Instruct | HuggingFace Hub / Local cache | 7.61 B | QLoRA $r=8, \alpha=16$ |

---

## 3. Automated Judge & Evaluation Outputs

| Evaluation Asset | Relative Path | Verified Records | Findings & Key Takeaways |
| :--- | :--- | :---: | :--- |
| **Mistral-7B Primary Judge** | `outputs/independent_judge_1000/independent_mistral_judge__FINAL.csv` | 3,990 valid, 10 invalid | Qwen-3B overall: 3.56 ± 1.08; Qwen-7B overall: 3.17 ± 1.14 |
| **OLMo-2-1B Judge (Failed)** | `outputs/independent_judge_1000/independent_olmo2_1b_judge__CORRECTED_FINAL.csv` | 3,999 records | Model collapse on traceback strings; negative reliability |
| **Dual Judge Checkpoint** | `research_upgrade/tables/judge_qwen25_3b_4000_results.jsonl` | 488 scored (486 valid, 2 invalid) | Stronger Qwen2.5-3B-Instruct judge checkpointed at 12.2% |
| **Das & Gambäck CMI** | `research_upgrade/tables/das_gamback_cmi_lid_4000.csv` | 4,000 responses | Language CMI: HingGPT 15.15%, Phi 22.24%, 3B 16.29%, 7B 14.28% |
| **Bits-per-Character (BPC)** | `research_upgrade/tables/table_bits_per_character_evaluation.csv` | 4 models | 7B leads compression (1.689 BPC); 3B (1.815 BPC) |
| **Equal-Length Diversity** | `research_upgrade/tables/table_equal_length_distinct_n.csv` | 4 models ($K=15, 25$) | 7B achieves Distinct-1 = 0.852 at K=25; 3B = 0.817 |

---

## 4. Verified Human Evaluation Assets

| Asset Name | Relative Path | Records | Status |
| :--- | :--- | :---: | :---: |
| **Primary Human Ratings** | `research_upgrade/tables/human_ratings_annotator_a_500.csv` | Exactly 500 | **100% Completed & Verified** |
| **Annotator A CSV Export** | `research_upgrade/human_validation/annotator_A_ratings.csv` | 500 rows | 500 Completed, 0 Pending |
| **Annotator A Sheet** | `research_upgrade/human_validation/annotator_A_rating_sheet.csv` | 500 rows | All 500 pre-filled |
| **Annotator A Pending** | `research_upgrade/human_validation/annotator_A_pending_ratings.csv` | 0 rows | 0 Remaining |
| **Human Validation Summary**| `research_upgrade/tables/table_human_evaluation_500_summary.csv` | 5 rows | Mean, Std, Median across dimensions |
| **Database Store** | `research_upgrade/human_validation/ratings.db` | 500 rows for A | SQLite WAL mode, zero nulls |
| **Annotator B Protected Archive** | `research_upgrade/archive/annotator_b/` | 15 rows | Preserved in snapshot, partner disabled |
