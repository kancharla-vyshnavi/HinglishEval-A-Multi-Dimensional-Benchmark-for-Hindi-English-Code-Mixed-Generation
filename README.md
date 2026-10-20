# HinglishEval: A Multi-Dimensional Benchmark of LLMs for Hindi–English Code-Mixed Generation

<p align="center">
  <strong>Evaluating Fluency, Code-Mixing Naturalness, Grammar, Prompt Adherence, Spelling, and Overall Quality</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Task-Code--Mixed%20Generation-blue" alt="Task: Code-Mixed Generation">
  <img src="https://img.shields.io/badge/Models-4-purple" alt="Four generator models">
  <img src="https://img.shields.io/badge/Benchmark-1%2C000%20Prompts-orange" alt="1,000 prompts">
  <img src="https://img.shields.io/badge/Generated%20Responses-4%2C000-green" alt="4,000 generated responses">
  <img src="https://img.shields.io/badge/Evaluation%20Dimensions-6-teal" alt="Six evaluation dimensions">
</p>

## Table of Contents

- [Overview](#overview)
- [Research Motivation](#research-motivation)
- [Objectives](#objectives)
- [Benchmark at a Glance](#benchmark-at-a-glance)
- [Models Evaluated](#models-evaluated)
- [Dataset Preparation](#dataset-preparation)
- [System Architecture](#system-architecture)
- [Evaluation Framework](#evaluation-framework)
- [Human Evaluation](#human-evaluation)
- [Automated-Judge Evaluation](#automated-judge-evaluation)
- [Statistical Analysis](#statistical-analysis)
- [Error Analysis](#error-analysis)
- [Linguistic Analysis](#linguistic-analysis)
- [Checkpoint and Diversity Metrics](#checkpoint-and-diversity-metrics)
- [Repository Structure](#repository-structure)
- [Installation](#installation)
- [Running the Project](#running-the-project)
- [Human-Validation Interface](#human-validation-interface)
- [Results and Discussion](#results-and-discussion)
- [Reproducibility](#reproducibility)
- [Limitations](#limitations)
- [Citation](#citation)
- [License](#license)
- [Acknowledgements](#acknowledgements)

## Overview

**HinglishEval** is a research project for evaluating large language models on Hindi–English code-mixed text generation. Hinglish is commonly used in informal digital communication, where Hindi and English words and grammatical structures may occur in the same sentence.

Generating natural Hinglish is more complex than producing grammatically correct Hindi or English independently. A response must preserve the user's intent, use appropriate language switching, remain readable, follow instructions, and maintain consistent spelling and transliteration.

This project presents a multi-dimensional evaluation framework combining controlled generation, linguistic analysis, automated judging, human assessment, statistical testing, robustness experiments, and response-error classification.

The benchmark compares four generator models on a shared collection of prompts. The resulting analyses examine how model performance changes across quality dimensions and evaluation methods.

### Key features

- A benchmark of 1,000 prompts evaluated across four generator models.
- 4,000 generated responses in the original benchmark.
- Six quality dimensions for response assessment.
- A reported Hindi–English code-mixed training corpus containing 277,431 sequences.
- A cleaned validation corpus containing 14,601 utterances.
- An eight-gram Jaccard overlap audit of the benchmark.
- Human-rating and automated-judge analyses.
- Inter-judge reliability and rubric-robustness experiments.
- An E1–E10 taxonomy for classifying generation errors.
- Linguistic metrics, checkpoint metrics, and prompt-format diagnostics.
- A human-validation interface implemented with FastAPI.

## Research Motivation

Conventional text-generation metrics do not fully capture the quality of code-mixed language. A model may produce a readable answer but ignore a request to use Hinglish. Another model may follow the prompt while producing unnatural language switching or inconsistent transliteration.

HinglishEval therefore considers several complementary questions:

1. Is the response fluent and understandable?
2. Is the Hindi–English mixing natural?
3. Are Hindi grammatical structures acceptable?
4. Does the response follow the original instruction?
5. Is spelling and transliteration consistent?
6. How does the response perform under an overall-quality judgment?
7. Do human evaluators and automated judges agree?
8. Are model rankings stable across evaluation methods?
9. Which response errors occur most frequently?
10. How do language composition and lexical diversity differ between models?

The framework is intended to support a more informative comparison than a single aggregate score.

## Objectives

The main objectives are to:

1. Prepare a cleaned Hindi–English code-mixed corpus.
2. Apply QLoRA-based continued pretraining to the designated project model.
3. Construct a controlled benchmark containing 1,000 prompts.
4. Compare four generator models under a shared benchmark.
5. Evaluate responses using six quality dimensions.
6. Compare human ratings with automated-judge outputs.
7. Measure inter-judge and inter-annotator agreement where matched data are available.
8. Conduct paired statistical comparisons with multiple-comparison correction.
9. Investigate sensitivity to rubric wording and prompt formatting.
10. Classify generation errors using the E1–E10 taxonomy.
11. Analyse language composition, switching behaviour, and lexical diversity.
12. Examine checkpoint metrics and implications for chatbot deployment.

## Benchmark at a Glance

| Component | Reported value |
|---|---:|
| Original benchmark prompts | 1,000 |
| Generator models | 4 |
| Original generated responses | 4,000 |
| Evaluation dimensions | 6 |
| Continued-pretraining sequences | 277,431 |
| Validation utterances | 14,601 |
| Prompts retained after the reported leakage audit | 992 |
| Prompts quarantined by the audit | 8 |
| Reported random seed | 42 |
| Reported bootstrap configuration | 10,000 resamples where specified |

**Important distinction:** 4,000 generated responses does not automatically mean 4,000 completed human evaluations, 4,000 matched annotation pairs, or 4,000 completed automated-judge scores. Each evaluation stage has its own sample size.

## Models Evaluated

The original benchmark compares four generator models.

| Model | Role |
|---|---|
| Qwen2.5-3B | Generator and designated project adaptation model |
| Qwen2.5-7B | Comparison generator |
| Phi-3.5-mini | Comparison generator |
| HingGPT | Hindi–English code-mixed generation model |

The project uses QLoRA-based continued pretraining for the designated Qwen2.5-3B model. The other three models are comparison systems and should not be described as having undergone the same training run.

Differences in architecture, tokenizer, instruction tuning, native chat templates, and stopping conventions can influence the results. The experiment compares the evaluated systems rather than isolating model size as the only variable.

## Dataset Preparation

### Training and validation data

The reported project configuration includes:

- **277,431 training sequences** for continued pretraining.
- **14,601 validation utterances**.
- A Hindi–English code-mixed language resource associated with L3Cube-HingCorpus research.

Data preparation aims to reduce malformed text and unsuitable duplicates while preserving the linguistic characteristics of code-mixed text.

### Benchmark construction

The original benchmark consists of 1,000 prompts. Each of the four generator models is evaluated against this prompt collection, producing 4,000 responses in total.

### Leakage audit

The reported audit uses eight-gram Jaccard overlap to examine potential textual overlap between benchmark prompts and the training corpus.

The reported outcome is:

- 992 prompts retained in the leakage-audited subset.
- 8 prompts quarantined.

The original 1,000-prompt benchmark and the 992-prompt leakage-audited subset represent different experimental populations. Results must identify which population was used.

An eight-gram overlap audit addresses a specific type of textual overlap. It does not establish the absence of every possible form of semantic overlap or memorization.

## System Architecture

The research workflow consists of the following stages:

1. **Corpus preparation:** Load and clean the code-mixed text.
2. **Preprocessing:** Apply the project's text-cleaning and deduplication procedures.
3. **Benchmark construction:** Prepare the shared prompt collection.
4. **Model adaptation:** Apply QLoRA-based continued pretraining to the designated model.
5. **Controlled generation:** Generate responses from the four benchmark models.
6. **Quality evaluation:** Assess outputs across six dimensions.
7. **Human assessment:** Analyse human ratings and annotator-specific behaviour.
8. **Automated judging:** Calculate rubric-based scores and evaluate judge calibration.
9. **Statistical analysis:** Conduct matched comparisons, reliability analysis, and robustness experiments.
10. **Error analysis:** Classify response problems using E1–E10.
11. **Linguistic analysis:** Measure language composition, switching, and lexical diversity.
12. **Reporting and deployment:** Generate figures and tables and assess chatbot integration.

Offline benchmark results and live chatbot behaviour are separate evaluation targets. Strong benchmark performance does not, by itself, demonstrate low latency or reliable live responses.

## Evaluation Framework

HinglishEval uses six evaluation dimensions on a five-point ordinal scale.

| Dimension | Evaluation objective |
|---|---|
| Fluency | Readability, coherence, and natural expression |
| Code-Mixing Naturalness | Appropriate and natural Hindi–English mixing |
| Hindi Grammar | Grammatical acceptability of Hindi structures |
| Prompt Adherence | Compliance with the user's instructions |
| Spelling Consistency | Consistency of spelling and transliteration |
| Overall Quality | Overall assessment of the generated response |

Higher scores indicate more favourable judgments under the adopted rubric.

The dimensions are related but not interchangeable. A response can be fluent without following the prompt, or follow the prompt while containing awkward code-switching.

## Human Evaluation

Human evaluation provides a human-centred assessment of generated responses. Its results must be reported separately from automated-judge scores.

### Annotation scope

The project contains a 4,000-response benchmark and a human-evaluation analysis. The current analysis records report the following counts:

| Annotation measure | Count |
|---|---:|
| Generated responses in the benchmark | 4,000 |
| Annotator A completed ratings | 3,964 |
| Annotator B completed ratings | 4,000 |
| Responses matched across both annotators | 3,964 |

The matched response count is relevant to analyses requiring both annotators to have rated the same response. It should not be replaced with the total number of generated responses.

### Annotator-specific analysis

Annotator-specific means and rankings are useful because evaluators may interpret naturalness, grammar, and overall quality differently.

The analysis should distinguish:

- Mean ratings from Annotator A.
- Mean ratings from Annotator B.
- Aggregated descriptive summaries.
- Matched response pairs.
- Inter-annotator agreement.
- Paired model-comparison results.

A difference between annotator means does not, by itself, identify the cause of the disagreement. Agreement statistics and dimension-level results provide additional information.

### Human-rating interpretation

Human scores should be interpreted with their sample size, rating scale, and matching structure. Results from a smaller human-validation sample must not be presented as full-collection scores.

## Automated-Judge Evaluation

Automated judges assign rubric-based scores to generated responses. The project examines judge outputs alongside human ratings and reliability statistics.

### Judge calibration

Judge calibration asks whether automated scores reflect human judgments. Useful measures include:

- **Spearman rank correlation (\(\rho\)):** Measures the association between two sets of rankings.
- **Quadratic weighted kappa (QWK):** Measures agreement between ordinal ratings while accounting for the magnitude of disagreements.
- **Dimension-wise comparison:** Shows whether agreement differs across fluency, code-mixing naturalness, grammar, prompt adherence, spelling, and overall quality.

### Reported calibration findings

The earlier reported Mistral–human calibration analysis contains the following dimension-level results:

| Dimension | Spearman \(\rho\) | p-value | QWK |
|---|---:|---:|---:|
| Fluency | 0.158 | 3.93 × 10⁻⁴ | 0.171 |
| Code-Mixing Naturalness | 0.222 | 5.64 × 10⁻⁷ | 0.176 |
| Hindi Grammar | 0.127 | 4.44 × 10⁻³ | 0.122 |
| Prompt Adherence | 0.191 | 1.63 × 10⁻⁵ | 0.153 |
| Spelling Consistency | 0.175 | 8.05 × 10⁻⁵ | 0.139 |
| Overall Quality | 0.184 | 3.57 × 10⁻⁵ | 0.169 |

These are the reported calibration results for that analysis; they should not be relabelled as the results of a different judge, annotator, or evaluation sample.

The correlations are positive but modest, and the QWK values indicate limited agreement. Statistical significance of a correlation does not necessarily imply strong practical agreement.

A separate Qwen2.5-3B-Instruct automated-judge run completed **488 of 4,000 responses** in the reported run. This is a partial run, not a completed full-collection automated evaluation.

## Statistical Analysis

The project uses statistical procedures to distinguish descriptive differences from evidence of systematic model differences.

### Paired comparisons

When the same prompts are evaluated by multiple models, paired tests can account for the shared prompt structure.

The analysis includes non-parametric model comparisons and multiple-comparison correction where applicable.

### Wilcoxon signed-rank test

The Wilcoxon signed-rank test can compare paired observations when its assumptions are appropriate. The paired sample must be defined explicitly, and missing pairs must not be treated as valid observations.

### Holm correction

Holm correction adjusts p-values across a specified family of hypotheses to control the family-wise error rate.

For model comparisons, report:

- Model pair.
- Paired sample size.
- Mean or median difference, as appropriate.
- Test statistic.
- Raw p-value.
- Holm-adjusted p-value.
- Effect size.
- Statistical interpretation.

A small p-value does not automatically imply a large or practically important effect.

### Reliability analysis

The project also examines agreement between evaluators. Inter-judge agreement and inter-annotator agreement are distinct quantities and must be labelled separately.

## Error Analysis

The E1–E10 taxonomy classifies recurring response problems.

| Code | Error category | Description |
|---|---|---|
| E1 | English-dominant output | Output is predominantly English when Hinglish is expected |
| E2 | Hindi-dominant output | Output is predominantly Hindi when a more balanced mix is expected |
| E3 | Unnatural code-switching | Language switching is awkward or contextually inappropriate |
| E4 | Grammatical error | Incorrect grammatical construction |
| E5 | Repetition | Repeated words, phrases, or content |
| E6 | Prompt misunderstanding | The response misinterprets the instruction |
| E7 | Incomplete response | The response does not adequately complete the task |
| E8 | Spelling/transliteration error | Inconsistent or incorrect spelling or transliteration |
| E9 | Hallucination-detector flag | Output is flagged by the designated detector |
| E10 | Irrelevant response | Response includes material unrelated to the prompt |

### Interpreting error counts

A response may receive multiple error labels. Consequently, the total number of error flags can exceed the number of generated responses.

A zero count for a detector category means that the detector produced no flags under the reported procedure. It does not prove that the underlying type of error was absent.

## Linguistic Analysis

Linguistic analysis complements rubric-based quality scores by measuring language composition and switching behaviour.

The project reports the following kinds of measures:

- Code-Mixing Index (CMI).
- Percentage of responses containing both Hindi and English.
- Das–Gambäck CMI.
- Average Hindi-token count.
- Average English-token count.
- Average number of language switches.

### Why linguistic metrics matter

Language composition can differ from perceived naturalness. A response may contain both languages without switching naturally, and a higher language-switch count does not necessarily indicate better communication.

CMI results depend on the metric definition, token classification, treatment of neutral tokens, and text normalization. Different definitions may produce different model rankings.

## Checkpoint and Diversity Metrics

The checkpoint analysis includes metrics describing predictive fit, text distribution, and lexical diversity.

| Metric | What it measures |
|---|---|
| Perplexity | Predictive uncertainty under a specified model and tokenization |
| Cross-entropy | Average prediction loss |
| Entropy | A measure of uncertainty or diversity under the adopted calculation |
| Characters per token | Character-to-token relationship |
| Bits per character (BPC) | Character-normalized predictive loss |
| Distinct-1 | Proportion of unique unigrams |
| Distinct-2 | Proportion of unique bigrams |
| Repetition rate | Repetition under the project's defined calculation |

These metrics are not substitutes for human-perceived response quality. Comparisons require consistent tokenization, evaluation data, aggregation, and treatment of empty or failed outputs.

The reported 100-sequence continued-pretraining diagnostic gives perplexity values of 154.97 for Base, 187.97 for Instruct, and 57.78 for the continued-pretrained configuration. These results belong to that diagnostic experiment and must remain separate from full-validation checkpoint results.

## Prompt-Format Diagnostics

Prompt construction can affect instruction-following models. The project examines differences between a current wrapper and plain-continuation formatting under the adopted validity criteria.

Reported validity rates were:

| Model | Current wrapper | Plain continuation |
|---|---:|---:|
| HingGPT | 7% | 92% |
| Phi-3.5-mini | 6% | 95% |
| Qwen2.5-3B | 7% | 99% |
| Qwen2.5-7B | 3% | 96% |

These are reported diagnostic rates, not proof that plain continuation is universally the correct inference format. Native chat templates, end-of-turn tokens, and output parsing must be considered for each model.

## Repository Structure

The research workspace is organised into figures, human-validation resources, leakage-audit materials, paper files, reports, scripts, tables, and a versioned `v3` directory.

```text
research_upgrade/
├── figures/
├── human_validation/
├── leakage_audit/
├── paper/
├── reports/
├── scripts/
├── tables/
└── v3/
    ├── configs/
    ├── data/
    ├── figures/
    ├── paper/
    ├── references/
    ├── reports/
    ├── scripts/
    └── tables/
```

The exact files available in a checkout may vary. Run commands from the repository root and retain the existing directory structure.

## Installation

### Requirements

The analysis scripts require a compatible Python environment and the dependencies specified by the project.

Python 3.11 or newer is a reasonable starting point for the documented commands, but the actual dependency versions should be taken from the repository's requirements or environment files.

### Create a virtual environment

**Windows PowerShell**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

**Linux or macOS**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

Install dependencies using the dependency file present in the repository. For example, if the repository contains `requirements.txt`:

```bash
python -m pip install -r requirements.txt
```

If a dependency file is not present in the checkout, install the dependencies documented by the relevant script rather than assuming that every training or inference package is required for analysis-only tasks.

## Running the Project

Run these commands from the repository root.

### 1. Generate publication figures and tables

```bash
python research_upgrade/v3/scripts/generate_publication_figures_and_tables.py
```

### 2. Generate the human-evaluation report

```bash
python research_upgrade/scripts/generate_human_eval_report.py
```

### 3. Evaluate linguistic and automatic metrics

```bash
python research_upgrade/scripts/evaluate_linguistic_and_automatic_metrics.py
```

These commands run the documented reporting and evaluation scripts. They do not, by themselves, reproduce the complete data-preparation, four-model generation, or continued-pretraining pipeline.

The generated files and outputs depend on the inputs and configuration available in the checkout.

## Human-Validation Interface

The project includes a FastAPI human-validation interface.

From the repository root, run:

```bash
python -m uvicorn research_upgrade.human_validation.app:app --host 127.0.0.1 --port 8000
```

Open the following address in a browser:

`http://127.0.0.1:8000`

This command launches the human-validation interface. It is not the command for launching the conversational chatbot.

## Chatbot Integration

The project includes chatbot deployment as a system component. The benchmark and the deployed chatbot serve different purposes:

- **Benchmark evaluation** measures model outputs on a fixed prompt collection.
- **Chatbot evaluation** examines responses during interactive use.
- **Latency evaluation** measures response time under a specified environment.
- **Context-handling evaluation** examines whether the system uses conversation history appropriately.
- **Prompt-adherence evaluation** tests whether interactive responses follow user instructions.

A live demo link, screenshot, or GIF should be added only when the corresponding asset or public endpoint is available.

## Results and Discussion

The reported experiments illustrate why code-mixed generation should be assessed through multiple evaluation methods.

### Human-evaluation summary

A previously reported 500-rating human-evaluation sample gives the following overall-quality means:

| Model | Mean ± SD |
|---|---:|
| Qwen2.5-3B | 2.704 ± 0.959 |
| Qwen2.5-7B | 2.480 ± 0.989 |
| HingGPT | 2.192 ± 0.904 |
| Phi-3.5-mini | 2.112 ± 0.961 |

These figures belong to that 500-rating sample. They are not the full-collection 4,000-response summary and should not be substituted for the separate two-annotator analysis.

### Main observations

1. Model rankings can differ by evaluation dimension.
2. Human ratings and automated-judge scores represent different sources of evidence.
3. Inter-evaluator agreement needs to be examined rather than assumed.
4. Prompt-format choices can affect observed validity rates.
5. Language composition and lexical diversity do not independently establish naturalness.
6. Error counts help identify recurring problems that aggregate scores may conceal.
7. Descriptive differences should be accompanied by appropriate uncertainty estimates and statistical tests.

No single score should be interpreted as a universal ranking of model quality across all Hinglish tasks.

## Reproducibility

The following practices are important when reproducing the reported analyses:

- Use the intended benchmark and clearly record the sample definition.
- Preserve prompt IDs and response IDs.
- Record model identifiers and generation configurations.
- Keep human-rating records separate from automated-judge outputs.
- Use matched observations for paired comparisons.
- Report missing records and exclusions.
- Identify the evaluation dimension and rating scale for every score.
- Report raw and Holm-adjusted p-values for the designated comparison family.
- Keep diagnostic experiments separate from full-validation results.
- Preserve scripts, configurations, tables, and figures alongside the analysis outputs.

The reported random seed is `42`. A bootstrap configuration of `10,000` resamples is reported where specified in the relevant analysis.

## Limitations

- The benchmark represents a particular collection of prompts and code-mixed language data.
- The 1,000-prompt benchmark and the 992-prompt leakage-audited subset are different evaluation populations.
- The generator models differ in architecture, tokenization, and instruction-tuning history.
- Human evaluation and automated judging may produce different rankings.
- Inter-annotator and inter-judge agreement can vary across dimensions.
- Predictive metrics such as perplexity do not directly measure conversational usefulness.
- A text-overlap audit cannot eliminate every possible form of contamination.
- Prompt-format diagnostics depend on the adopted validity criteria.
- Offline benchmark performance does not guarantee good live-chatbot behaviour.
- Reported partial automated-judge runs must not be presented as completed full-collection evaluations.

## Citation

If you use this project in research, cite the associated paper once its final public bibliographic record is available.

Relevant background resources include:

- L3Cube-HingCorpus and HingBERT: https://aclanthology.org/2022.wildre-1.2/
- LoRA: https://arxiv.org/abs/2106.09685
- QLoRA: https://arxiv.org/abs/2305.14314
- Qwen2.5 Technical Report: https://arxiv.org/abs/2412.15115
- Phi-3 Technical Report: https://arxiv.org/abs/2404.14219
- L3Cube code-mixed NLP resources: https://github.com/l3cube-pune/code-mixed-nlp

A public paper identifier and project-specific citation should be added when the final public record exists.

## License

The repository should include the applicable `LICENSE` file. The license badge and licensing statement should match the actual license distributed with the project.

## Acknowledgements

This work draws on research in code-mixed natural language processing, parameter-efficient model adaptation, and evaluation of language-model generation. The relevant model cards, dataset documentation, and redistribution terms should be consulted before sharing model checkpoints or datasets.

