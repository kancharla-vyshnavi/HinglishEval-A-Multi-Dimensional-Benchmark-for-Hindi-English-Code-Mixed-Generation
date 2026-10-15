# Final Comprehensive Completion and Scientific Verification Report

**Project Title:** HinglishEval: A Multi-Dimensional Benchmark for Hindi-English Code-Mixed Generation  
**Corpus / Repository:** `kancharla-vyshnavi/A-Multi-Dimensional-Benchmark-of-LLMs-for-Hindi-English-Code-Mixed-Generation`  
**Execution Environment:** Windows 11, NVIDIA GeForce RTX 4050 Laptop GPU (6.0 GB VRAM), Python 3.11  
**Master Output Directory:** `research_upgrade/v3/`  
**Verification Date:** 2026-10-14  

---

## 1. Task-by-Task Implementation Status

| Task ID & Scope | Implementation Status | Key Evidence / Primary Deliverable |
| :--- | :---: | :--- |
| **Task 1: Correct Human-Rating Statistics** | `COMPLETED` | `tables/human_pairwise_tests.csv`, `reports/human_statistics_report.md` |
| **Task 2: Judge Evaluation & Calibration Status** | `COMPLETED` | `configs/judge_config.json`, `reports/judge_cost_estimate.md`, `tables/judge_human_alignment.csv` |
| **Task 3: Real Baselines & Perplexity Discrepancy** | `COMPLETED` | `reports/perplexity_discrepancy_report.md`, `tables/base_instruct_cpt_comparison.csv`, `tables/lora_ablation_results.csv` |
| **Task 4: Recompute Mistral Evaluator Bias** | `COMPLETED` | `tables/mistral_human_bias_by_model_dimension.csv`, `figures/human_vs_mistral_bias.png`, `reports/mistral_bias_report.md` |
| **Task 5: Generation Prompt & Chat Template Diagnostic** | `COMPLETED` | `reports/training_inference_format_audit.md`, `reports/benchmark_construct_validity_report.md`, `tables/prompt_format_diagnostic.csv` |
| **Task 6: Independence, Disclosure & Annotation Sheets** | `COMPLETED` | `data/second_rater_annotation_sheet_100.csv`, `data/author_test_retest_sheet_100.csv`, `reports/annotation_independence_and_disclosure.md` |
| **Task 7: Bibliographic Verification (30 References)** | `COMPLETED` | `references/references_audit.csv`, `references/verified_references.bib`, `reports/reference_audit_report.md` |
| **Task 8: Canonical Tables, Figures & Automated Validator** | `COMPLETED` | `scripts/validate_paper_results.py`, `paper/hinglisheval_paper.md`, `reports/paper_consistency_report.md` |

---

## 2. What Actually Changed in the Research Project

1. **Overturned Erroneous Superiority Claims:**
   - Previous drafts claimed Qwen2.5-3B "decisively outperformed" and was "statistically superior" to Qwen2.5-7B based on an uncorrected directional test ($p = 0.0335$).
   - Corrected two-sided Mann-Whitney $U$ test with Holm-Bonferroni family-wise error rate correction yields $U = 8808.0$, raw $p = 0.0671$, and adjusted $p_{\text{adj}} = 0.1341 > 0.05$.
   - The paper's core thesis was updated to distinguish **practical compute/VRAM efficiency** ($2.07$ GB vs $4.65$ GB VRAM) from statistically proven human preference.

2. **Debunked Blanket "+0.85 Mistral Leniency Bias":**
   - Recalculation across all 500 matched human ratings revealed that Mistral-7B's mean Overall Quality bias is only **$+0.098$ points** (95% CI $[-0.036, +0.232]$).
   - The earlier $+0.85$ claim arose from conflating Spelling Consistency ($+0.842$) with Overall Quality. Mistral is actually strict on Hindi Grammar ($-0.534$).

3. **Reconciled Validation Perplexity Discrepancy (57.78 vs 74.02):**
   - Forensic audit proved that **74.02** is the perplexity evaluated across the full 14,601-sequence validation split (loss 4.3043).
   - **57.78** is the perplexity evaluated on the 100-sequence diagnostic ablation slice (loss 4.0566).
   - Pre-CPT base perplexity was 154.97 (a 62.7% reduction achieved via CPT).

4. **Identified Root Cause of `owitzuser` and Prompt Echoing:**
   - Base Causal LMs (`Qwen-Base`, `HingGPT`) were forced into ChatML wrappers without turn-ending stopping criteria (`<|im_end|>`, `<|end|>`), causing BPE tokenizer subword fragmentation (`owitz` + `user`), repetitive loops (Phi-3.5 prompt echoing), and safety refusals (12% in Qwen-7B).

5. **Exposed and Rectified Corrupted Bibliography Entries:**
   - L3Cube-HingCorpus: Replaced corrupted "Joshi, Goel, & Joshi" with official authors **Ravindra Nayak and Raviraj Joshi** (WILDRE-6 at LREC 2022).
   - PHINC: Replaced "V. Singh (2021) in WMT" with **Vivek Srivastava and Mayank Singh** (W-NUT 2020 at EMNLP).
   - QLoRA: Corrected publication year to **NeurIPS 2023**.

6. **Restored Missing Dimensions & Disclosed Single-Annotator Status:**
   - Spelling Consistency restored across all tables and figures.
   - Transparently disclosed that the 500 human ratings were produced solely by the primary author (Annotator A); staged blinded 100-item sheets for independent second-rater validation and author test-retest.

---

## 3. Exact Output Paths

### Reports
- `research_upgrade/v3/reports/human_statistics_report.md`
- `research_upgrade/v3/reports/judge_cost_estimate.md`
- `research_upgrade/v3/reports/judge_evaluation_report.md`
- `research_upgrade/v3/reports/perplexity_discrepancy_report.md`
- `research_upgrade/v3/reports/baseline_and_ablation_report.md`
- `research_upgrade/v3/reports/mistral_bias_report.md`
- `research_upgrade/v3/reports/training_inference_format_audit.md`
- `research_upgrade/v3/reports/benchmark_construct_validity_report.md`
- `research_upgrade/v3/reports/annotation_independence_and_disclosure.md`
- `research_upgrade/v3/reports/reference_audit_report.md`
- `research_upgrade/v3/reports/paper_consistency_report.md`

### Tables
- `research_upgrade/v3/tables/canonical_human_ratings_summary.csv`
- `research_upgrade/v3/tables/human_pairwise_tests.csv`
- `research_upgrade/v3/tables/human_pairwise_effect_sizes.csv`
- `research_upgrade/v3/tables/human_bootstrap_confidence_intervals.csv`
- `research_upgrade/v3/tables/human_power_analysis.csv`
- `research_upgrade/v3/tables/judge_human_alignment.csv`
- `research_upgrade/v3/tables/judge_alignment_confidence_intervals.csv`
- `research_upgrade/v3/tables/base_instruct_cpt_comparison.csv`
- `research_upgrade/v3/tables/base_instruct_cpt_paired_tests.csv`
- `research_upgrade/v3/tables/lora_ablation_results.csv`
- `research_upgrade/v3/tables/lora_ablation_paired_tests.csv`
- `research_upgrade/v3/tables/mistral_human_bias_by_model_dimension.csv`
- `research_upgrade/v3/tables/mistral_human_correlation_metrics.csv`
- `research_upgrade/v3/tables/mistral_human_bias_confidence_intervals.csv`
- `research_upgrade/v3/tables/canonical_benchmark_summary_992.csv`
- `research_upgrade/v3/tables/canonical_data_leakage_audit.csv`
- `research_upgrade/v3/tables/canonical_model_selection_comparison.csv`

### Figures (300 DPI Publication-Ready)
- `research_upgrade/v3/figures/human_evaluation_six_dimensions.png`
- `research_upgrade/v3/figures/human_vs_mistral_bias.png`
- `research_upgrade/v3/figures/linguistic_and_diversity_metrics.png`
- `research_upgrade/v3/figures/error_taxonomy_e1_e10.png`
- `research_upgrade/v3/figures/cpt_perplexity_and_rank_ablation.png`
- `research_upgrade/v3/figures/prompt_format_comparison.png`

### Data & Annotation Sheets
- `research_upgrade/v3/data/second_rater_annotation_sheet_100.csv`
- `research_upgrade/v3/data/author_test_retest_sheet_100.csv`
- `research_upgrade/v3/data/annotation_id_mapping.csv`
- `research_upgrade/v3/data/judge_dry_run_results.jsonl`

### References & Paper
- `research_upgrade/v3/references/references_audit.csv`
- `research_upgrade/v3/references/verified_references.bib`
- `research_upgrade/v3/paper/hinglisheval_paper.md`
- `research_upgrade/v3/CHANGELOG.md`
- `research_upgrade/v3/PROGRESS_LOG.md`

---

## 4. Key Verified Numerical Findings

1. **Human Evaluation Ratings (Mean & 95% Bootstrap CI):**
   - **Qwen2.5-3B:** Fluency $2.912$ `[2.712, 3.120]`, Code-Mixing $2.664$ `[2.456, 2.872]`, Hindi Grammar $2.904$ `[2.704, 3.104]`, Prompt Adherence $2.568$ `[2.352, 2.784]`, Spelling $2.800$ `[2.592, 3.008]`, Overall Quality $2.704$ `[2.440, 2.968]`.
   - **Qwen2.5-7B:** Fluency $2.720$, Code-Mixing $2.488$, Hindi Grammar $2.624$, Prompt Adherence $2.472$, Spelling $2.552$, Overall Quality $2.480$ `[2.240, 2.728]`.
   - **Phi-3.5-mini:** Overall Quality $2.112$ `[1.928, 2.296]`.
   - **HingGPT:** Overall Quality $2.192$ `[1.968, 2.424]`.
2. **Two-Sided Mann-Whitney U Pairwise Comparisons on Overall Quality:**
   - Qwen2.5-3B vs Qwen2.5-7B: $U = 8808.0$, raw $p = 0.0671$, Holm $p_{\text{adj}} = 0.1341$ (**Not Significant**).
   - Qwen2.5-3B vs HingGPT: $U = 9884.0$, raw $p = 1.49 \times 10^{-4}$, Holm $p_{\text{adj}} = 5.96 \times 10^{-4}$ (**Significant**).
   - Qwen2.5-3B vs Phi-3.5-mini: $U = 10072.0$, raw $p = 1.89 \times 10^{-5}$, Holm $p_{\text{adj}} = 9.44 \times 10^{-5}$ (**Significant**).
3. **Information-Theoretic Compression & Diversity (992 Leakage-Free Responses):**
   - Bits-per-Character (BPC): Qwen2.5-3B ($1.482$), Qwen2.5-7B ($1.498$), Phi-3.5-mini ($1.842$), HingGPT ($2.415$).
   - Distinct-2: Qwen2.5-3B ($0.781$), Qwen2.5-7B ($0.764$), HingGPT ($0.548$), Phi-3.5-mini ($0.512$).
   - Mean CMI: Qwen2.5-3B ($28.45\%$), Qwen2.5-7B ($27.12\%$), Phi-3.5-mini ($19.34\%$), HingGPT ($15.62\%$).
4. **Mistral-7B Bias Metrics across 500 Matched Responses:**
   - Overall Quality: $+0.098$ points (Spearman $\rho = +0.1837$, $p < 0.001$, $\kappa_w = 0.1691$).
   - Spelling Consistency: $+0.842$ points (lenient).
   - Hindi Grammar: $-0.534$ points (strict).

---

## 5. Claims Reversed or Weakened

| Previous Claim in Earlier Drafts | Corrected Position in v3 Deliverables |
| :--- | :--- |
| "Qwen2.5-3B is statistically superior to Qwen2.5-7B" | **Reversed:** Difference is not statistically significant ($p_{\text{adj}} = 0.1341$). Selection is based on compute efficiency (2.07 GB vs 4.65 GB VRAM). |
| "Mistral-7B has a global +0.85 leniency bias" | **Reversed:** Overall Quality bias is only +0.098 points; leniency is confined to spelling (+0.842), offset by strict Hindi grammar scoring (-0.534). |
| "Qwen2.5-3B dual judge is 100% completed" | **Weakened to Partial:** Progress is verified at 488 / 4,000 items (12.20%). |
| "OLMo-2-1B provides reliable headline scoring" | **Reversed:** Collapses on corrupt text ($\kappa_w = -0.0135$), excluded from headline conclusions. |
| "AI Assistant acts as an Independent External Auditor" | **Retracted:** Clarified that AI assistant is a software execution tool under human author oversight. |

---

## 6. Commands and Verification Tests Executed

1. `recompute_human_statistics.py`: Two-sided Mann-Whitney U, Holm correction, 10,000 bootstrap CIs. (Exit 0)
2. `judge_api.py` (dry run): 20 items, token accounting, blinding, rubric few-shot prompts. (Exit 0)
3. `validate_judge_results.py`: Vectorized QWK, Kendall tau, Spearman rho across judges. (Exit 0)
4. `evaluate_baselines_and_ablations.py`: CPT loss reconciliation, LoRA rank modeling. (Exit 0)
5. `recompute_mistral_bias.py`: Dimension-wise bias recalculation, 300 DPI plot. (Exit 0)
6. `prepare_annotation_sheets.py`: 100-item stratified blind sheets, author test-retest. (Exit 0)
7. `analyze_inter_annotator_agreement.py --test`: Unit tests for Krippendorff's alpha and QWK. (Exit 0)
8. `audit_and_generate_references.py`: Bibliographic verification of all 30 citations. (Exit 0)
9. `generate_publication_figures_and_tables.py`: Single-source-of-truth tables and figures. (Exit 0)
10. `validate_paper_results.py`: End-to-end automated paper validator (19 passed, 0 failed). (Exit 0)

---

## 7. API Usage and Cost Audit

- **OpenAI GPT-4o-mini:** 20-item dry run completed successfully ($0.0038). Estimated cost for 4,000 items: **$0.76 USD**.
- **Anthropic Claude 3.5 Haiku:** 20-item dry run completed successfully ($0.0213). Estimated cost for 4,000 items: **$4.27 USD**.
- **Combined API Judge Cost:** **$5.03 USD** for the entire 4,000 benchmark dataset.
- In compliance with Non-Negotiable Rule 5 and Rule 7, the full 4,000 API run was dry-run and costed, but not automatically launched to avoid unapproved financial expenditure.

---

## 8. GPU Requirements and Experiments Run

- **Hardware:** NVIDIA GeForce RTX 4050 Laptop GPU (6.0 GB VRAM).
- **Execution:** All 4 models loaded in 4-bit QLoRA.
- Qwen2.5-3B consumes $2.07$ GB VRAM; Qwen2.5-7B consumes $4.65$ GB VRAM.
- Validation loss evaluated across full 14,601 validation split ($4.3043$, PPL 74.02) and diagnostic slice ($4.0566$, PPL 57.78).

---

## 9. Pending Annotations & External Dependencies

1. **Second Human Annotator:** The 100-item blinded sheet (`second_rater_annotation_sheet_100.csv`) is staged with clear 1–5 rubrics and instructions, awaiting an independent native bilingual annotator.
2. **Author Test-Retest:** The 100-item re-rating sheet (`author_test_retest_sheet_100.csv`) is staged for completion after a 1-to-2 week washout period.
3. **Full 4,000 API Run:** Configured and dry-run tested ($5.03 budget), awaiting user authorization.

---

## 10. Remaining Risks and Unresolved Discrepancies

- **Inter-annotator agreement** cannot be published until genuine second-rater scores are logged.
- **Dialectal Orthography:** Roman-script Hinglish lacks standardized spelling rules; spelling scores contain intrinsic linguistic ambiguity.
- **Single-Turn Limitation:** Benchmark measures single-turn generation rather than extended multi-turn dialogic interactions.

---

## 11. Reproduction Instructions

To reproduce all canonical tables, figures, statistical tests, and validation checks from scratch:
```bash
# 1. Activate Python virtual environment
.\.venv311\Scripts\activate

# 2. Run human statistics recomputation (Task 1)
python research_upgrade/v3/scripts/recompute_human_statistics.py

# 3. Run judge evaluation alignment (Task 2)
python research_upgrade/v3/scripts/validate_judge_results.py

# 4. Run baseline and ablation evaluation (Task 3)
python research_upgrade/v3/scripts/evaluate_baselines_and_ablations.py

# 5. Run Mistral bias recalculation (Task 4)
python research_upgrade/v3/scripts/recompute_mistral_bias.py

# 6. Generate annotation sheets and verify agreement tools (Task 6)
python research_upgrade/v3/scripts/prepare_annotation_sheets.py
python research_upgrade/v3/scripts/analyze_inter_annotator_agreement.py --test

# 7. Audit references and compile BibTeX (Task 7)
python research_upgrade/v3/scripts/audit_and_generate_references.py

# 8. Generate all canonical tables and 300 DPI figures (Task 8)
python research_upgrade/v3/scripts/generate_publication_figures_and_tables.py

# 9. Run automated paper consistency validator (Task 8)
python research_upgrade/v3/scripts/validate_paper_results.py
```

---

## 12. Publication-Readiness Verdict

### Verdict: **CONDITIONALLY READY FOR SUBMISSION**

**Evidence-Based Rationale:**
- **Why It Is Scientifically Ready Now:**
  1. The manuscript and canonical tables have undergone a complete statistical overhaul: two-sided tests, Holm-Bonferroni correction, and 10,000 bootstrap confidence intervals replace invalid uncorrected $p$-values.
  2. All contradictory claims ("statistical superiority", "100% COMPLETED", "+0.85 global bias") have been eliminated.
  3. The 992-item leakage-free benchmark is empirically isolated and documented.
  4. The 30 references are audited against authoritative academic databases (ACL, NeurIPS, IEEE, arXiv).
  5. The automated paper consistency checker (`validate_paper_results.py`) passes 19/19 checks with exit code 0.
- **Conditions Prior to Final Camera-Ready:**
  1. An independent second bilingual annotator completes the 100-item blinded sheet (`second_rater_annotation_sheet_100.csv`) so that inter-annotator agreement ($\alpha_{\text{ordinal}}, \kappa_w$) can be computed.
  2. The author completes the 100-item test-retest sheet after the 1-to-2 week washout period to report intra-annotator reliability.
  3. (Optional) Run the full $5.03 API judge evaluation if cloud budget is allocated.
