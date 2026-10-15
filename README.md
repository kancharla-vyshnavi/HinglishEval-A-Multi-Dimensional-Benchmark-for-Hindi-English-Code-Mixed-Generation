# HinglishEval: A Multi-Dimensional Benchmark for Hindi-English Code-Mixed Generation

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![Status: Research Complete](https://img.shields.io/badge/Status-Research%20Complete-success.svg)]()

A reproducible multi-dimensional benchmark for evaluating Large Language Models (LLMs) on **Hindi-English code-mixed (Hinglish) generation** across linguistic quality, prompt adherence, robustness, statistical significance, error patterns, and Hinglish-specific linguistic characteristics.

---

# 1. Research Objective & Motivation

Hindi-English code-mixed language is widely used in informal communication, social media, digital services, education, and everyday online interactions. However, conventional text-generation evaluation metrics do not fully capture the characteristics of code-mixed language.

This project develops a controlled evaluation framework for studying how different LLMs generate Hinglish and how their outputs differ across multiple quality dimensions.

The benchmark evaluates:

* **Fluency**
* **Code-mixing quality**
* **Hindi grammatical quality**
* **Prompt adherence**
* **Spelling / transliteration quality**
* **Overall response quality**
* **Evaluator robustness**
* **Error patterns**
* **Hinglish-specific linguistic characteristics**

The objective is not to reduce Hinglish generation quality to a single metric, but to provide a **multi-dimensional and statistically supported comparison framework**.

---

# 2. Models Evaluated

Four models were evaluated under the same controlled benchmark:

| Model            | Model Type           | Role                               |
| ---------------- | -------------------- | ---------------------------------- |
| **HingGPT**      | Hinglish-specialized | Domain-focused Hinglish generation |
| **Phi-3.5-mini** | General-purpose      | Compact instruction-tuned LLM      |
| **Qwen2.5-3B**   | General-purpose      | Multilingual LLM                   |
| **Qwen2.5-7B**   | General-purpose      | Higher-capacity multilingual LLM   |

The evaluation uses the same benchmark prompts and controlled generation procedure across all four models.

---

# 3. Dataset & Benchmark

The project uses a cleaned and deduplicated **Natural Hinglish Corpus** containing approximately **14,601 usable sequences** (`data/processed/cpt/validation.jsonl`).

### Benchmark Provenance & Contamination Audit
- **Original Benchmark Prompts:** **1,000 prompts** sampled deterministically (seed `42`) across conversational Hinglish genres (`data/benchmarks/hinglish_bench_.csv`).
- **Quarantined Near-Duplicates:** **8 prompts** with Jaccard 8-gram overlap $0.80 \le J < 0.90$ representing formulaic colloquial greetings.
- **Leakage-Filtered Benchmark Subset:** **992 prompts** confirmed strictly leakage-free ($J < 0.80$) against the 277k CPT training corpus (`research_upgrade/tables/proposed_leakage_free_benchmark_992.csv`).
- **Controlled Generator Outputs:** **4,000 generations** evaluated across the 1,000 original prompts across four models with nucleus decoding (temperature = 0.7, top-p = 0.9, max new tokens = 50, repetition penalty = 1.1).

## Benchmark Structure

| Field         | Description                           |
| ------------- | ------------------------------------- |
| `prompt_id`   | Unique benchmark prompt identifier    |
| `row_index`   | Source row reference                  |
| `prompt`      | Controlled Hinglish generation prompt |
| `source_text` | Corresponding source text             |

The benchmark is designed so that model outputs can be compared under identical prompt conditions.

---

# 4. Research Pipeline

The complete evaluation pipeline is:

```text
Natural Hinglish Corpus
        │
        ▼
Data Cleaning & Deduplication
        │
        ▼
Train / Validation Preparation
        │
        ▼
QLoRA Continued Pretraining (CPT)
        │
        ▼
CPT-Adapted Models
        │
        ▼
Hinglish-Bench
1,000 Controlled Prompts
        │
        ▼
4 Models × 1,000 Prompts
        │
        ▼
4,000 Controlled Generations
        │
        ├──────────────────────────────┐
        │                              │
        ▼                              ▼
Mistral-7B-Instruct-v0.3        Qwen2.5-3B-Instruct
Independent Judge 1             Independent Judge 2
        │                              │
        └──────────────┬───────────────┘
                       ▼
              Inter-Judge Reliability
               QWK + Spearman ρ
                       │
                       ▼
              Robustness Evaluation
              Perturbed Mistral Rubric
                       │
                       ▼
           Statistical Analysis
      Friedman + Wilcoxon + Holm
      Effect Sizes + Bootstrap CI
                       │
                       ▼
                Error Analysis
                  E1 – E10
                       │
                       ▼
         Hinglish Linguistic Metrics
                       │
                       ▼
         Final Tables + Figures
                       │
                       ▼
              Research Paper
                       │
                       ▼
              Hinglish Chatbot
```

---

> **Detailed Architectural Flowchart:** For the complete, interactive end-to-end flowchart across all six research stages, see [`research_upgrade/PROJECT_FLOWCHART.md`](research_upgrade/PROJECT_FLOWCHART.md).

# 5. Controlled Generation

The final benchmark produces **4,000 controlled generations**:

```text
1,000 prompts × 4 models = 4,000 generations
```

The main controlled-generation outputs are stored under:

```text
outputs/controlled_1000/
```

Primary files include:

```text
benchmark_generations_.csv
benchmark_generations_.jsonl
generation_config_.json
```

The benchmark uses the same prompts across all models to maintain controlled comparison conditions.

---

# 6. Independent LLM Evaluation

Two active open-weight instruction-tuned LLM judges were deployed:

## Judge 1 (Primary Headline Judge)
**Mistral-7B-Instruct-v0.3** (4-bit NF4):
- **4,000 records processed**
- **3,990 valid judgments** (10 unparsed/empty generations flagged and handled transparently)

## Judge 2 (Active Cross-Validation Judge)
**Qwen2.5-3B-Instruct** (4-bit NF4):
- **4,000 records processed**
- **3,996 valid judgments** (4 malformed generations preserved with `is_valid = False`; zero traceback text counted as scores)

## Excluded Evaluators & Failure Accounting
- **OLMo-2-1B-Instruct (Documented Failure Mode):** Excluded from valid judge comparisons. While it processed 4,000 records, it suffered catastrophic evaluation collapse—awarding passing scores to 970 Python crash tracebacks (`AttributeError: 'NoneType' object...`) and exhibiting extreme ceiling saturation (mean 4.26/5.00, negative human correlation $\kappa_w = -0.0135$). Its failure logs are preserved transparently for reproducibility.
- **Frontier API Judges (GPT-4o-mini & Claude-3.5-Haiku):** Designated as **NOT RUN / BLOCKED** due to unavailable paid API access (OpenAI account credit balance exhausted; Anthropic credentials absent). Zero paid API calls were executed, zero costs incurred ($0.00 reported spend), and zero API numbers fabricated.

The active judges evaluate generated responses across six core dimensions:
1. Fluency
2. Code-Mixing Naturalness
3. Hindi Grammar
4. Prompt Adherence
5. Spelling Consistency
6. Overall Quality

Scores use a **1–5 scale**.

---

# 7. Inter-Judge Reliability

Agreement between the two independent open-weight judges was evaluated on the **exact intersection of valid records ($N = 3,986$ matched pairs)**:

| Dimension | QWK | Spearman $\rho$ | $p$-value | Interpretation |
| :--- | :---: | :---: | :---: | :--- |
| **Prompt Adherence** | 0.499 | +0.474 | $4.76 \times 10^{-222}$ | Moderate Agreement |
| **Overall Quality** | 0.435 | +0.445 | $9.83 \times 10^{-193}$ | Moderate Agreement |
| **Hindi Grammar** | 0.418 | +0.443 | $1.20 \times 10^{-191}$ | Moderate Agreement |
| **Fluency** | 0.392 | +0.442 | $2.31 \times 10^{-190}$ | Fair-to-Moderate Agreement |
| **Code-Mixing Naturalness** | 0.357 | +0.391 | $4.51 \times 10^{-146}$ | Fair Agreement |
| **Spelling Consistency** | 0.205 | +0.243 | $7.76 \times 10^{-55}$ | Slight Agreement |

> **Methodological Note on Significance:** While all six dimensions achieve extreme statistical significance ($p < 10^{-54}$) demonstrating genuine non-random rank correlation, statistical significance alone does not imply complete consensus or human-level accuracy. Orthographic and transliteration variance (Spelling Consistency) remains the most divergent dimension between evaluators.

## Impact on Headline Model Results

Because inter-judge agreement varies across dimensions, the model-level scores reported in the headline performance tables should be interpreted as **evaluator-specific quality signals rather than definitive ground-truth quality scores**.

Both judges corroborate that **Qwen2.5-3B** achieves the highest overall rating under automated judging, followed by Qwen2.5-7B, HingGPT, and Phi-3.5-mini. However, because Qwen2.5-3B-Instruct shares model lineage with two evaluated generators, Mistral-7B serves as our primary independent headline judge to guard against intra-family bias.

# 8. Human Evaluation & Validation

To complement the automated LLM-judge evaluation, the project includes a human evaluation component to assess the quality of generated Hinglish responses across six dimensions.

## Evaluation Setup

- **Responses evaluated:** 500
- **Models covered:** HingGPT, Phi-3.5-mini, Qwen2.5-3B, and Qwen2.5-7B
- **Rating scale:** 1–5 for each dimension
- **Evaluation dimensions:** Fluency, Code-Mixing Naturalness, Hindi Grammar, Prompt Adherence, Spelling Consistency, and Overall Quality
- **Annotation datasets:**
  - **Calibrated 500-Item Expert Baseline:** Independently verified multi-model benchmark subset used for human-judge rank correlation and signed calibration offsets (disproving the uniform +0.85 leniency claim).
  - **Full-Scale 4,000-Item Double Annotation (`ratings_4000.db`):** Complete double-annotation by Annotator A (4,000 completed) and Annotator B (4,000 completed) across all six dimensions.

## Human Evaluation Dimensions

| Dimension | Description |
|---|---|
| Fluency | Naturalness and readability of the response |
| Code-Mixing Naturalness | Appropriateness of Hindi-English mixing |
| Hindi Grammar | Grammatical correctness of Hindi expressions |
| Prompt Adherence | How well the response follows the prompt |
| Spelling Consistency | Consistency of spelling and Romanized-Hindi transliteration |
| Overall Quality | Overall perceived response quality |

## Inter-Annotator Agreement & Findings

Double-annotation across all 4,000 items revealed:
- **Within-One-Point Agreement:** High across all dimensions (**80.0% to 92.4%**), confirming general consensus on broader quality bands.
- **Exact Agreement:** Moderate (**27.4% to 40.8%**).
- **Scale Compression & Negative Alpha:** Extreme concentration of ratings in scores 2 and 3 (>90% of all ratings) combined with session drift produces expected variance smaller than observed difference ($D_o > D_e$), resulting in negative ordinal Krippendorff's alpha ($-0.395$ to $-0.063$) and negative QWK ($-0.357$ to $-0.038$).
- **Methodological Takeaway:** Macro-scale human ratings in subjective code-mixed NLP suffer from annotator pacing fatigue and marginal scale compression. Automated judges provide reproducible comparative rankings when anchored by human-calibrated offsets.

---
# Evaluator Robustness

A robustness experiment evaluates whether changing the evaluation rubric affects the Mistral judge's scores.

The same 4,000 generated responses are evaluated under a **perturbed Mistral rubric**.

The analysis includes:

* Original vs perturbed mean scores
* Spearman correlation
* Weighted agreement
* Mean absolute score change
* Signed score change
* Model-level score changes
* Rank/order stability
* Bootstrap 95% confidence intervals

The robustness outputs are stored under:

```text
outputs/final_robustness/
```

The robustness analysis is important because the inter-judge disagreement indicates that evaluator behavior is itself a source of measurement variability.

---


# 9. Statistical Analysis

The statistical methodology strictly matches the experimental design of each evaluation setting:

## 1. Paired Benchmark Prompts (1,000 Prompts × 4 Models, N = 990 Complete Blocks)
Because all four generator models were evaluated on the exact same 1,000 prompts, observations are paired across models:
- **Friedman Repeated-Measures Omnibus Test:** Conducted across all four models on complete prompt blocks ($N = 990, \text{df} = 3$). Highly statistically significant across all six dimensions ($p < 10^{-128}$; Overall Quality $\chi^2 = 1862.01, p < 10^{-300}$).
- **Pairwise Paired Wilcoxon Signed-Rank Tests (Holm Corrected):**
  - Qwen2.5-3B vs Phi-3.5-mini: Mean Diff = +2.533, $W = 129.0$, Holm $p = 5.34 \times 10^{-159}$ (Significant)
  - Qwen2.5-7B vs Phi-3.5-mini: Mean Diff = +2.147, $W = 344.0$, Holm $p = 4.98 \times 10^{-148}$ (Significant)
  - Qwen2.5-3B vs HingGPT: Mean Diff = +1.570, $W = 20605.0$, Holm $p = 1.04 \times 10^{-113}$ (Significant)
  - HingGPT vs Phi-3.5-mini: Mean Diff = +0.964, $W = 3203.5$, Holm $p = 3.33 \times 10^{-99}$ (Significant)
  - Qwen2.5-7B vs HingGPT: Mean Diff = +1.184, $W = 38772.0$, Holm $p = 1.15 \times 10^{-84}$ (Significant)
  - Qwen2.5-3B vs Qwen2.5-7B: Mean Diff = +0.386, $W = 61828.0$, Holm $p = 1.43 \times 10^{-14}$ (Significant under Mistral-7B)

## 2. Human Evaluation Baseline (N = 500 Stratified Sample, 125 per Model)
In contrast to the repeated-measures benchmark, the human 500 baseline sampled prompts stratified across models (largely disjoint, with only 13–23 overlapping prompts between pairs).
- Therefore, **independent two-sided Mann-Whitney U tests** with Holm correction were appropriately applied.
- Under human evaluation, Qwen2.5-3B vs Qwen2.5-7B Overall Quality difference (+0.224 points) is **not statistically significant** ($U = 8808.0$, raw $p = 0.0671$, Holm $p_{\text{adj}} = 0.1341 > 0.05$).
- **Takeaway:** Qwen2.5-3B is recommended for edge deployments due to its **$2.3\times$ lower VRAM footprint (2.05 GB vs 4.65 GB)** and $2.2\times$ faster throughput, rather than proven human superiority.

---

# 10. Error Analysis: E1–E10

A structured error taxonomy is used to identify common failure patterns across the 4,000 controlled generations.

| Code    | Error Type                       |
| ------- | -------------------------------- |
| **E1**  | English-dominant output          |
| **E2**  | Hindi-dominant output            |
| **E3**  | Unnatural code-switching         |
| **E4**  | Grammatical error                |
| **E5**  | Repetition                       |
| **E6**  | Prompt misunderstanding          |
| **E7**  | Incomplete response              |
| **E8**  | Spelling / transliteration error |
| **E9**  | Hallucination / factual error    |
| **E10** | Irrelevant response              |

The automated analysis identified:

| Error | Count | Percentage |
| ----- | ----: | ---------: |
| E1    |    61 |       1.5% |
| E2    |   648 |      16.2% |
| E3    |    26 |       0.7% |
| E4    |   284 |       7.1% |
| E5    |   242 |       6.0% |
| E6    | 1,045 |      26.1% |
| E7    |   679 |      17.0% |
| E8    |   865 |      21.6% |
| E9    |     0 |       0.0% |
| E10   |   485 |      12.1% |

**Important:** E9 = 0 means that the automated detector flagged zero cases. It does **not** establish that the models produced no true hallucinations.

## 10.1 Why Are E6, E8, and E7 the Most Frequent?

The three most frequent detected categories were:

* **E6 Prompt misunderstanding — 26.1%**
* **E8 Spelling / transliteration error — 21.6%**
* **E7 Incomplete response — 17.0%**

These patterns suggest that a substantial portion of detected failures is concentrated around three aspects of Hinglish generation:

### E6 — Prompt Misunderstanding

E6 represents cases where the generated response does not adequately address the requested task or misses an important instruction.

In a code-mixed generation setting, this may appear as a response that produces text but does not correctly preserve the intended task, requested format, or conversational objective.

The observed frequency therefore highlights **instruction-following as an important failure pattern in the benchmark**.

However, E6 is an observed error category and does not by itself establish the underlying causal mechanism.

### E8 — Spelling / Transliteration Error

E8 captures spelling and Romanized-Hindi/transliteration inconsistencies.

Hinglish commonly uses Roman script for Hindi words, which introduces additional variation in spelling and transliteration.

For example, semantically similar Hindi expressions can have multiple Romanized forms. Consequently, inconsistent transliteration can affect automatic detection and perceived text quality even when the intended meaning remains understandable.

The high E8 frequency therefore highlights **orthographic and transliteration consistency as an important challenge for Hinglish generation**.

This should not be interpreted as proof that the underlying cause is a particular tokenizer, training-data property, or model architecture.

### E7 — Incomplete Response

E7 identifies responses that stop before adequately completing the requested task.

This pattern can affect prompt adherence and overall usefulness even when the generated text is grammatically acceptable.

The E7 frequency therefore indicates that **response completeness is another important failure pattern** in the evaluated generations.

Again, the taxonomy identifies an observed output pattern rather than proving why a generation stopped early.

## 10.2 Interpretation of Error Frequencies

The E1–E10 taxonomy identifies **observed error patterns rather than proven causal mechanisms**.

Therefore:

* E6 indicates observed prompt-following failures, not a definitive explanation of why they occurred.
* E8 indicates spelling/transliteration problems, not a proven data or tokenizer cause.
* E7 indicates incomplete outputs, not a proven decoding or generation-length cause.

The error analysis is therefore used to identify **where failures are concentrated**, while the research paper discusses possible interpretations without treating them as experimentally established causes.

Error-analysis outputs are stored under:

```text
outputs/error_analysis/
```

---

# 11. Hinglish-Specific Linguistic Analysis

The project includes additional linguistic analysis designed specifically for Hinglish generation.

The analysis covers:

* English lexical share
* Hindi lexical share
* Code-Mixing Index (CMI)
* Presence of both languages
* Model-level lexical characteristics
* Response-level Hinglish characteristics

The CMI is treated as a **transparent heuristic indicator** of lexical mixing rather than a perfect language-identification system.

Final metric outputs:

```text
outputs/hinglish_metrics/
```

Important files:

```text
code_mixing_index.csv
code_mixing_summary.csv
model_level_hinglish_metrics.csv
response_level_hinglish_metrics.csv
```

---

# 12. Qualitative Examples

Aggregate scores and error percentages provide quantitative evidence, but representative generations make the benchmark easier to interpret.

The qualitative section is intended to provide **side-by-side examples of strong and problematic generations** before the reader moves into the detailed research paper.

The examples should focus on the same prompt being evaluated across models or on representative outputs illustrating the major error categories.

## Example Categories

| Example Type                     | What to Inspect                                                                      |
| -------------------------------- | ------------------------------------------------------------------------------------ |
| Strong generation                | Natural Hinglish, appropriate code-mixing, clear prompt adherence, complete response |
| Prompt misunderstanding          | Response does not adequately address the requested task                              |
| Spelling / transliteration issue | Incorrect or inconsistent Romanized-Hindi spelling                                   |
| Incomplete response              | Response stops before fully addressing the prompt                                    |
| Unnatural code-switching         | Hindi-English switching is awkward or unnatural                                      |
| Grammatical error                | Hindi or mixed-language grammatical construction is problematic                      |

### Side-by-Side Example Format

| Prompt                            | Model          | Generation                  | Interpretation                                      |
| --------------------------------- | -------------- | --------------------------- | --------------------------------------------------- |
| *Representative benchmark prompt* | Selected model | *Representative generation* | Strong prompt adherence and natural Hinglish        |
| *Same / similar prompt*           | Another model  | *Representative generation* | Prompt misunderstanding or incomplete response      |
| *Representative benchmark prompt* | Selected model | *Representative generation* | Spelling/transliteration issue                      |
| *Representative benchmark prompt* | Another model  | *Representative generation* | More complete and contextually appropriate response |

> **Note:** Actual generation text should be taken directly from the controlled-generation output files. No synthetic or invented model outputs are used as research evidence.

These qualitative examples are **illustrative evidence** and are not treated as additional quantitative benchmark scores.

---

# 13. Final Publication Figures

All publication figures are available in both high-resolution PNG (300 DPI) and vector PDF format under:

```text
research_upgrade/figures/final_publication_figures/
```

| Figure | Filename | Description |
| :--- | :--- | :--- |
| **Figure 1** | `fig1_generator_model_comparison_grouped_bar.png` | Grouped bar chart comparing 4 models across 6 dimensions under Mistral-7B |
| **Figure 2** | `fig2_generator_model_dimension_heatmap.png` | Performance heatmap across six linguistic evaluation dimensions |
| **Figure 3** | `fig3_model_score_distributions_boxplots.png` | Boxplots of score distributions for Overall Quality |
| **Figure 4** | `fig4_judge_agreement_calibration_bias.png` | Dimension-specific signed bias (Mistral - Human) disproving uniform +0.85 claim |
| **Figure 5** | `fig5_human_vs_mistral_judge_rank_alignment.png` | Human expert vs Mistral-7B rank alignment scatter plot ($N = 500$) |
| **Figure 6** | `fig6_evaluator_validity_failure_breakdown.png` | Transparent evaluator validity and failure accounting (4,000 target responses) |
| **Figure 7** | `fig7_pairwise_model_statistical_forest_plot.png` | Pairwise architecture comparisons forest plot (Paired Wilcoxon, Holm corrected, $N = 990$) |

---

# 14. 17K Automatic Evaluation

A separate automatic evaluation was performed on a larger 17K evaluation dataset.

This evaluation is **separate from the 1,000-prompt benchmark and independent judge analysis**.

## Evaluation Rules

* Only the **`prompt`** column is used as model input.
* `source_text` is not used as model input.
* The trained/adapted checkpoints are evaluated.
* The original base models are not used as the evaluated systems.
* One response is generated per prompt for each model.
* Only four automatic metrics are reported.

## Metrics

1. Perplexity
2. Distinct-1
3. Distinct-2
4. Repetition Rate

## Results

| Model        | Perplexity | Distinct-1 | Distinct-2 | Repetition Rate |
| ------------ | ---------: | ---------: | ---------: | --------------: |
| HingGPT      |    171.232 |     0.0777 |     0.4055 |          0.4358 |
| Phi-3.5-mini |    50.7891 |     0.2021 |     0.7509 |          0.0040 |
| Qwen2.5-3B   |    74.0219 |     0.2569 |     0.7778 |          0.0545 |
| Qwen2.5-7B   |    55.1290 |     0.3401 |     0.8532 |          0.0332 |

These automatic metrics provide a complementary view of generation behavior.

In particular, lexical diversity and repetition should not be interpreted as direct substitutes for the multi-dimensional judge evaluation.

The 17K evaluation is therefore treated as a **separate automatic evaluation track** rather than merged into the judge scores.

## 17K Evaluation Figure

![17K Automatic Evaluation](outputs/final_charts/17k_automatic_evaluation_trained_models.png)

## 17K Evaluation Files

```text
outputs/17k_automatic_evaluation_trained_models.csv
outputs/17k_automatic_evaluation_trained_models.png
outputs/final_charts/17k_automatic_evaluation_trained_models.png
outputs/final_research_tables/table_17k_automatic_evaluation_trained_models.csv
src/generate_17k_automatic_evaluation.py
```

---

# 15. Final Publication Tables

The 10 publication-ready scientific tables generated from verified data are stored in:

```text
research_upgrade/tables/final_publication_tables/
```

| Table | CSV Filename | Description |
| :--- | :--- | :--- |
| **Table 1** | `table_1_dataset_benchmark_summary.csv` | Dataset, CPT corpus, benchmark prompts, and generation summary |
| **Table 2** | `table_2_model_adaptation_setup.csv` | Model architectures, parameter scales, LoRA adaptation, and VRAM footprints |
| **Table 3** | `table_3_evaluation_dimensions_rubric.csv` | Six evaluation dimensions, 1–5 Likert scoring anchors, and linguistic focus |
| **Table 4** | `table_4_evaluator_validity_and_coverage.csv` | Evaluator execution validity, coverage, invalid counts, and study roles |
| **Table 5** | `table_5_per_model_mistral_performance.csv` | Descriptive mean and standard deviation for each model across six dimensions |
| **Table 6** | `table_6_pairwise_model_comparisons.csv` | Pairwise paired Wilcoxon signed-rank tests, Cohen's d, and Holm correction ($N = 990$) |
| **Table 7** | `table_7_judge_human_calibration_500.csv` | Evaluator signed calibration bias, 95% bootstrap CIs, Spearman $\rho$, and QWK ($N = 500$) |
| **Table 8** | `table_8_friedman_omnibus_tests.csv` | Friedman repeated-measures non-parametric omnibus tests across four models |
| **Table 9** | `table_9_human_inter_annotator_agreement_4000.csv` | Human agreement: Exact %, $\pm 1$ %, QWK (95% CI), and Ordinal Alpha (95% CI) ($N = 4,000$) |
| **Table 10** | `table_10_excluded_and_failed_judgments.csv` | Transparent failure accounting, syntax errors, tracebacks, and exclusion rationales |

These tables provide structured machine-readable versions of the main research results.

---

# 16. Repository Structure

```text
HinglishLLM/
│
├── README.md
├── paper.md
├── .gitignore
│
├── chatbot/
│   ├── app.py
│   └── chatbot.py
│
├── configs/
│
├── data/
│   ├── benchmarks/
│   │   └── hinglish_bench_.csv
│   └── model/
│
├── models/
│
├── outputs/
│   ├── controlled_1000/
│   ├── independent_judge_1000/
│   ├── reliability_1000_FINAL/
│   ├── statistical_analysis_1000_FINAL/
│   ├── error_analysis/
│   ├── hinglish_metrics/
│   ├── final_charts/
│   ├── final_research_tables/
│   └── final_robustness/
│
└── src/
    ├── evaluation/
    ├── metrics/
    ├── run_final_inter_judge_reliability.py
    ├── run_final_statistical_analysis.py
    ├── run_olmo2_phi_repair.py
    └── generate_17k_automatic_evaluation.py
```

Large pretrained model weights and checkpoint files are excluded from normal Git tracking through `.gitignore` rules.

---

# 17. Reproducibility

The repository preserves the generated evaluation artifacts so that the final analysis can be inspected without regenerating all model outputs.

The main reproducibility components are:

```text
Benchmark
    ↓
Controlled generations
    ↓
Independent judges
    ↓
Reliability analysis
    ↓
Robustness analysis
    ↓
Statistical analysis
    ↓
Error analysis
    ↓
Hinglish metrics
    ↓
17K automatic evaluation
    ↓
Final tables & figures
```

The benchmark generation configuration is stored in:

```text
outputs/controlled_1000/generation_config_.json
```

---

# 18. Environment

The project was developed and evaluated using a Python/PyTorch environment with GPU acceleration.

The recorded environment includes:

```text
Python 3.11.x
PyTorch 2.14.0+cu132
Transformers 5.17.0
PEFT 0.21.0
CUDA-enabled GPU
```

A dependency snapshot is provided in:

```text
new_requirements.txt
```

Because model inference depends on GPU memory, CUDA compatibility, model checkpoints, and local hardware configuration, exact runtime behavior may vary across machines.

---

# 19. Hinglish Chatbot

The final project also contains a chatbot interface using a CPT-adapted model.

Chatbot files:

```text
chatbot/
├── app.py
└── chatbot.py
```

The chatbot uses a Qwen-based model with a PEFT adapter for Hinglish generation.

The chatbot is treated as an application layer built on top of the research pipeline rather than as an additional benchmark result.

---

# 20. Research Limitations

Several limitations should be considered when interpreting the results.

## Benchmark Coverage

Although the final benchmark contains 1,000 prompts, it cannot represent every form of Hindi-English code-mixed communication.

## Automated Judge Dependence

LLM-based evaluation depends on the behavior and rubric interpretation of the selected judges.

## Inter-Judge Disagreement

The independent judges show limited agreement on several dimensions.

Therefore, the two-judge composite and the headline model scores are treated as **evaluation signals under the defined judging setup**, rather than unquestionable ground-truth scores.

This is particularly relevant when interpreting Tables 3 and 4.

## Evaluator Robustness

The robustness experiment demonstrates that changes in rubric formulation can alter evaluator scores.

This indicates that evaluator design is an important component of the measurement process.

## Error Detector Limitations

Automated E1–E10 detection can miss subtle or context-dependent errors.

## E9 Interpretation

The absence of automatically detected E9 cases should not be interpreted as proof that no factual errors or hallucinations exist.

## CMI Limitation

The Code-Mixing Index is a heuristic linguistic measure and does not constitute perfect language identification.

## Causal Interpretation

Observed differences between models should not be interpreted as causal evidence for model architecture, parameter count, pretraining data, or specialization because the benchmark does not isolate individual causal factors experimentally.

---

# 21. Research Outputs

The project produces the following major outputs:

```text
✓ Cleaned Hinglish corpus
✓ 1,000-prompt Hinglish benchmark
✓ 4,000 controlled generations
✓ Independent Mistral-7B evaluation (4,000 records)
✓ Independent Qwen2.5-3B evaluation (4,000 records)
✓ Documented OLMo-2-1B failure analysis (970 tracebacks)
✓ Inter-judge reliability & human calibration analysis
✓ Evaluator robustness analysis
✓ Friedman statistical analysis
✓ Pairwise Wilcoxon + Holm correction
✓ Rank-biserial effect sizes
✓ Bootstrap confidence intervals
✓ E1–E10 automated error analysis
✓ Hinglish-specific linguistic metrics
✓ 10 publication-grade scientific tables
✓ 7 publication-quality figures (PNG & PDF)
✓ Separate 17K automatic evaluation
✓ Research paper
✓ Hinglish chatbot
```

---

# 22. Research Paper

The research manuscript associated with the project is available in:

```text
paper.md
```

The paper documents the methodology, benchmark construction, controlled generation process, independent evaluation, robustness analysis, statistical analysis, error analysis, Hinglish-specific findings, and model-level interpretation.

The paper provides the detailed methodological and analytical discussion, while this README provides a concise reproducibility-oriented overview.

---

# 23. License

This project is released under the **MIT License**.

See the repository license file for the complete license text.

---

# 24. Repository

GitHub repository:

**A Multi-Dimensional Benchmark of LLMs for Hindi-English Code-Mixed Generation**

https://github.com/kancharla-vyshnavi/A-Multi-Dimensional-Benchmark-of-LLMs-for-Hindi-English-Code-Mixed-Generation
