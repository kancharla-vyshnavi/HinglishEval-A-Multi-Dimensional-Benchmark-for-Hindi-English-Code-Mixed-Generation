# HinglishEval: A Multi-Dimensional Benchmark for Hindi-English Code-Mixed Generation

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)

**HinglishEval** is a research project for evaluating large language models on Hindi-English code-mixed (Hinglish) generation. It combines controlled benchmarking, QLoRA-based continued pretraining, independent LLM judges, human evaluation, statistical analysis, robustness testing, error analysis, linguistic metrics, and a Hinglish chatbot.

## Table of Contents

1. [Overview](#1-overview)
2. [Research Objectives](#2-research-objectives)
3. [Dataset and Benchmark](#3-dataset-and-benchmark)
4. [Models and Training](#4-models-and-training)
5. [Research Pipeline](#5-research-pipeline)
6. [Evaluation Dimensions](#6-evaluation-dimensions)
7. [Independent LLM Judges](#7-independent-llm-judges)
8. [Inter-Judge Reliability](#8-inter-judge-reliability)
9. [Human Evaluation](#9-human-evaluation)
10. [Statistical Analysis](#10-statistical-analysis)
11. [Robustness Evaluation](#11-robustness-evaluation)
12. [Error Analysis](#12-error-analysis)
13. [Hinglish Linguistic Metrics](#13-hinglish-linguistic-metrics)
14. [Automatic Evaluation](#14-automatic-evaluation)
15. [New Research Figures](#15-new-research-figures)
16. [Publication Tables](#16-publication-tables)
17. [Repository Structure](#17-repository-structure)
18. [Installation](#18-installation)
19. [Running the Chatbot](#19-running-the-chatbot)
20. [Reproducibility](#20-reproducibility)
21. [Key Findings](#21-key-findings)
22. [Limitations](#22-limitations)
23. [Research Outputs](#23-research-outputs)
24. [Research Paper](#24-research-paper)
25. [License](#25-license)

---

## 1. Overview

Hindi-English code-mixing is common in everyday conversations and digital communication. Conventional text-generation metrics alone cannot fully capture the quality of Hinglish responses.

HinglishEval provides a controlled framework for comparing generated responses across linguistic quality, prompt adherence, evaluator reliability, robustness, and Hinglish-specific characteristics.

The project includes:

- A cleaned and deduplicated Hinglish corpus.
- QLoRA-based continued pretraining of four generation models.
- A 1,000-prompt controlled benchmark.
- 4,000 controlled model generations.
- Independent Mistral and Qwen evaluation.
- Human calibration and inter-annotator analysis.
- Statistical significance testing.
- Evaluator robustness experiments.
- E1–E10 error analysis.
- Code-Mixing Index and lexical analysis.
- Publication tables and research figures.
- A Hinglish chatbot.

## 2. Research Objectives

The objectives are to:

1. Compare four language models on controlled Hinglish prompts.
2. Evaluate six dimensions of response quality.
3. Measure agreement between independent LLM judges.
4. Compare automated judgments with human ratings.
5. Study the effects of rubric perturbations on evaluation.
6. Identify recurring generation errors.
7. Analyze code-mixing and lexical characteristics.
8. Apply appropriate statistical tests and multiple-comparison corrections.
9. Preserve research artifacts for reproducibility.
10. Build a practical Hinglish chatbot using an adapted language model.

## 3. Dataset and Benchmark

The project uses the L3Cube-HingCorpus / Natural Hinglish Corpus.

| Dataset component | Reported count |
|---|---:|
| Training examples | 277,431 |
| Validation examples | 14,601 |
| Original benchmark prompts | 1,000 |
| Quarantined moderate near-duplicates | 8 |
| Proposed leakage-filtered subset | 992 |
| Controlled generations | 4,000 |

The original benchmark contains 1,000 prompts, with 1,000 generations from each of four models. A separate contamination audit identified eight moderate near-duplicates and produced a proposed leakage-filtered subset of 992 prompts.

The 1,000-prompt experiment and 992-prompt subset are different artifacts and must not be treated as interchangeable.

Key files:

```text
data/
├── benchmarks/
│   └── hinglish_bench_1000.csv
└── processed/
    └── cpt/
        └── validation.jsonl

research_upgrade/
└── tables/
    └── proposed_leakage_free_benchmark_992.csv

outputs/
└── controlled_1000/
    ├── benchmark_generations_1000.csv
    ├── benchmark_generations_1000.jsonl
    └── generation_config_1000.json
```

## 4. Models and Training

Four generation models were evaluated.

| Model | Role |
|---|---|
| HingGPT | Hinglish-specialized generation |
| Phi-3.5-mini | Compact general-purpose language model |
| Qwen2.5-3B | Multilingual language model |
| Qwen2.5-7B | Higher-capacity multilingual language model |

### QLoRA continued pretraining

The project used QLoRA-based continued pretraining on the prepared Hinglish corpus.

The reported checkpoint identifier is `checkpoint-17340`.

```text
models/
├── hinggpt_cpt/
│   └── checkpoint-17340/
├── phi35_mini_cpt/
│   └── checkpoint-17340/
├── qwen25_3b_cpt/
│   └── checkpoint-17340/
└── qwen25_7b_cpt/
    └── checkpoint-17340/
```

Model weights and checkpoint files are large artifacts. Do not commit them to a public Git repository without reviewing their size, licensing, and distribution requirements.

## 5. Research Pipeline

```text
Natural Hinglish Corpus
          |
          v
Data Cleaning and Deduplication
          |
          v
Train / Validation Preparation
          |
          v
QLoRA Continued Pretraining
          |
          v
Four Adapted Generation Models
          |
          v
1,000-Prompt Controlled Benchmark
          |
          v
4,000 Generated Responses
          |
          v
Mistral-7B and Qwen2.5-3B Judges
          |
          v
Inter-Judge Reliability
          |
          v
Human Evaluation and Calibration
          |
          v
Robustness and Statistical Analysis
          |
          v
E1-E10 Error Analysis
          |
          v
Hinglish Linguistic Metrics
          |
          v
Research Tables and Figures
          |
          v
Research Paper and Chatbot
```

## 6. Evaluation Dimensions

Each response is rated on a 1–5 scale across six dimensions.

| Dimension | Description |
|---|---|
| Fluency | Readability and linguistic flow |
| Code-Mixing Naturalness | Naturalness of Hindi-English switching |
| Hindi Grammar | Grammatical correctness |
| Prompt Adherence | Compliance with the requested task |
| Spelling Consistency | Consistency of spelling and transliteration |
| Overall Quality | Holistic response quality |

These dimensions are complementary. A fluent response may still fail to follow the prompt or may use unnatural code-switching.

## 7. Independent LLM Judges

### Primary judge: Mistral-7B-Instruct-v0.3

| Audit item | Reported count |
|---|---:|
| Records processed | 4,000 |
| Valid judgments | 3,990 |
| Invalid or empty judgments | 10 |

### Cross-validation judge: Qwen2.5-3B-Instruct

| Audit item | Reported count |
|---|---:|
| Records processed | 4,000 |
| Valid judgments | 3,996 |
| Invalid judgments | 4 |
| Missing records | 0 |
| Duplicate IDs | 0 |

The reported matched valid overlap between the two active judges is **N = 3,986**.

### Excluded evaluator: OLMo-2-1B-Instruct

The audit identified a failure mode involving 970 Python traceback outputs that received passing scores. OLMo-2-1B is excluded from valid judge comparisons. Its failure logs should be preserved for transparent reporting and reproducibility.

### API judges

GPT-4o-mini and Claude-3.5-Haiku were marked **NOT RUN** because API access was unavailable. No results are claimed for these evaluators.

## 8. Inter-Judge Reliability

The reported comparison uses the exact matched valid records from Mistral-7B and Qwen2.5-3B-Instruct.

| Dimension | QWK | Spearman rho |
|---|---:|---:|
| Prompt Adherence | 0.499 | +0.474 |
| Overall Quality | 0.435 | +0.445 |
| Hindi Grammar | 0.418 | +0.443 |
| Fluency | 0.392 | +0.442 |
| Code-Mixing Naturalness | 0.357 | +0.391 |
| Spelling Consistency | 0.205 | +0.243 |

QWK measures ordinal rating agreement, while Spearman correlation measures similarity in ranking.

The results indicate positive rank association but imperfect agreement. Spelling Consistency has the lowest reported agreement.

Mistral-7B is the primary headline judge. Qwen2.5-3B-Instruct is used for cross-validation, with its shared model lineage relative to two generation models acknowledged as a potential limitation.

## 9. Human Evaluation

Human evaluation complements automated judging through a 500-item calibration subset and a reported 4,000-item double-annotation effort.

### Human calibration results

| Metric | Reported value |
|---|---:|
| Calibration subset | 500 items |
| Spearman rho | 0.184 |
| Quadratic Weighted Kappa | 0.169 |
| Mistral Overall Quality bias | +0.098 |
| Reported 95% bias confidence interval | [-0.036, +0.232] |

The reported human correlation is weak. The small signed bias estimate does not support a claim of uniform judge leniency across all dimensions.

### Double annotation

The project reports 4,000 paired items and 8,000 total ratings. Analyses include exact agreement, within-one-point agreement, QWK, and ordinal Krippendorff's alpha.

The reported agreement results are mixed, including negative ordinal agreement coefficients in some analyses. These should be reported transparently rather than characterized as strong reliability.

Possible annotation fatigue or scale-compression effects should be treated as hypotheses unless further analysis establishes their contribution.

Human rating databases and personal annotation sheets should not be published without appropriate privacy review.

## 10. Statistical Analysis

The statistical tests were selected according to the experimental design.

### Repeated-measures benchmark

The four generation models share benchmark prompts. The reported analysis includes:

- Friedman repeated-measures tests.
- Paired Wilcoxon signed-rank tests.
- Holm correction for multiple comparisons.
- Effect-size analysis.
- Bootstrap confidence intervals where available.

The reported complete-block sample size is N = 990.

### Human calibration comparison

For the reported human comparison with largely disjoint prompt sets, independent two-sided Mann–Whitney U tests with Holm correction were used.

The reported Qwen2.5-3B versus Qwen2.5-7B Overall Quality comparison was:

| Statistic | Reported result |
|---|---:|
| Mean difference | +0.224 |
| Raw p-value | 0.0671 |
| Holm-adjusted p-value | 0.1341 |

This human comparison is not statistically significant after correction. It does not establish that Qwen2.5-3B is superior to Qwen2.5-7B in human-rated Overall Quality.

## 11. Robustness Evaluation

The robustness experiment investigates whether perturbing the evaluation rubric changes Mistral's judgments.

Reported audit counts:

| Audit item | Count |
|---|---:|
| Total rows | 4,000 |
| Valid judgments | 3,989 |
| Invalid or missing judgments | 11 |

The analysis includes original-versus-perturbed score changes, rank stability, agreement, and model-level sensitivity.

Robustness results should be interpreted according to the perturbation design and the magnitude and consistency of the changes.

## 12. Error Analysis

The project uses an E1–E10 taxonomy to identify recurring generation errors.

| Code | Error type | Count | Percentage |
|---|---|---:|---:|
| E1 | English-dominant output | 61 | 1.5% |
| E2 | Hindi-dominant output | 648 | 16.2% |
| E3 | Unnatural code-switching | 26 | 0.7% |
| E4 | Grammatical error | 284 | 7.1% |
| E5 | Repetition | 242 | 6.0% |
| E6 | Prompt misunderstanding | 1,045 | 26.1% |
| E7 | Incomplete response | 679 | 17.0% |
| E8 | Spelling/transliteration error | 865 | 21.6% |
| E9 | Hallucination/factual error | 0 | 0.0% |
| E10 | Irrelevant response | 485 | 12.1% |

The most frequently detected categories include prompt misunderstanding, spelling/transliteration errors, and incomplete responses.

**Important:** E9 = 0 means that the automated detector flagged zero cases. It does not prove that the models produced no hallucinations or factual errors.

These counts identify observed output patterns; they do not prove the causes of those patterns.

## 13. Hinglish Linguistic Metrics

The linguistic analysis includes:

- English lexical share.
- Hindi lexical share.
- Code-Mixing Index (CMI).
- Presence of both languages.
- Model-level lexical characteristics.
- Response-level linguistic characteristics.

CMI is treated as a heuristic indicator of lexical mixing, not a perfect language-identification system.

Reported output locations:

```text
outputs/
└── hinglish_metrics/
    ├── code_mixing_index.csv
    ├── code_mixing_summary.csv
    ├── model_level_hinglish_metrics.csv
    └── response_level_hinglish_metrics.csv
```

## 14. Automatic Evaluation

A separate larger automatic evaluation was reported for an approximately 17K-example evaluation set. It is distinct from the 1,000-prompt controlled judge benchmark.

| Model | Perplexity | Distinct-1 | Distinct-2 | Repetition rate |
|---|---:|---:|---:|---:|
| HingGPT | 171.2320 | 0.0777 | 0.4055 | 0.4358 |
| Phi-3.5-mini | 50.7891 | 0.2021 | 0.7509 | 0.0040 |
| Qwen2.5-3B | 74.0219 | 0.2569 | 0.7778 | 0.0545 |
| Qwen2.5-7B | 55.1290 | 0.3401 | 0.8532 | 0.0332 |

These metrics measure different properties. Lower perplexity or repetition and higher lexical diversity do not independently establish better response quality.

A separate diagnostic perplexity experiment reported 100-sequence results of 154.97 for the base model, 187.97 for the instruct model, and 57.78 for the CPT model. Full validation CPT perplexity was reported as 74.02 over 14,601 sequences. These results should not be conflated with the 17K automatic evaluation.

## 15. New Research Figures

The following are the **new figure files reported in the project history**. The Markdown image links below use their observed filenames; verify the paths against the current repository before publishing.

### Figure 1 — Human versus Mistral Judge Comparison

![Human versus Mistral judge comparison](research_upgrade/figures/fig3_human_vs_mistral_judge_comparison.png)

### Figure 2 — Code-Mixing Distribution

![Code-mixing distribution](research_upgrade/figures/fig4_das_gamback_cmi_distribution.png)

### Figure 3 — Compression and Lexical Diversity

![Compression and lexical diversity](research_upgrade/figures/fig5_compression_and_lexical_diversity.png)

### Figure 4 — E1–E10 Error Taxonomy

![E1-E10 error taxonomy](research_upgrade/figures/fig6_e1_e10_error_taxonomy_breakdown.png)

### Figure 5 — Robustness Perturbation Degradation

![Robustness perturbation degradation](research_upgrade/figures/fig7_robustness_perturbation_degradation.png)

### Figure 6 — Data Leakage and Jaccard Overlap

![Data leakage and Jaccard overlap](research_upgrade/figures/fig8_data_leakage_jaccard_overlap.png)

### Additional publication figures

The project also reports a separate publication figure set under:

```text
research_upgrade/figures/final_publication_figures/
```

Use the actual filenames in that directory for any additional images. Do not link a nonexistent image path or use an older figure in place of a new one.

## 16. Publication Tables

The reported publication tables are stored under:

```text
research_upgrade/tables/final_publication_tables/
```

They cover:

1. Dataset and benchmark summary.
2. Model adaptation setup.
3. Evaluation dimensions and rubric.
4. Evaluator validity and coverage.
5. Per-model Mistral performance.
6. Pairwise model comparisons.
7. Human calibration.
8. Friedman tests.
9. Human inter-annotator agreement.
10. Excluded and failed judgments.

Verify the actual files before assuming every table is present.

## 17. Repository Structure

The following is a representative structure. Additional files may exist in the repository.

```text
HinglishEval/
├── README.md
├── paper.md
├── .gitignore
├── chatbot/
│   ├── app.py
│   └── chatbot.py
├── data/
│   ├── benchmarks/
│   └── processed/
├── models/
├── outputs/
│   ├── controlled_1000/
│   ├── independent_judge_1000/
│   ├── robustness_mistral_1000/
│   ├── error_analysis/
│   ├── hinglish_metrics/
│   └── final_charts/
├── research_upgrade/
│   ├── human_validation/
│   ├── scripts/
│   ├── tables/
│   ├── figures/
│   └── paper/
└── src/
    ├── evaluation/
    └── metrics/
```

Large model weights, credentials, private annotation databases, personal rating sheets, and sensitive backups should be excluded from public GitHub unless explicitly reviewed and approved for release.

## 18. Installation

The reported development environment uses Python 3.11 and a virtual environment named `.venv311`.

From the project root in Windows PowerShell:

```powershell
py -3.11 -m venv .venv311
.\.venv311\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If the project uses `new_requirements.txt` instead, inspect it and install the appropriate dependency set:

```powershell
pip install -r new_requirements.txt
```

Do not install conflicting dependency files blindly. Verify PyTorch, CUDA, Transformers, and PEFT versions against the environment used for the experiments.

## 19. Running the Chatbot

If `chatbot/app.py` is the configured entry point:

```powershell
.\.venv311\Scripts\Activate.ps1
python chatbot/app.py
```

Run the command from the project root. Follow the model paths and dependencies configured in the actual application.

The chatbot is an application built on top of the research project, not an additional benchmark result unless evaluated separately.

## 20. Reproducibility

Reproduction requires the appropriate dataset, model checkpoints, generation configurations, judge prompts, valid/invalid judgment flags, analysis scripts, and dependency versions.

Reported scripts include:

```text
research_upgrade/scripts/
├── run_qwen_judge_evaluation.py
├── validate_qwen_judge_status.py
├── generate_scientific_tables_and_figures.py
├── audit_everything.py
├── audit_paper_consistency.py
└── audit_data_overlap.py
```

Additional scripts reported in the project include:

```text
validate_paper_results.py
analyze_agreement.py
```

Check the current repository before running any script. Historical test reports should not be described as newly executed tests unless they have been rerun.

## 21. Key Findings

The reported findings support several cautious conclusions:

- Hinglish generation quality is multidimensional.
- The two active judges show positive rank correlations but imperfect agreement.
- Spelling consistency is a particularly challenging dimension for inter-judge agreement.
- Human-versus-Mistral alignment is weak in the reported calibration subset.
- Robustness experiments examine the sensitivity of scores to rubric changes.
- Prompt misunderstanding and spelling/transliteration errors are frequent detected error categories.
- Statistical conclusions depend on the experimental design and correction for multiple comparisons.
- The human comparison does not establish a statistically significant Overall Quality advantage for Qwen2.5-3B over Qwen2.5-7B.

Qwen2.5-3B should not be described as universally superior based only on automated mean scores. The conclusion must reflect the relevant judge, dimension, human evaluation, and statistical uncertainty.

## 22. Limitations

The project has several limitations:

- The benchmark does not represent every form of Hinglish communication.
- LLM judges may disagree with one another and with human annotators.
- Human inter-annotator agreement is imperfect.
- Rubric perturbations can change evaluator scores.
- Automated error detection may miss context-dependent mistakes.
- Zero automatically detected hallucinations does not establish their absence.
- CMI is a heuristic rather than a perfect language-identification method.
- Perplexity and lexical diversity do not fully capture response quality.
- The Qwen judge shares model lineage with two generation models, creating a potential evaluation bias.
- API-based evaluators were not run because access was unavailable.
- Observed model differences do not establish causal effects of architecture, parameter count, or training data.

## 23. Research Outputs

The project reports these major artifacts:

- Cleaned Hinglish corpus.
- Training and validation splits.
- QLoRA continued-pretraining checkpoints.
- Original 1,000-prompt benchmark.
- Proposed 992-prompt leakage-filtered subset.
- 4,000 controlled generations.
- Mistral and Qwen judge evaluations.
- Inter-judge reliability analysis.
- Human calibration and agreement analysis.
- Robustness evaluation.
- Statistical comparisons and effect sizes.
- E1–E10 error analysis.
- Hinglish linguistic metrics.
- Automatic evaluation outputs.
- Publication tables and figures.
- Research manuscript.
- Hinglish chatbot.

Confirm each artifact's current status and availability in the repository before claiming it is included in a public release.

## 24. Research Paper

The research manuscript is maintained in [`paper.md`](paper.md).

It documents the methodology, benchmark construction, controlled generation, judge evaluation, reliability, robustness, human evaluation, statistical analysis, error patterns, linguistic metrics, and limitations.

Before submission, verify that every reported number matches the final analysis files and that the paper, README, figures, captions, and tables use consistent sample sizes and statistical claims.

## 25. License

The project is intended to use the MIT License. Confirm that a `LICENSE` file exists and contains the correct license text before claiming that the repository has been formally released under MIT.

---

**HinglishEval — A Multi-Dimensional Benchmark for Hindi-English Code-Mixed Generation**

A research framework for systematic and reproducible evaluation of Hinglish generation.
