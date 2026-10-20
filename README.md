## HinglishEval: A Multi-Dimensional Benchmark for Hindi–English Code-Mixed Generation

<p align="center">
  <strong>Do Large Language Models Actually Write Natural Hinglish?</strong>
  <br />
  A systematic evaluation of fluency, code-mixing, Hindi grammar, prompt adherence, spelling consistency, and overall quality.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Task-Hinglish%20Generation-blue" alt="Task: Hinglish Generation" />
  <img src="https://img.shields.io/badge/Models-4-purple" alt="Four models" />
  <img src="https://img.shields.io/badge/Benchmark-1%2C000%20Prompts-orange" alt="1000 prompts" />
  <img src="https://img.shields.io/badge/Human%20Evaluation-2%20Annotators-green" alt="Two annotators" />
  <img src="https://img.shields.io/badge/Framework-PyTorch%20%7C%20Transformers-red" alt="PyTorch and Transformers" />
</p>

<p align="center">
  <a href="#overview">Overview</a> •
  <a href="#key-findings">Key Findings</a> •
  <a href="#results">Results</a> •
  <a href="#methodology">Methodology</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#reproducibility">Reproducibility</a> •
  <a href="#citation">Citation</a>
</p>

---

## Overview

**HinglishEval** is a multi-dimensional research benchmark designed to evaluate how effectively large language models generate Hindi–English code-mixed text.

Hinglish is widely used in everyday digital communication. However, evaluating Hinglish generation requires more than measuring grammatical correctness or assigning a single fluency score. A model may produce readable text while switching languages unnaturally, using inconsistent Romanized Hindi spelling, misunderstanding instructions, or generating irrelevant responses.

This project evaluates these challenges through a unified workflow combining:

- A benchmark of 1,000 Hinglish prompts.
- Four text-generation models and 4,000 generated responses.
- Human evaluation across six quality dimensions.
- Automated evaluation using language-model judges.
- Inter-annotator and inter-judge agreement analysis.
- Statistical significance testing and bootstrap confidence intervals.
- An E1–E10 error taxonomy.
- Linguistic, lexical-diversity, and checkpoint diagnostics.
- Continued pretraining of Qwen2.5-3B using QLoRA.

The objective is to provide a more comprehensive understanding of the strengths, weaknesses, and evaluation challenges of LLM-generated Hinglish.

## Key Findings

1. **Human evaluation reveals relatively small differences among the leading models.** Qwen2.5-7B and Qwen2.5-3B obtain nearly identical overall human-evaluation means in the reported combined results.

2. **Phi-3.5-mini ranks lowest in the reported overall human evaluation.** Its mean score is 2.114, compared with 2.227 for Qwen2.5-7B and 2.221 for Qwen2.5-3B.

3. **The automated judge produces much larger score gaps than human evaluation.** For example, the reported overall score for Qwen2.5-3B is 3.563, while Phi-3.5-mini receives 1.027.

4. **Inter-annotator agreement is low across several dimensions.** The reported quadratic weighted kappa (QWK) values range from −0.357 to +0.128 across the six dimensions.

5. **Prompt misunderstanding and spelling/transliteration are prominent error categories.** E6 records 1,045 flags, while E8 records 865 flags in the reported error analysis.

6. **Code-mixing quality requires dedicated evaluation.** Linguistic metrics and human ratings provide complementary evidence that cannot be captured by a single automatic metric.

These findings highlight why human evaluation, automated judging, and linguistic analysis should be interpreted together.

## Project at a Glance

| Component | Description |
|---|---|
| Research task | Hindi–English code-mixed text generation |
| Benchmark | 1,000 prompts |
| Generated responses | 4,000 |
| Generator models | Qwen2.5-3B, Qwen2.5-7B, Phi-3.5-mini, HingGPT |
| Human evaluation | Two annotators |
| Quality dimensions | Six |
| Automated judges | Mistral-7B-Instruct and OLMo-2-1B |
| Error analysis | E1–E10 taxonomy |
| Training corpus | 277,431 sequences |
| Cleaned validation utterances | 14,601 |
| Leakage audit | 992 retained prompts; 8 quarantined |
| Statistical methods | Wilcoxon signed-rank, Holm correction, bootstrap confidence intervals |
| Agreement metrics | QWK, ordinal Krippendorff's alpha, Spearman correlation |
| Fine-tuning approach | QLoRA-based continued pretraining |
| Main trained model | Qwen2.5-3B |

---

## Table of Contents

- [Overview](#overview)
- [Key Findings](#key-findings)
- [Project at a Glance](#project-at-a-glance)
- [Research Objectives](#research-objectives)
- [Models Evaluated](#models-evaluated)
- [Methodology](#methodology)
- [Human Evaluation](#human-evaluation)
- [Automated Judge Evaluation](#automated-judge-evaluation)
- [Results](#results)
- [Statistical Analysis](#statistical-analysis)
- [Error Taxonomy](#error-taxonomy)
- [Linguistic Diagnostics](#linguistic-diagnostics)
- [Training Configuration](#training-configuration)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Repository Structure](#repository-structure)
- [Reproducibility](#reproducibility)
- [Limitations](#limitations)
- [Future Work](#future-work)
- [Citation](#citation)
- [License](#license)
- [Acknowledgements](#acknowledgements)

---

## Research Objectives

HinglishEval addresses the following research questions.

### RQ1 — Generation quality

How do different LLMs compare when generating Hindi–English code-mixed text?

### RQ2 — Human evaluation

How do the models perform in terms of fluency, code-mixing naturalness, Hindi grammar, prompt adherence, spelling consistency, and overall quality?

### RQ3 — Automated evaluation

Do LLM-based judges rank the models consistently, and how do their ratings compare with human judgments?

### RQ4 — Evaluator reliability

How much agreement exists between human annotators and between independent LLM judges?

### RQ5 — Linguistic characteristics

How do models differ in code-mixing intensity, language-switching behavior, lexical diversity, repetition, and language-model likelihood metrics?

### RQ6 — Error analysis

Which recurring generation errors affect the quality of code-mixed output?

### RQ7 — Continued pretraining

How can QLoRA-based continued pretraining be incorporated into a Hinglish generation evaluation workflow?

---

## Models Evaluated

Four generation systems are included in the benchmark.

| Model | Role in the study |
|---|---|
| Qwen2.5-3B | Main QLoRA continued-pretraining model |
| Qwen2.5-7B | Larger Qwen comparison model |
| Phi-3.5-mini | Comparison model |
| HingGPT | Hinglish-oriented comparison model |

The models differ in size, tokenizer, training history, and architecture. Consequently, the comparison should be interpreted as a comparison of complete generation systems rather than an architecture-only experiment.

### Training distinction

QLoRA-based continued pretraining is applied to Qwen2.5-3B in this project. The other three models serve as comparison systems and should not be described as having undergone the same training procedure.

---

## Methodology

The research workflow combines data preparation, generation, human evaluation, automated judging, statistical analysis, and linguistic diagnostics.

### End-to-end workflow

```text
Hinglish Corpus
      |
      v
Data Cleaning and Deduplication
      |
      v
Training and Validation Preparation
      |
      v
QLoRA Continued Pretraining
(Qwen2.5-3B)
      |
      v
1,000-Prompt Benchmark
      |
      v
Four Generator Models
      |
      v
4,000 Generated Responses
      |
      +-----------------------------+
      |                             |
      v                             v
Human Evaluation              Automated Judges
Two Annotators                Mistral-7B / OLMo-2-1B
      |                             |
      v                             v
Human Quality Scores          Judge Scores and Calibration
      |                             |
      +--------------+--------------+
                     |
                     v
          Statistical Evaluation
          - Bootstrap confidence intervals
          - Wilcoxon signed-rank tests
          - Holm correction
          - Inter-rater agreement
                     |
                     v
          Linguistic and Error Analysis
                     |
                     v
          Tables, Figures, and Paper
```

### Dataset preparation

The reported workflow includes:

- 277,431 training sequences.
- 14,601 cleaned validation utterances.
- A 1,000-prompt generation benchmark.
- An 8-gram overlap audit.
- A reported audited subset of 992 prompts, with 8 prompts quarantined.

The contamination audit helps identify lexical overlap. It does not guarantee the absence of semantic or indirect contamination.

### Generation benchmark

Four models are evaluated on the benchmark, producing 4,000 responses in total. These generations form the basis of the reported model-level comparison and error analysis.

### Evaluation layers

The workflow uses complementary evaluation methods:

1. Human ratings to assess perceived generation quality.
2. Automated LLM judging to evaluate model outputs using a rubric.
3. Inter-annotator and inter-judge agreement analysis.
4. Linguistic and lexical metrics to characterize generated text.
5. Error categorization to identify recurring failures.
6. Statistical tests to assess observed model differences.

---

## Human Evaluation

Human evaluation measures six dimensions of generated Hinglish.

| Dimension | What it evaluates |
|---|---|
| Fluency | Readability and naturalness of the generated text |
| Code-Mixing Naturalness | Whether Hindi–English mixing feels natural |
| Hindi Grammar | Grammatical acceptability of Hindi constructions |
| Prompt Adherence | Whether the response follows the given instruction |
| Spelling Consistency | Consistency of Romanized Hindi spelling and transliteration |
| Overall Quality | Holistic assessment of the response |

The reported combined human-evaluation table presents mean scores and 95% bootstrap confidence intervals. The two annotators' separate results and their agreement statistics are also important because annotators may use the rating scale differently.

### Human-evaluation interpretation

The combined overall-quality means are close for the three leading systems:

- Qwen2.5-7B: 2.227
- Qwen2.5-3B: 2.221
- HingGPT: 2.175

Phi-3.5-mini receives 2.114.

These values indicate that the absolute differences in the reported combined human scores are small. Statistical significance and practical importance should therefore be considered separately.

Low agreement also means that an average alone does not fully describe evaluator behavior. Per-annotator results should be examined alongside combined results.

---

## Automated Judge Evaluation

The project uses Mistral-7B-Instruct and OLMo-2-1B as automated judges.

Automated judges provide a scalable way to assess many generations, but their ratings may be affected by rubric wording, evaluator preferences, and differences between model families.

### Reported Mistral-7B-Instruct results

Values below are mean ± standard deviation from the reported automated-judge table.

| Dimension | HingGPT | Phi-3.5-mini | Qwen2.5-3B | Qwen2.5-7B |
|---|---:|---:|---:|---:|
| Fluency | 2.123 ± 1.003 | 1.028 ± 0.235 | 3.533 ± 0.921 | 3.251 ± 0.991 |
| Code-Mixing | 2.400 ± 1.279 | 1.041 ± 0.363 | 3.979 ± 1.211 | 3.682 ± 1.235 |
| Hindi Grammar | 1.644 ± 0.631 | 1.014 ± 0.167 | 2.943 ± 0.954 | 2.610 ± 0.942 |
| Prompt Adherence | 1.783 ± 1.057 | 1.032 ± 0.333 | 3.741 ± 1.399 | 3.072 ± 1.531 |
| Spelling | 2.868 ± 1.426 | 1.054 ± 0.411 | 4.648 ± 0.876 | 4.664 ± 0.837 |
| Overall Quality | 1.990 ± 0.951 | 1.027 ± 0.242 | 3.563 ± 1.081 | 3.173 ± 1.139 |

**Interpretation:** The automated judge assigns substantially higher overall scores to Qwen2.5-3B than to Phi-3.5-mini. The human-evaluation gap is much smaller. This difference motivates explicit calibration and agreement analysis rather than relying on automated scores alone.

### Judge agreement

The reported comparison between Mistral-7B and OLMo-2-1B uses 3,989 evaluated cases. QWK values range from −0.166 to +0.008.

The project also evaluates rubric sensitivity. In the reported perturbation experiment, the modified rubric raises Mistral's scores across all six dimensions, with an overall mean increase of +0.420 and a 95% confidence interval of [0.380, 0.458].

These findings demonstrate why judge reliability and rubric sensitivity should be reported alongside model rankings.

---

## Results

### Combined human overall-quality scores

Reported mean of the two annotators, with 1,000 responses per model.

| Model | Overall Quality |
|---|---:|
| Qwen2.5-7B | 2.227 |
| Qwen2.5-3B | 2.221 |
| HingGPT | 2.175 |
| Phi-3.5-mini | 2.114 |

### Six-dimension human results

Values are means with 95% bootstrap confidence intervals.

| Model | Fluency | Code-Mixing | Hindi Grammar | Prompt Adherence | Spelling | Overall |
|---|---|---|---|---|---|---|
| Qwen2.5-7B | 2.394 [2.370, 2.421] | 2.613 [2.592, 2.635] | 2.864 [2.839, 2.888] | 2.659 [2.622, 2.685] | 2.724 [2.684, 2.755] | 2.227 [2.194, 2.262] |
| Qwen2.5-3B | 2.399 [2.372, 2.424] | 2.616 [2.592, 2.638] | 2.884 [2.860, 2.910] | 2.667 [2.633, 2.697] | 2.752 [2.714, 2.782] | 2.221 [2.189, 2.258] |
| HingGPT | 2.361 [2.339, 2.388] | 2.583 [2.559, 2.613] | 2.845 [2.813, 2.872] | 2.631 [2.601, 2.663] | 2.694 [2.658, 2.723] | 2.175 [2.142, 2.209] |
| Phi-3.5-mini | 2.358 [2.335, 2.382] | 2.558 [2.533, 2.584] | 2.827 [2.798, 2.852] | 2.615 [2.578, 2.643] | 2.688 [2.646, 2.720] | 2.114 [2.079, 2.142] |

Qwen2.5-3B has the highest reported mean in several individual dimensions, while Qwen2.5-7B has the highest combined overall-quality mean. The differences are small, and confidence intervals should be considered when interpreting rankings.

### Pairwise statistical comparisons

The following reported results use Wilcoxon signed-rank tests with Holm correction for overall quality, with N = 1,000.

| Comparison | Mean Difference | Raw p-value | Holm-adjusted p-value | Significant at 0.05? |
|---|---:|---:|---:|---|
| Qwen2.5-7B vs Phi-3.5-mini | +0.1125 | 4.89 × 10⁻⁹ | 2.94 × 10⁻⁸ | Yes |
| Qwen2.5-3B vs Phi-3.5-mini | +0.1070 | 2.62 × 10⁻⁸ | 1.31 × 10⁻⁷ | Yes |
| HingGPT vs Phi-3.5-mini | +0.0605 | 1.51 × 10⁻³ | 6.05 × 10⁻³ | Yes |
| Qwen2.5-7B vs HingGPT | +0.0520 | 3.56 × 10⁻³ | 1.07 × 10⁻² | Yes |
| Qwen2.5-3B vs HingGPT | +0.0465 | 2.73 × 10⁻² | 5.47 × 10⁻² | No |
| Qwen2.5-3B vs Qwen2.5-7B | −0.0055 | 0.540 | 0.540 | No |

Under the reported Holm-adjusted results, the difference between Qwen2.5-3B and Qwen2.5-7B is not statistically significant. The comparison between Qwen2.5-3B and HingGPT also does not reach the 0.05 threshold after correction.

---

## Inter-Annotator Agreement

The project reports exact agreement, agreement within one scale point, QWK, ordinal Krippendorff's alpha, and Spearman correlation.

| Dimension | Exact Agreement | Within ±1 | QWK | Ordinal α | Spearman ρ |
|---|---:|---:|---:|---:|---:|
| Prompt Adherence | 35.8% | 86.5% | +0.086 | −0.012 | +0.118 |
| Spelling Consistency | 37.1% | 84.0% | +0.128 | +0.063 | +0.183 |
| Hindi Grammar | 37.2% | 86.1% | −0.119 | −0.157 | −0.154 |
| Fluency | 28.8% | 90.4% | +0.000 | −0.327 | +0.047 |
| Code-Mixing Naturalness | 29.2% | 80.1% | −0.357 | −0.395 | −0.408 |
| Overall Quality | 14.2% | 57.8% | +0.087 | −0.323 | +0.230 |

**Interpretation:** Agreement is limited, particularly for overall quality and code-mixing naturalness. High within-one-point agreement does not necessarily imply strong ordinal agreement. Differences in scale usage and interpretation can influence combined scores and should be acknowledged.

---

## Error Taxonomy

The project uses ten error categories to classify recurring generation failures.

| Code | Error Category | HingGPT | Phi-3.5-mini | Qwen2.5-3B | Qwen2.5-7B | Total |
|---|---|---:|---:|---:|---:|---:|
| E1 | English-dominant | 6 | 6 | 19 | 30 | 61 |
| E2 | Hindi-dominant | 53 | 264 | 180 | 151 | 648 |
| E3 | Unnatural code-switching | 9 | 1 | 10 | 6 | 26 |
| E4 | Grammatical error | 98 | 73 | 68 | 45 | 284 |
| E5 | Repetition | 36 | 117 | 41 | 48 | 242 |
| E6 | Prompt misunderstanding | 156 | 351 | 215 | 323 | 1,045 |
| E7 | Incomplete response | 163 | 275 | 106 | 135 | 679 |
| E8 | Spelling / transliteration | 2 | 678 | 114 | 71 | 865 |
| E9 | Hallucination detector flag | 0 | 0 | 0 | 0 | 0 |
| E10 | Irrelevant response | 135 | 236 | 91 | 23 | 485 |

The analysis reports 4,335 flags across 4,000 generations. A single response can receive multiple error flags, so the number of flags is not the number of distinct responses containing errors.

**Important:** E9 = 0 means that the detector raised no flags. It does not establish that hallucinations are absent.

### Main error-analysis observations

- E6, prompt misunderstanding, is the largest reported category.
- E8, spelling and transliteration, is another major source of errors, particularly for Phi-3.5-mini.
- E7, incomplete responses, indicates that instruction completion remains a challenge.
- E10 captures responses that do not adequately address the requested task.
- E3 highlights the need to distinguish natural language mixing from arbitrary language switching.

---

## Linguistic Diagnostics

The project includes measures of language mixing, language presence, switching, perplexity, diversity, and repetition.

| Metric | HingGPT | Phi-3.5-mini | Qwen2.5-3B | Qwen2.5-7B |
|---|---:|---:|---:|---:|
| Code-Mixing Index (CMI, %) | 19.07 | 15.71 | 15.63 | 13.73 |
| Both languages present (%) | 77.3 | 51.3 | 67.0 | 68.3 |
| Das–Gambäck CMI | 15.146 | 22.238 | 16.776 | 12.927 |
| Average language switches | 8.709 | 4.677 | 4.308 | 4.202 |
| Perplexity | 171.23 | 50.79 | 74.02 | 55.13 |
| Distinct-1 | 0.734 | 0.700 | 0.897 | 0.882 |
| Distinct-2 | 0.858 | 0.751 | 0.960 | 0.970 |
| Repetition rate | 0.168 | 0.127 | 0.097 | 0.118 |

### Metric interpretation

- **Code-Mixing Index:** Characterizes the degree of mixing between languages.
- **Both languages present:** Measures the percentage of responses containing both Hindi and English.
- **Language switches:** Counts transitions between languages under the project’s token-labeling procedure.
- **Perplexity:** Measures predictive uncertainty under a particular language model and tokenization setup. It should not be treated as a direct human-quality score.
- **Distinct-1 and Distinct-2:** Measure unigram and bigram diversity.
- **Repetition rate:** Captures repeated lexical content under the project’s metric definition.

Metrics must be interpreted together. More language switching or higher lexical diversity does not automatically imply more natural Hinglish.

---

## Training Configuration

The project reports QLoRA-based continued pretraining of Qwen2.5-3B.

| Parameter | Reported Setting |
|---|---|
| Training sequences | 277,431 |
| Validation utterances | 14,601 |
| Adaptation method | QLoRA |
| LoRA rank | 8 |
| LoRA alpha | 16 |
| LoRA dropout | 0.05 |
| Sequence length | 128 |
| Batch size | 16 |
| Optimizer | paged_adamw_8bit |
| Precision | FP16 |
| Random seed | 42 |

Training and generation require a compatible environment with PyTorch, Transformers, PEFT, bitsandbytes, and suitable GPU resources.

The exact training behavior, checkpoint availability, and reproduction of model outputs depend on the configuration and assets included in the repository.

---

## Installation

### Prerequisites

- Python 3.10 or a compatible Python version for the project dependencies.
- Git.
- A compatible environment for the analysis scripts.
- CUDA-capable GPU for training workflows that require GPU acceleration.

### Clone the repository

```bash
git clone https://github.com/kancharla-vyshnavi/A-Multi-Dimensional-Benchmark-of-LLMs-for-Hindi-English-Code-Mixed-Generation.git

cd A-Multi-Dimensional-Benchmark-of-LLMs-for-Hindi-English-Code-Mixed-Generation
```

### Create a virtual environment

**Windows PowerShell**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

**Linux / macOS**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

### Install analysis dependencies

```bash
python -m pip install pandas numpy scipy matplotlib
```

Training workflows may additionally require:

```bash
python -m pip install torch transformers peft bitsandbytes
```

Install versions compatible with your Python, operating system, and CUDA setup. For reproducible experiments, use a pinned dependency file if one is provided in the repository.

---

## Quick Start

### 1. Generate publication tables and figures

From the repository root:

```bash
python research_upgrade/v3/scripts/generate_publication_figures_and_tables.py
```

This is the documented command for rebuilding publication tables and figures from the saved project data.

### 2. Generate the human-evaluation report

```bash
python research_upgrade/scripts/generate_human_eval_report.py
```

### 3. Evaluate linguistic and automatic metrics

```bash
python research_upgrade/scripts/evaluate_linguistic_and_automatic_metrics.py
```

### 4. Run the human-rating application

The project includes a FastAPI-based rating interface.

```bash
python -m uvicorn research_upgrade.human_validation.app:app --host 127.0.0.1 --port 8000
```

Open the following address in your browser:

```text
http://127.0.0.1:8000
```

The commands above assume the referenced files and dependencies are present in the checked-out repository. Follow any script-specific configuration and input-data requirements.

---

## Repository Structure

The project organizes analysis assets, human evaluation, scripts, figures, tables, and manuscript files into separate areas.

```text
HinglishEval/
├── All Graphs/
├── Tables csv/
├── src/
│   └── run_independent_mistral_judge.py
├── research_upgrade/
│   ├── figures/
│   ├── human_validation/
│   ├── leakage_audit/
│   ├── paper/
│   ├── reports/
│   ├── scripts/
│   ├── tables/
│   └── v3/
│       ├── configs/
│       ├── data/
│       ├── figures/
│       ├── paper/
│       ├── references/
│       ├── reports/
│       ├── scripts/
│       └── tables/
├── README.md
├── LICENSE
└── CITATION.cff
```

The exact set of files may change as the project evolves.

### Important data and analysis files

| File | Purpose |
|---|---|
| `human_ratings_4000_two_annotators.csv` | Human-rating records |
| `table_human_evaluation_4000_summary.csv` | Combined human-evaluation summary |
| `table_human_evaluation_4000_annotator_breakdown.csv` | Separate annotator results |
| `table_human_evaluation_4000_inter_annotator_agreement.csv` | Agreement statistics |
| `table_human_evaluation_4000_pairwise_significance.csv` | Pairwise significance results |
| `research_upgrade/scripts/generate_4k_human_evaluation_tables.py` | Script for generating the 4K human-evaluation tables |
| `src/run_independent_mistral_judge.py` | Independent Mistral-judge workflow |

The project also includes figures, research reports, leakage-audit artifacts, and manuscript material.

---

## Reproducibility

The reported evaluation uses the following procedures.

| Component | Method |
|---|---|
| Random seed | 42 |
| Confidence intervals | Bootstrap, 10,000 resamples |
| Pairwise model comparisons | Wilcoxon signed-rank tests |
| Multiple comparisons | Holm correction |
| Human agreement | QWK, ordinal Krippendorff's alpha, Spearman correlation |
| Leakage audit | 8-gram overlap audit |
| Error analysis | E1–E10 taxonomy |
| Linguistic analysis | CMI, language switches, Distinct-n, perplexity, repetition |

### Reproducibility recommendations

1. Preserve the original benchmark and annotation files.
2. Record package versions and model checkpoint identifiers.
3. Use the documented random seed where applicable.
4. Keep human-evaluation results separate from automated-judge outputs.
5. Retain per-annotator results in addition to combined averages.
6. Report confidence intervals and adjusted p-values alongside model comparisons.
7. Document any changes to preprocessing, scoring rubrics, or error detectors.
8. Avoid committing secrets, credentials, private annotation information, or large model weights without an explicit need and appropriate permissions.

---

## Limitations

HinglishEval has several limitations that are important when interpreting the results.

- **Inter-annotator disagreement:** Human ratings show limited agreement across multiple dimensions.
- **Scale-use differences:** Annotators may use rating scales differently, affecting combined scores.
- **Automated judge bias:** LLM-based judges may assign substantially different scores from human evaluators.
- **Rubric sensitivity:** Changes in rubric wording can shift automated scores.
- **Metric limitations:** Perplexity, lexical diversity, and code-mixing indices capture different aspects of generation and cannot replace human judgments.
- **Contamination-audit limitations:** An 8-gram overlap audit does not rule out semantic contamination.
- **Model comparability:** The models differ in size, tokenizer, and training history.
- **Offline evaluation:** Benchmark results do not directly measure deployment latency, user satisfaction, or real-world safety.
- **Checkpoint and environment dependence:** Exact reproduction requires the relevant data, dependencies, configurations, and model assets.

---

## Future Work

Potential directions for extending this research include:

- Expanding the benchmark with more conversational and domain-specific Hinglish prompts.
- Improving annotation guidelines and measuring agreement after calibration.
- Evaluating additional human annotators and reporting annotator-level uncertainty.
- Calibrating LLM judges against human ratings.
- Studying the effect of rubric wording and evaluation order.
- Extending error detection to more nuanced forms of code-mixing and transliteration.
- Testing additional continued-pretraining configurations.
- Evaluating generation latency, robustness, and user-facing performance.
- Publishing complete reproduction configurations and approved research artifacts.

These directions are proposed extensions, not claims of completed experiments.

---

## Paper and Resources

| Resource | Location |
|---|---|
| Repository | [HinglishEval on GitHub](https://github.com/kancharla-vyshnavi/A-Multi-Dimensional-Benchmark-of-LLMs-for-Hindi-English-Code-Mixed-Generation) |
| Manuscript | `research_upgrade/v3/paper/hinglisheval_paper.md` |
| Human-evaluation tables | `research_upgrade/tables/` |
| Publication scripts | `research_upgrade/v3/scripts/` |
| Figures | `research_upgrade/figures/` and related figure directories |

A public arXiv paper, model adapter, or checkpoint should be linked here only when it is actually available.

---

## License

The repository includes a `LICENSE` file. Review that file for the exact terms applicable to this project's code.

Third-party datasets, pretrained models, and model checkpoints remain subject to their own licenses and terms of use. The repository's license does not automatically grant additional rights to third-party assets.

---

## Acknowledgements

This work brings together code-mixed language generation, human evaluation, automated judging, statistical analysis, and linguistic diagnostics.

The project builds on publicly available research resources and model ecosystems, including work associated with L3Cube-HingCorpus, Qwen, Phi, Mistral, OLMo, LoRA, and QLoRA. Please consult the relevant original papers, documentation, and licenses when using those resources.

---

<p align="center">
  <strong>HinglishEval</strong>
  <br />
  A multi-dimensional approach to understanding Hindi–English code-mixed generation.
  <br /><br />
  Built by Kancharla Vyshnavi
  <br />
  B.Tech CSE (AI), Narayana Engineering College, Nellore
</p>
