# Automated Paper Consistency and Scientific Verification Report

**Execution Timestamp:** 2026-10-14  
**Checker Script:** `research_upgrade/v3/scripts/validate_paper_results.py`  
**Overall Status:** ALL CHECKS PASSED  

### Summary Statistics:
- **Total Verification Checks Passed:** 19
- **Total Verification Checks Failed:** 0
- **Warnings / Informational Notices:** 0

---

## 1. Verified Checks Log

| Category / Check Name | Verified Finding | Status |
| :--- | :--- | :---: |
| **Human Ratings Count** | Exactly 500 validated records present | `PASSED` |
| **Model Stratification** | All 4 models have exactly 125 ratings: {'Qwen2.5-7B': 125, 'Qwen2.5-3B': 125, 'Phi-3.5-mini': 125, 'HingGPT': 125} | `PASSED` |
| **Rating Dimensions** | All six required rating dimensions are present | `PASSED` |
| **Score Range Validity** | All ratings are strictly valid integers between 1 and 5 | `PASSED` |
| **Overall Quality Means** | Recomputed means strictly match canonical results: {'Qwen2.5-3B': 2.704, 'Qwen2.5-7B': 2.48, 'Phi-3.5-mini': 2.112, 'HingGPT': 2.192} | `PASSED` |
| **Qwen-3B vs 7B Statistical Test** | Holm-adjusted p = 0.1341 > 0.05. Statistical superiority is NOT supported. | `PASSED` |
| **Mistral Overall Bias** | Overall Quality bias correctly measured near zero (mean = 0.098), disproving global +0.85 claim | `PASSED` |
| **Leakage-Free Prompts Count** | Exactly 992 leakage-free prompts retained (8 moderate overlap excluded) | `PASSED` |
| **PPL Reconciliation** | Discrepancy fully reconciled (74.02 = full 14,601 val split; 57.78 = 100-sequence slice) | `PASSED` |
| **Audited Reference Count** | All 30 manuscript references audited | `PASSED` |
| **L3Cube-HingCorpus Authors** | Corrected to official authors: Ravindra Nayak & Raviraj Joshi (WILDRE-6 at LREC 2022) | `PASSED` |
| **PHINC Authors & Venue** | Corrected to Vivek Srivastava & Mayank Singh (W-NUT 2020 at EMNLP) | `PASSED` |
| **QLoRA Publication Year** | Corrected to NeurIPS 2023 | `PASSED` |
| **Figure human_evaluation_six_dimensions.png** | Present (156.2 KB) | `PASSED` |
| **Figure human_vs_mistral_bias.png** | Present (531.3 KB) | `PASSED` |
| **Figure linguistic_and_diversity_metrics.png** | Present (211.9 KB) | `PASSED` |
| **Figure error_taxonomy_e1_e10.png** | Present (200.0 KB) | `PASSED` |
| **Figure cpt_perplexity_and_rank_ablation.png** | Present (263.4 KB) | `PASSED` |
| **Prohibited Claims Scan** | Zero unrefuted prohibited claims found across new v3 reports and tables | `PASSED` |

---

## 3. Scope of Automated Verification

### What This Checker Explicitly Validates:
1. Exact match between raw CSV source ratings (500 items) and published statistical tables.
2. Two-sided Mann-Whitney U test results, Holm-Bonferroni correction, and power calculations.
3. Dimension-specific recalculation of Mistral evaluator bias, confirming the refutation of the +0.85 global bias claim.
4. Exact counts of the 992 leakage-free benchmark prompts and 8 excluded prompts.
5. Reconciliation of validation perplexity values (74.02 full split vs 57.78 ablation slice).
6. Comprehensive verification of all 30 bibliographic citations against official proceedings (ACL, NeurIPS, IEEE, arXiv).
7. Physical existence, non-emptiness, and formatting of all 300 DPI publication figures.
8. Rigorous automated scan preventing regression into unverified claims ('100% COMPLETED', 'decisively leads', etc.).

### What This Checker Cannot Validate (Human Prerequisites):
1. Subjective qualitative aesthetics of Hinglish code-switching in prose.
2. Genuine ratings from the pending second human annotator.
3. Test-retest ratings during the author's upcoming 1-to-2 week washout period.
