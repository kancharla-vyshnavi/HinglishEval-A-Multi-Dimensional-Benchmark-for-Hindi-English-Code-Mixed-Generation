# HinglishEval Complete Project Audit Report

**Audit Date:** 2026-10-13  
**Auditor:** Antigravity AI Research Agent  
**Repository:** `https://github.com/kancharla-vyshnavi/A-Multi-Dimensional-Benchmark-of-LLMs-for-Hindi-English-Code-Mixed-Generation`  
**Working Directory:** `c:\Users\vyshu\OneDrive\Desktop\HinglishLLM`  

---

## Executive Summary

This comprehensive audit evaluates the integrity, reproducibility, statistical validity, and documentation quality of the research project **"HinglishEval: A Multi-Dimensional Benchmark for Hindi-English Code-Mixed Generation."** 

Every claim, script, configuration file, checkpoint, dataset partition, and result in the repository has been directly inspected and cross-referenced against active project files. The findings are categorized into five rigorous classifications:
1. **Verified** (Empirically substantiated and mathematically consistent)
2. **Inconsistent** (Direct contradiction between paper text, code configurations, or generated tables)
3. **Missing / Methodologically Flawed** (Omitted components or flawed experimental designs requiring correction)
4. **Blocked** (Constrained by hardware, quota, or compute limitations, requiring principled alternatives)
5. **Requiring Human Validation** (Inherently subjective assessments that must be deferred to human annotators)

---

## 1. Verified Findings

- **[Verified] Dataset Record Counts:**
  - Training dataset: Exactly **277,431** sequences verified in `C:\Users\vyshu\Downloads\train.jsonl`.
  - Validation pool: Exactly **14,601** cleaned sequences verified in `data\processed\cpt\validation.jsonl`.
  - Benchmark prompts: Exactly **1,000** unique prompts verified in `data\benchmarks\hinglish_bench_.csv`.
  - Controlled generation outputs: Exactly **4,000** model responses (1,000 per model) verified in `outputs\controlled_1000\benchmark_generations_.csv`.

- **[Verified] Evaluator Sample Sizes & Complete Cases:**
  - Mistral-7B-Instruct-v0.3 completed 3,990 valid judgments (10 invalid JSON parses due to trailing truncation).
  - OLMo-2-0425-1B-Instruct completed 3,999 valid judgments (1 invalid parse).
  - Paired complete-case overlap without imputation: Exactly **3,989 matched pairs** ($995$ HingGPT, $1,000$ Phi-3.5-mini, $994$ Qwen2.5-3B, $1,000$ Qwen2.5-7B).

- **[Verified] Benchmark vs Training Data Overlap (Data Leakage Audit):**
  - Cross-referencing all 1,000 benchmark prompts against all 277,431 training lines reveals:
    - **Exact String Duplicates:** **0** (0.00%).
    - **Case-Insensitive Exact Matches:** **0** (0.00%).
    - **Normalized Alphanumeric Matches:** **0** (0.00%).
    - **High Near-Duplicates (Token Jaccard $\ge 0.90$):** **0** (0.00%).
    - **Moderate Near-Duplicates ($0.80 \le \text{Jaccard} < 0.90$):** **102** training rows corresponding to **8** distinct benchmark prompts (**0.80%** of benchmark).
  - *Integrity Note:* Original datasets and benchmark files are preserved unmodified. The 8 affected prompts are documented in `research_upgrade/tables/benchmark_train_overlap_matches.csv` and disclosed in the leakage report.

- **[Verified] Numerical Alignment in Baseline Tables:**
  - **Table 3 (Overall Model Performance):** Means and standard deviations in `paper.md` match `outputs/final_research_tables/table_3_overall_model_performance.csv` across all models (HingGPT: Mistral $1.990 \pm 0.951$, OLMo $4.182 \pm 0.613$, Combined $3.086 \pm 0.574$; Phi-3.5-mini: Mistral $1.027 \pm 0.242$, OLMo $4.894 \pm 0.336$, Combined $2.960 \pm 0.207$; Qwen2.5-3B: Mistral $3.563 \pm 1.081$, OLMo $4.011 \pm 0.727$, Combined $3.787 \pm 0.641$; Qwen2.5-7B: Mistral $3.173 \pm 1.139$, OLMo $3.956 \pm 0.712$, Combined $3.564 \pm 0.722$).
  - **Table 5 (Inter-Judge Reliability):** QWK and Spearman rho values in `paper.md` match `outputs/reliability_1000_FINAL/final_inter_judge_reliability_summary.csv` (Fluency: $\kappa_w = -0.142, \rho = -0.265$; Code-Mixing: $\kappa_w = -0.139, \rho = -0.311$; Grammar: $\kappa_w = 0.008, \rho = 0.017$; Adherence: $\kappa_w = -0.110, \rho = -0.279$; Spelling: $\kappa_w = -0.166, \rho = -0.281$; Overall: $\kappa_w = -0.108, \rho = -0.341$).
  - **Table 6 (Mistral Robustness Under Perturbation):** Original means, perturbed means, signed shifts, and Spearman correlations in `paper.md` match `outputs/robustness_mistral_1000_analysis/robustness_summary.csv`.
  - **Table 7 (Pairwise Wilcoxon Hypothesis Testing):** Test statistics $W$, raw $p$-values, Holm-adjusted $p$-values, effect sizes $r_{rb}$, and 95% bootstrap intervals match `outputs/statistical_analysis_1000_FINAL/final_wilcoxon_pairwise_holm.csv`.
  - **Table 8 (Automated Error Taxonomy E1–E10):** Frequency distributions across all 4,000 generations match `outputs/final_research_tables/table_8_error_analysis_e1_e10.csv`.
  - **Table 9 (Linguistic Characteristics):** Lexical CMI percentages match `outputs/final_research_tables/table_9_hinglish_linguistic_metrics.csv` (HingGPT: 19.07%, Phi-3.5-mini: 15.71%, Qwen2.5-3B: 15.63%, Qwen2.5-7B: 13.73%).

---

## 2. Inconsistent Findings (Discrepancies Requiring Reconciliation)

| # | Item / Location | Claimed in Paper (`paper.md`) | Actual Value in Checkpoints / Code | Impact & Reconciliation Action |
| :---: | :--- | :--- | :--- | :--- |
| **1** | **QLoRA LoRA Rank ($r$) and Scaling Alpha ($\alpha$)** (`paper.md` Section 4, Line 62) | Claimed: *"All CPT models were adapted using QLoRA ($r = 16, \alpha = 32$, 4-bit NormalFloat quantization)"* | **Actual:** `adapter_config.json` across **all four checkpoints** (`hinggpt_277k_cpt`, `phi35_mini_final_17340`, `qwen25_3b_cpt`, `qwen25_7b_cpt`) has **$r = 8, \alpha = 16$**. | **Critical.** Paper text directly misrepresents model architecture. Must update paper text to report actual $r=8, \alpha=16$, and report $r \in \{8, 16, 64\}$ in the ablation study. |
| **2** | **Phi-3.5-mini Base Architecture** (`paper.md` Section 4, Line 58) | Described as adapting compact foundation model *"Phi-3.5-mini"*. | **Actual:** `adapter_config.json` specifies `base_model_name_or_path: "microsoft/Phi-3.5-mini-instruct"`. | **Major.** Phi-3.5 was adapted from the instruction-tuned checkpoint, not the base unaligned model. Clarify in paper methodology. |
| **3** | **Table 4 Standard Deviations** (`paper.md` Table 4 vs `outputs/final_research_tables/table_4_dimension_wise_performance.csv`) | Discrepancy in standard deviations for all dimensions (e.g., Fluency HingGPT: paper states $\pm 0.536$, CSV has $\pm 0.557$; Qwen2.5-3B Fluency: paper states $\pm 0.730$, CSV has $\pm 0.526$). | In `table_4_dimension_wise_performance.csv`, Combined SD is computed as the standard deviation of $(S_{\text{Mistral}} + S_{\text{OLMo}})/2$. Paper text appears to have used an alternative pooled formula. | **Moderate.** Regenerate Table 4 directly from the underlying CSV source of truth with explicit documentation of standard deviation formulas. |
| **4** | **Script Filename Inconsistencies** (`src/final_project_validation.py`) | Script checks for `outputs\controlled_1000\benchmark_generations_1000.csv` and `independent_mistral_judge_1000_FINAL.csv`. | Disk files are named `benchmark_generations_.csv` and `independent_mistral_judge__FINAL.csv`. | **Minor.** Preserve original files; document filename alias map in `PROJECT_INVENTORY.md`. |
| **5** | **Duplicated Model Checkpoints** (`models/` vs `data/model/`) | Both directories exist with identical nested QLoRA checkpoints. | `models/` contains identical safetensors and configs copied from `data/model/`. | **Minor.** Maintain `data/model/` as canonical source of truth; preserve existing structure. |

---

## 3. Missing or Methodologically Flawed Elements

- **[Critical Flaw] OLMo-2-1B Judge Breakdown & Negative Inter-Judge Reliability:**
  - OLMo-2-0425-1B-Instruct exhibits severe ceiling compression (overall mean $4.261 \pm 0.704$, with 80.5% of ratings being 4 or 5).
  - Most critically, OLMo-2-1B awarded scores $\ge 3$ to **970 crashed generations** containing explicit Python tracebacks (`[GENERATION_ERROR] AttributeError...`).
  - Consequently, inter-judge correlation between Mistral-7B and OLMo-2-1B was **negative** across almost all dimensions (Overall $\kappa_w = -0.108, \rho = -0.341$).
  - *Methodological Consequence:* Averaging Mistral-7B and OLMo-2-1B into a single "Combined Mean" without validation distorts model evaluation. For publication quality, OLMo-2-1B must be flagged as defective, and a stronger, calibrated judge must be deployed with explicit few-shot anchors and JSON validation.

- **[Missing] 17K Automatic Evaluation in Paper Draft:**
  - The 17K automatic evaluation (`outputs/17k_automatic_evaluation_trained_models.csv`) measures Perplexity, Distinct-1, Distinct-2, and Repetition Rate across all 4 CPT models.
  - While highlighted in `README.md` (Section 14) and visual charts, this entire experiment is omitted from `paper.md`. It must be integrated into Section 7.

- **[Methodological Flaw] Heuristic Code-Mixing Index vs Standard CMI:**
  - The baseline repository calculated CMI using simple character/script regex heuristics (`outputs/hinglish_metrics/calculate_code_mixing.py`).
  - This does not conform to the peer-reviewed **Das & Gambäck (2014)** or **Gambäck & Das (2016)** standard CMI, which requires token-level language identification (LID).
  - *Upgrade:* Replaced with standard Das & Gambäck CMI using token-level language identification via `l3cube-pune/hing-bert-lid`.

- **[Methodological Flaw] Uncontrolled Distinct-n and Repetition Rates:**
  - In the baseline evaluation, Distinct-1 and Distinct-2 were calculated over variable-length generations. Longer sequences naturally dilute token diversity ratios.
  - *Upgrade:* Implemented equal-length truncation ($K \in \{15, 25\}$ tokens) to ensure rigorous cross-model comparability.

- **[Methodological Flaw] Bits-per-Character (BPC) vs Perplexity:**
  - Raw perplexity cannot be directly compared across architectures with drastically different tokenizer vocabularies (e.g. HingGPT vocabulary $\approx 30\text{k}$ vs Qwen2.5 vocabulary $\approx 152\text{k}$).
  - *Upgrade:* Derived and evaluated Bits-per-Character ($\text{BPC} = \frac{\ln(\text{PPL})}{\ln(2) \cdot r_{\text{char}}}$) using token-to-character compression ratios.

- **[Missing] Verifiable Academic Citations:**
  - `paper.md` contains only **7 references**.
  - A publication-ready submission requires at least **25 verified, genuine academic citations** covering code-switching corpora (GLUECoS, LinCE, PHINC, L3Cube-HingCorpus), LLM-as-a-judge frameworks (MT-Bench, G-Eval), parameter-efficient fine-tuning (LoRA, QLoRA), and foundation model technical reports.

- **[Missing] Genuine Dataset Examples in Paper:**
  - `paper.md` lacks genuine, verified prompt-response pairs drawn directly from the 4,000 benchmark generations.
  - At least 5 authentic examples must be included with full linguistic annotations and source verification.

- **[Data Organization Flaw] Training File External Location:**
  - `train.jsonl` resides at `C:\Users\vyshu\Downloads\train.jsonl`, outside the git workspace. While intact and verified, this creates reproducibility friction for external collaborators.

---

## 4. Blocked Elements & Principled Alternatives

| Proposed Task | Identified Blocker | Impact | Adopted Principled Alternative |
| :--- | :--- | :--- | :--- |
| **Frontier Cloud Judge (GPT-4o, Claude 3.5, Qwen2.5-72B)** | No API keys configured in environment; 72B local inference requires $\ge 40$ GB VRAM (host has 6.0 GB VRAM). | Cannot run 70B+ model locally or via cloud without external keys. | Deployed **`Qwen/Qwen2.5-3B-Instruct`** in 4-bit NF4 as secondary judge alongside retained **`Mistral-7B-Instruct-v0.3`**, utilizing 12 carefully calibrated few-shot anchors (2 per dimension) and strict JSON schema validation. |
| **Full 17,340-Step LoRA Retraining Ablations** | Retraining across $r \in \{8, 16, 64\}$ and seq lengths $\{128, 512\}$ requires $>100$ GPU compute hours on a laptop GPU (thermal throttling and runtime limits). | Cannot retrain full models from scratch within workstation budget. | Conducted exact parameter, optimizer state, and memory scaling modeling ($r \in \{8, 16, 64\}$), paired with empirical validation cross-entropy loss, perplexity, and throughput evaluation of Base vs Instruct vs CPT on the validation corpus. |

---

## 5. Items Requiring Human Validation (MUST BE LAST)

- **[Deferred to Final Phase] Human Evaluation Study (300 Sampled Responses):**
  - Sampling frame: 300 responses stratified across 4 models (75 per model) and discourse categories.
  - Manual annotation must be performed by 3 native Hinglish bilingual speakers using a 1–5 Likert rubric.
  - Agreement must be evaluated via Krippendorff’s $\alpha$ (ordinal weighting) and pairwise QWK.
  - **Critical Rule:** No human scores will be simulated or fabricated. All preparatory materials (rating CSV, Google Form specification, seed sampling script) are completed and held ready for manual human annotation.

- **[Deferred to Final Phase] Validation of E1–E10 Error Detectors:**
  - Precision, recall, and F1 scores of automated heuristic detectors can only be validated against human ground truth.
  - Currently documented as objective deterministic rule-based indicators, not ground truth.

- **[Deferred to Final Phase] Definitive Model Winner Selection:**
  - While Qwen2.5-3B achieves higher observed judge scores than Qwen2.5-7B, final declaration of the benchmark winner remains **provisional** until human preference verification is completed.

---

## 6. Audit Verdict & Feasibility Sign-Off

The project data, checkpoints, and benchmark outputs are intact, verified, and free of catastrophic data leakage (0.00% exact matches). The foundational methodology is sound, but requires critical adjustments for publication quality:
1. Reconcile QLoRA hyperparameter claims ($r=8$ vs $r=16$).
2. Replace or isolate defective OLMo-2-1B judgments and establish reliable dual-judge calibration with Qwen2.5-3B-Instruct.
3. Integrate standard Das & Gambäck CMI, Bits-per-Character, and length-controlled diversity metrics.
4. Expand paper references from 7 to $\ge 25$ verified citations and embed 5 verified dataset examples.
5. Provide a complete, fully transparent disclosure of limitations, evaluator divergence, and provisional claims pending human evaluation.
