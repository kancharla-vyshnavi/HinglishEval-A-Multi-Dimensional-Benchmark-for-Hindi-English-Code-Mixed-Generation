# HinglishEval Research Upgrade v3: Master Progress Log

**Project:** HinglishEval: A Multi-Dimensional Benchmark for Hindi-English Code-Mixed Generation  
**Working Directory:** `c:\Users\vyshu\OneDrive\Desktop\HinglishLLM`  
**Output Root:** `research_upgrade/v3/`  
**Initialization Time:** 2026-10-14 02:24:00 IST  

---

## Workspace Setup & Initial Inventory

- **2026-10-14 02:23:36 IST** | `New-Item -ItemType Directory ...`  
  - Created directory tree: `scripts/`, `data/`, `tables/`, `figures/`, `reports/`, `paper/`, `references/`, `logs/`, `configs/`.
  - Exit code: 0. Status: COMPLETED.
- **2026-10-14 02:25:47 IST** | GPU & Environment Hardware Check:
  - NVIDIA GeForce RTX 4050 Laptop GPU (6.0 GB VRAM), CUDA available.
  - Exit code: 0. Status: COMPLETED.

---

## Task 1: Recompute Human-Rating Statistics (COMPLETED)

- **2026-10-14 02:30:49 IST** | `.\.venv311\Scripts\python.exe research_upgrade\v3\scripts\recompute_human_statistics.py`
  - Input: `research_upgrade\tables\human_ratings_annotator_a_500.csv` (500 ratings, 125 per model across 6 dimensions).
  - Test Design: Two-sided Mann-Whitney U test (independent samples; prompt overlap across models is only 13–23 prompts, 0 common to all 4).
  - Multiplicity: Holm-Bonferroni correction across 6 pairwise model comparisons per dimension.
  - Resampling: 10,000 bootstrap iterations (seed = 42).
  - Outputs Created:
    - `research_upgrade/v3/tables/human_pairwise_tests.csv`
    - `research_upgrade/v3/tables/human_pairwise_effect_sizes.csv`
    - `research_upgrade/v3/tables/human_bootstrap_confidence_intervals.csv`
    - `research_upgrade/v3/tables/human_power_analysis.csv`
    - `research_upgrade/v3/reports/human_statistics_report.md`
  - Critical Result & Correction:
    - Qwen2.5-3B vs Qwen2.5-7B on Overall Quality: $U = 8808.0$, raw two-sided $p = 0.0671$, Holm-adjusted $p_{\text{adj}} = 0.1341$ (**NOT statistically significant**, $p > 0.05$).
    - Overturns previous unsupported claim of 'statistically significant superiority' ($p = 0.0335$, which was an uncorrected one-sided p-value).
    - Model selection rationale updated: Qwen2.5-3B is favored for its $2.3\times$ lower VRAM footprint (2.05 GB vs 4.65 GB) and edge efficiency, not statistically confirmed human preference.
  - Exit code: 0. Status: COMPLETED.

---

## Task 2: Judge Evaluation and Honest Completion Status (COMPLETED)

- **2026-10-14 02:37:08 IST** | `.\.venv311\Scripts\python.exe research_upgrade\v3\scripts\judge_api.py`
  - Implementation: Dual independent API judge pipeline (OpenAI `gpt-4o-mini-2024-07-18` and Anthropic `claude-3-5-haiku-20241022`).
  - Model Blinding: Shuffled presentation with fixed seed 42; generator identities concealed.
  - Dry Run: 20-item stratified sample executed and schema-validated.
  - Token Accounting: Average 1,010 input tokens, 65 output tokens per item.
  - Cost Projections (4,000 items): GPT-4o-mini = $0.76 USD; Claude 3.5 Haiku = $4.27 USD; Combined = $5.03 USD.
  - Status Disclosure: Documented as BLOCKED / PREPARED awaiting API credentials; no scores fabricated.
  - Outputs Created:
    - `research_upgrade/v3/configs/judge_config.json`
    - `research_upgrade/v3/data/judge_dry_run_results.jsonl`
    - `research_upgrade/v3/reports/judge_cost_estimate.md`
  - Exit code: 0. Status: COMPLETED.

- **2026-10-14 02:40:34 IST** | `.\.venv311\Scripts\python.exe research_upgrade\v3\scripts\validate_judge_results.py`
  - Matched Calibration: 500 validated human responses vs Mistral-7B, OLMo-2-1B, and Qwen2.5-3B-Instruct.
  - Alignment Metrics: Spearman rho, Kendall tau, Quadratic Weighted Kappa, and 10,000-resample bootstrap 95% CIs.
  - Findings:
    - Mistral-7B is verified as the best-aligned independent judge ($\rho = +0.127$ to $+0.222$, all $p < 0.005$; Overall bias = $+0.098$ points).
    - OLMo-2-1B confirmed as collapsed (mean overall = 4.26/5.00, QWK = -0.0135); relegated to appendix.
    - Qwen2.5-3B-Instruct confirmed as PARTIAL (488 / 4,000 records on disk, 56 matched human ratings).
  - Outputs Created:
    - `research_upgrade/v3/tables/judge_human_alignment.csv`
    - `research_upgrade/v3/tables/judge_alignment_confidence_intervals.csv`
    - `research_upgrade/v3/reports/judge_evaluation_report.md`
  - Exit code: 0. Status: COMPLETED.

---

## Task 3: Real Baselines, Perplexity Reconciliation, and LoRA Ablations (COMPLETED)

- **2026-10-14 02:45:36 IST** | `.\.venv311\Scripts\python.exe research_upgrade\v3\scripts\evaluate_baselines_and_ablations.py`
  - Perplexity Discrepancy Reconciliation:
    - Resolved source of PPL = 74.0219 (evaluated across the entire 14,601-row held-out validation corpus during initial Colab training) vs PPL = 57.78 (evaluated on 100-sequence local forward-pass ablation slice).
    - Trainer state checkpoint at step 17,340 confirms eval_loss = 4.2114 nats ($\text{PPL} = 67.45$).
    - Documented both scopes precisely in `perplexity_discrepancy_report.md`.
  - Base vs Instruct vs CPT Empirical Validation (Qwen2.5-3B):
    - Base: Loss = 5.0432 nats, PPL = 154.97, 403.1 tok/s
    - Instruct: Loss = 5.2363 nats, PPL = 187.97, 440.5 tok/s
    - CPT: Loss = 4.0566 nats, PPL = 57.78, 335.1 tok/s (62.7% reduction in perplexity).
  - 992-Prompt Paired Wilcoxon Signed-Rank Benchmark Tests:
    - Qwen2.5-3B achieves statistically significant superiority over Qwen2.5-7B ($p_{\text{adj}} = 8.16 \times 10^{-13}$), HingGPT ($p_{\text{adj}} = 1.05 \times 10^{-83}$), and Phi-3.5-mini ($p_{\text{adj}} = 1.63 \times 10^{-132}$) on paired Mistral judge ratings.
  - LoRA Rank Scaling & Compute Disclosure:
    - Parameter scaling and AdamW memory modeling verified for $r \in \{8, 16, 64\}$.
    - Retraining from scratch for $r=16$ and $r=64$ is honestly documented as BLOCKED by compute budget (>100 GPU hours on host RTX 4050).
  - Outputs Created:
    - `research_upgrade/v3/tables/base_instruct_cpt_comparison.csv`
    - `research_upgrade/v3/tables/base_instruct_cpt_paired_tests.csv`
    - `research_upgrade/v3/tables/lora_ablation_results.csv`
    - `research_upgrade/v3/tables/lora_ablation_paired_tests.csv`
    - `research_upgrade/v3/reports/perplexity_discrepancy_report.md`
    - `research_upgrade/v3/reports/baseline_and_ablation_report.md`
  - Exit code: 0. Status: COMPLETED.

- **[2026-10-14T02:48:12+05:30] Task 4: Empirical Recalculation of Mistral-7B Bias**
  - Command: `.\.venv311\Scripts\python.exe research_upgrade\v3\scripts\recompute_mistral_bias.py`
  - Matched Sample: 500 validated human ratings (125 items per model across 4 models).
  - Key finding: Replaced invalid blanket "+0.85" claim. Overall Quality bias is only +0.098 points (95% CI [-0.036, +0.232]). Spelling Consistency has positive bias (+0.842), Hindi Grammar has negative bias (-0.534, stricter than human). All dimensions have positive rank correlation (Spearman rho +0.127 to +0.222, all p < 0.005).
  - Outputs generated:
    - `research_upgrade/v3/tables/mistral_human_bias_by_model_dimension.csv`
    - `research_upgrade/v3/tables/mistral_human_correlation_metrics.csv`
    - `research_upgrade/v3/tables/mistral_human_bias_confidence_intervals.csv`
    - `research_upgrade/v3/figures/human_vs_mistral_bias.png` (300 DPI publication figure)
    - `research_upgrade/v3/reports/mistral_bias_report.md`
  - Exit code: 0. Status: COMPLETED.

- **[2026-10-14T03:00:00+05:30] Task 5: Generation Prompt and Chat Template Forensic Audit**
  - Script: `research_upgrade/v3/scripts/diagnose_prompt_formats.py`
  - Forensic Findings:
    - `owitzuser` anomaly explained: Qwen token 52331 is "owitz" and token 872 is "user". Forcing ChatML `<|im_start|>` on Base Causal LMs without turn-ending stopping criteria caused BPE tokenizer subword splitting and multi-turn echoing.
    - Phi-3.5-mini prompt echoing (83%): Caused by omitting `<|end|>` (token ID 32007) from `eos_token_id`.
    - Safety refusals (12% in Qwen-7B): Out-of-distribution ChatML wrappers triggered embedded base safety templates.
  - Outputs generated:
    - `research_upgrade/v3/reports/training_inference_format_audit.md`
    - `research_upgrade/v3/reports/benchmark_construct_validity_report.md`
    - `research_upgrade/v3/tables/prompt_format_diagnostic.csv`
    - `research_upgrade/v3/figures/prompt_format_comparison.png`
  - Exit code: 0. Status: COMPLETED.

- **[2026-10-14T02:59:30+05:30] Task 6: Annotation Independence, Disclosure & Verification Protocols**
  - Scripts: `research_upgrade/v3/scripts/prepare_annotation_sheets.py`, `research_upgrade/v3/scripts/analyze_inter_annotator_agreement.py`
  - Disclosure: Stated unequivocally that all 500 completed ratings are from the primary author (Annotator A) and AI is a non-independent execution assistant. Staged 100-item blinded sheet and 100-item author test-retest sheet.
  - Unit tests executed: Isolated synthetic tests for Krippendorff's alpha (ordinal) and QWK passed (exit code 0).
  - Outputs generated:
    - `research_upgrade/v3/data/second_rater_annotation_sheet_100.csv` (100 items, 25 per model, 6 rubrics)
    - `research_upgrade/v3/data/author_test_retest_sheet_100.csv` (100 items, 25 per model)
    - `research_upgrade/v3/data/annotation_id_mapping.csv` (200 records mapping back to source IDs)
    - `research_upgrade/v3/reports/annotation_independence_and_disclosure.md`
  - Exit code: 0. Status: COMPLETED.

- **[2026-10-14T03:04:17+05:30] Task 7: Comprehensive Bibliographic Verification (30 References)**
  - Script: `research_upgrade/v3/scripts/audit_and_generate_references.py`
  - Discrepancies corrected against ACL Anthology, NeurIPS, IEEE, and arXiv:
    - L3Cube-HingCorpus: Replaced corrupted "Joshi, Goel, & Joshi" with official authors Ravindra Nayak & Raviraj Joshi (WILDRE-6 at LREC 2022).
    - PHINC: Replaced "V. Singh (2021) in WMT" with Vivek Srivastava & Mayank Singh (W-NUT 2020 at EMNLP).
    - QLoRA: Corrected publication year to NeurIPS 2023.
  - Outputs generated:
    - `research_upgrade/v3/references/references_audit.csv` (30 references audited)
    - `research_upgrade/v3/references/verified_references.bib` (Complete BibTeX entries)
    - `research_upgrade/v3/reports/reference_audit_report.md`
  - Exit code: 0. Status: COMPLETED.

- **[2026-10-14T03:12:50+05:30] Task 8: Canonical Results Tables, Figures, Paper Rewrite & Automated Validator**
  - Scripts: `research_upgrade/v3/scripts/generate_publication_figures_and_tables.py`, `research_upgrade/v3/scripts/validate_paper_results.py`
  - Outputs generated:
    - `research_upgrade/v3/tables/canonical_human_ratings_summary.csv`
    - `research_upgrade/v3/tables/canonical_benchmark_summary_992.csv`
    - `research_upgrade/v3/tables/canonical_data_leakage_audit.csv`
    - `research_upgrade/v3/tables/canonical_model_selection_comparison.csv`
    - `research_upgrade/v3/figures/human_evaluation_six_dimensions.png` (300 DPI publication figure)
    - `research_upgrade/v3/figures/linguistic_and_diversity_metrics.png` (300 DPI publication figure)
    - `research_upgrade/v3/figures/error_taxonomy_e1_e10.png` (300 DPI publication figure)
    - `research_upgrade/v3/figures/cpt_perplexity_and_rank_ablation.png` (300 DPI publication figure)
    - `research_upgrade/v3/paper/hinglisheval_paper.md` (Fully rewritten, calibrated research manuscript)
    - `research_upgrade/v3/reports/paper_consistency_report.md` (Automated validator: 19/19 checks passed)
    - `research_upgrade/v3/CHANGELOG.md`
    - `research_upgrade/v3/FINAL_COMPLETION_REPORT.md`
  - Automated Validator exit code: 0. Status: COMPLETED.
