# HinglishEval: A Multi-Dimensional Benchmark for Hindi-English Code-Mixed Generation

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)

# 1. Clone and enter the repository
git clone https://github.com/kancharla-vyshnavi/A-Multi-Dimensional-Benchmark-of-LLMs-for-Hindi-English-Code-Mixed-Generation.git
cd A-Multi-Dimensional-Benchmark-of-LLMs-for-Hindi-English-Code-Mixed-Generation

# 2. Create and activate a Python environment (Python 3.11+)
python -m venv .venv
Activate .venv, install the report script's Python dependencies, then run the human-evaluation report:
python -m pip install --upgrade pip
python -m pip install pandas numpy scipy
python research_upgrade/scripts/generate_human_eval_report.py
Expected output: the script reads research_upgrade/tables/human_ratings_annotator_a_500.csv, writes research_upgrade/tables/table_human_evaluation_500_summary.csv, and updates research_upgrade/human_validation/human_validation_report.md. The input CSV must be present. This command reproduces the human-summary report; it does not train a model or launch the end-user chatbot.
Headline result
In the verified 500-response, single-annotator human sample (125 responses per model), Qwen2.5-3B received the highest mean overall-quality rating: 2.704/5 (95% bootstrap CI 2.536–2.872). Qwen2.5-7B scored 2.480 (2.304–2.648), HingGPT 2.192 (2.032–2.352), and Phi-3.5-mini 2.112 (1.952–2.280). The canonical human-summary CSV provides descriptive statistics and confidence intervals. Pairwise Holm-corrected p-values and effect sizes are not included in that canonical summary, so no corrected-significance claim is made here.
Results: human evaluation
Values are mean (95% bootstrap confidence interval) on a 1–5 scale; each model has n=125 rated responses per dimension. CIs are from the canonical table generated with 10,000 bootstrap resamples (seed 42).
Dimension	Qwen2.5-3B	Qwen2.5-7B	Phi-3.5-mini	HingGPT
Fluency	2.912 (2.760–3.064)	2.720 (2.544–2.896)	2.384 (2.200–2.560)	2.488 (2.304–2.672)
Code-Mixing naturalness	2.664 (2.520–2.808)	2.488 (2.336–2.648)	2.104 (1.944–2.264)	2.248 (2.080–2.416)
Hindi grammar	2.904 (2.752–3.056)	2.624 (2.456–2.792)	2.328 (2.152–2.504)	2.568 (2.384–2.752)
Prompt adherence	2.568 (2.416–2.720)	2.472 (2.312–2.640)	2.088 (1.928–2.248)	2.136 (1.984–2.296)
Spelling consistency	2.800 (2.632–2.960)	2.552 (2.384–2.712)	2.240 (2.072–2.416)	2.408 (2.224–2.592)
Overall quality	2.704 (2.536–2.872)	2.480 (2.304–2.648)	2.112 (1.952–2.280)	2.192 (2.032–2.352)


Interpretation: Qwen2.5-3B has the highest observed mean in all six dimensions in this 500-response sample. Confidence intervals and pairwise tests should be read together; overlapping CIs are not themselves a significance test.
Key figures
Generator model comparison

Figure 1. Mean human-rated quality by model; compare relative scores across the six evaluation dimensions.
Human-versus-automated-judge alignment

Figure 2. Alignment between human ratings and automated Mistral-judge scores in the calibration analysis.
E1–E10 error taxonomy

Figure 3. Distribution of E1–E10 error categories in the analyzed error records.
Project scope and benchmark
The project inventory reports:
- 277,431 continued-pretraining sequences.
- 14,601 validation utterances/sequences.
- 1,000 original benchmark prompts and 4,000 generated outputs (1,000 per model).
- An overlap-audited subset of 992 prompts after eight prompts were quarantined for moderate similarity.
- Four generator configurations: Qwen2.5-3B, Qwen2.5-7B, Phi-3.5-mini, and HingGPT.
The 1,000-prompt original benchmark, 992-prompt audited subset, 4,000-generation corpus, and 500-response human sample are different populations and must not be conflated.
Dataset source and redistribution
The project is associated with the L3Cube-HingCorpus research line. Check the source dataset's license and terms before downloading or redistributing any corpus. Do not commit restricted raw data, user-sensitive annotations, credentials, or large model weights. The repository's own code license does not override third-party dataset or model licenses.
Models and checkpoints
Model label	Project role	Checkpoint status/link
Qwen2.5-3B	Main QLoRA continued-pretraining experiment	Local checkpoint reported at models/qwen25_3b_cpt/checkpoint-17340/; base family: Qwen2.5-3B-Instruct
Qwen2.5-7B	Larger comparison	Base family: Qwen2.5-7B-Instruct; local/Hub revision must be pinned for reproduction
Phi-3.5-mini	Compact comparison	Phi-3.5-mini-instruct; inventory lists a local path, but checkpoint training provenance should be verified before claiming it was adapted in the same run
HingGPT	Hinglish-focused comparison model from L3Cube Pune	Hugging Face repository/revision: TBA


QLoRA adapter: Public Hugging Face URL: TBA.
Pairwise overall-quality comparisons
The manuscript reports the following rank-biserial effect sizes for overall quality. Positive/negative signs follow the comparison order shown in the source table. Holm-adjusted p-values are not available in the canonical human-summary CSV, so significance labels are not inferred from effect sizes. These effect sizes should not be conflated with the 500-response single-annotator descriptive sample.
Pairwise comparison	Rank-biserial effect size	Holm-adjusted p-value
Qwen2.5-3B vs Qwen2.5-7B	+0.300	TBA
Qwen2.5-3B vs HingGPT	+0.792*	TBA
Qwen2.5-3B vs Phi-3.5-mini	+0.909*	TBA


*The source table records HingGPT vs Qwen2.5-3B as −0.792 and Phi-3.5-mini vs Qwen2.5-3B as −0.909; the signs above are reversed to match the comparison order displayed here.
Judge–human correlation
For the reported human-versus-Mistral calibration analysis, overall-quality Spearman correlation was ρ = 0.184 (p = 3.57 × 10⁻⁵), with quadratic weighted kappa QWK = 0.169. These are calibration-analysis statistics and are not a claim of strong agreement.
Human-evaluation status and agreement
- Completed human ratings: 500 responses, all six dimensions populated; 125 responses per model.
- Annotator design: single-annotator study (Annotator A). A second-annotator partition is not included in the completed sample reported here.
- Inter-annotator Cohen's kappa: not reported for this study design because the canonical sample has one completed rating per response.
- Automated judge: the project inventory reports 3,990 valid Mistral-judge records and 10 invalid records for the 4,000-generation set.
Human ratings, automated judge scores, and judge-to-human alignment are distinct analyses. Consult the saved report and result tables before quoting any agreement coefficient.
Full install (training and inference)
The lightweight Quickstart installs only the packages needed to rebuild the human-rating summary. Training and local inference require a compatible PyTorch/CUDA stack and model-specific packages. Install the PyTorch build that matches your operating system, CUDA driver, and GPU, then install the model dependencies specified by the selected experiment configuration. GPU training is hardware-dependent; there is no single portable install command for every environment.
Analysis commands
Run commands from the repository root. The report-generation scripts expect the input files at the paths described below.
# Rebuild canonical human summary tables and publication figures
python research_upgrade/v3/scripts/generate_publication_figures_and_tables.py

# Recompute the human-evaluation report from the 500-rating CSV
python research_upgrade/scripts/generate_human_eval_report.py

# Compute linguistic/automatic metrics (requires the 4,000-generation CSV,
# validation data, model/tokenizer access, and dependencies)
python research_upgrade/scripts/evaluate_linguistic_and_automatic_metrics.py

These commands reproduce available analysis/reporting stages. The benchmark-generation and model-training stages are not exposed as a single portable command in this README.
Human-evaluation app
The human-rating interface entry point is research_upgrade/human_validation/app.py and uses FastAPI. From the repository root, install the app's dependencies, then start it with:
python -m uvicorn research_upgrade.human_validation.app:app --host 127.0.0.1 --port 8000
Open http://127.0.0.1:8000 to use the human-rating interface. This interface is for collecting ratings and is distinct from the end-user Hinglish chatbot.
Example prompt
A sample benchmark prompt is included in [`sample_benchmark_prompts.csv`](sample_benchmark_prompts.csv). This file illustrates the benchmark format; it is not a live chatbot transcript.
Repository structure
research_upgrade/
├── figures/                  # Research figures and publication visuals
├── human_validation/         # FastAPI rating app, validation, and rating reports
├── leakage_audit/             # Overlap audit and audited benchmark
├── paper/                     # Manuscript
├── reports/                   # Audit, methods, and analysis reports
├── scripts/                   # Evaluation, audit, reporting, and figure scripts
├── tables/                    # Human ratings, metrics, and generated tables
└── v3/
    ├── configs/               # Judge configuration
    ├── data/                  # Annotation sheets and ID mapping
    ├── figures/               # Canonical figures
    ├── paper/                 # Revised manuscript
    ├── references/             # Reference audit artifacts
    ├── reports/                # Human/statistical/judge reports
    ├── scripts/                # Recompute and validation scripts
    └── tables/                 # Canonical summaries, CIs, tests, effect sizes
Large datasets, model checkpoints, SQLite databases, and backups should not be committed to Git unless their licenses, size, and privacy implications permit redistribution.
Reproducibility and limitations
- The canonical human-summary table uses random seed 42 and 10,000 bootstrap resamples for its confidence intervals.
- Record which prompt population is being analyzed (1,000 original, 992 audited, or a subset).
- Keep raw generations, parsed judge outputs, invalid records, and exclusion reasons.
- Human study conclusions are limited by a 500-response, single-annotator sample.
- Similarity auditing cannot prove the absence of every form of benchmark contamination.
- Offline benchmark results do not establish real-world chatbot latency, safety, or user satisfaction.
Paper
The research manuscript is available at [`research_upgrade/v3/paper/hinglisheval_paper.md`](research_upgrade/v3/paper/hinglisheval_paper.md). Paper / arXiv link: TBA.
Citation
See [`CITATION.cff`](CITATION.cff) for GitHub's “Cite this repository” metadata. The project is provided under the MIT License where applicable; third-party datasets and checkpoints retain their own terms.
License
The repository metadata declares MIT licensing for project code. See LICENSE for the license text. Third-party datasets, model checkpoints, and external services remain subject to their own terms.
Author
Kancharla Vyshnavi — HinglishEval research project.
