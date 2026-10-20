# HinglishEval: A Multi-Dimensional Benchmark & LLM-as-a-Judge Reliability Study for Hindi-English Code-Mixed Generation

> **A contamination-audited evaluation framework establishing the reliability boundaries of LLM evaluators and benchmarking open-weight models on real-world Hindi-English (Hinglish) conversational text.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python: 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![Paper](https://img.shields.io/badge/Paper-Markdown%20%7C%20PDF-red.svg)](paper.md)
[![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Adapters%20%26%20Data-orange.svg)](https://huggingface.co/kancharla-vyshnavi)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/kancharla-vyshnavi/A-Multi-Dimensional-Benchmark-of-LLMs-for-Hindi-English-Code-Mixed-Generation/pulls)

---

## ⚡ Headline Results (30-Second Summary)

* **Inter-Judge Agreement:** Across 3,986 matched valid generations, Mistral-7B and Qwen2.5-3B achieve positive rank correlation but modest ordinal agreement (**QWK = 0.205 to 0.499**, Spearman $\rho = +0.243$ to $+0.474$); Spelling Consistency shows the weakest inter-judge consensus ($\kappa_w = 0.205$).
* **Human Calibration:** Mistral-7B exhibits weak human rank alignment (**Spearman $\rho = 0.184$**, $\kappa_w = 0.169$ on 500 verified calibration items). Disproving blanket $+0.85$ leniency assumptions, Mistral's Overall Quality bias is calibrated at just **$+0.098$ points** (95% CI $[-0.036, +0.232]$), acting in a strongly dimension-specific manner (lenient on spelling $+0.842$, strict on Hindi grammar $-0.534$).
* **Top Generation Errors:** The automated E1–E10 taxonomy across all 4,000 model generations reveals that failures are dominated by **E6: Prompt Misunderstanding (26.1%, 1,045 cases)**, **E8: Spelling & Transliteration Errors (21.6%, 865 cases)**, and **E7: Incomplete Responses (17.0%, 679 cases)**.
* **Human Preference vs. Edge Efficiency:** Qwen2.5-3B achieves the highest descriptive mean overall rating ($2.704 \pm 0.959$ vs $2.480 \pm 0.989$ for Qwen2.5-7B), but the difference is **not statistically significant** ($U = 8808.0$, Holm-adjusted $p = 0.1341 > 0.05$). Qwen2.5-3B is recommended for edge deployments purely due to its **$2.3\times$ lower VRAM footprint** (2.05 GB vs 4.65 GB).
* **Compact Judge Failure Mode:** Compact sub-3B evaluator **OLMo-2-1B suffered total collapse** on code-mixed syntax (awarding passing scores to 970 Python crash tracebacks, $\kappa_w = -0.0135$), proving small models cannot serve as uncalibrated zero-shot judges.

---

## 🚀 Quickstart

Run in 4 commands using a single unified requirements file:

```bash
# 1. Clone repository & set up Python 3.11 environment
git clone https://github.com/kancharla-vyshnavi/A-Multi-Dimensional-Benchmark-of-LLMs-for-Hindi-English-Code-Mixed-Generation.git
cd A-Multi-Dimensional-Benchmark-of-LLMs-for-Hindi-English-Code-Mixed-Generation
python -m venv .venv311 && source .venv311/bin/activate   # Windows: .\.venv311\Scripts\activate

# 2. Install dependencies (single file)
pip install -r requirements.txt

# 3. Reproduce paper results in 5 seconds (19 automated checks)
python validate_paper_results.py

# 4. Launch the edge Hinglish chatbot (runs locally in 2.05 GB VRAM)
python chatbot/app.py
```

---

## 📦 What's Inside

| Component | Description | Volume / Specs |
|---|---|---|
| **Dataset** | Cleaned and deduplicated Natural Hinglish Corpus (L3Cube) | 277,431 train / 14,601 val |
| **Benchmark** | Hinglish-Bench: 8-gram Jaccard audited (8 moderate near-duplicates quarantined) | 1,000 total (992 leakage-free) |
| **Models** | HingGPT (124M), Phi-3.5-mini (3.8B), Qwen2.5-3B (3.09B), Qwen2.5-7B (7.61B) | QLoRA CPT (`checkpoint-17340`) |
| **Generations** | Controlled deterministic generation (`temp=0.7`, `top_p=0.9`, `max_tokens=256`) | 4,000 balanced outputs |
| **Evaluators** | Mistral-7B-Instruct-v0.3 (Primary, 3,990 valid), Qwen2.5-3B-Instruct (Cross-val, 3,996 valid) | Matched overlap $N = 3,986$ |
| **Human Data** | Multi-annotator Likert evaluations across 6 dimensions | 500 calibrated / 4,000 double-rated |
| **Negative Audits** | Full failure logs of OLMo-2-1B collapse; API judges (GPT-4o, Claude) marked NOT RUN | Complete negative reporting |

### Research Pipeline

```text
Natural Hinglish Corpus (277K) ──► Preprocessing & Deduplication ──► QLoRA Continued Pretraining (17,340 steps)
                                                                                  │
1,000-Prompt Benchmark         ──► Controlled Generation (4,000 outputs) ◄────────┘
(992 Leakage-Free)                               │
                                                 ▼
                       ┌──────────────────────────────────────────────────┐
                       │          Multi-Dimensional LLM-as-a-Judge       │
                       │   Mistral-7B-Instruct  vs  Qwen2.5-3B-Instruct   │
                       └─────────────────────────┬────────────────────────┘
                                                 │
               ┌─────────────────────────────────┼────────────────────────────────┐
               ▼                                 ▼                                ▼
     Human Calibration (N=500)       Robustness & E1-E10 Errors        Statistical Testing (FWER)
     (rho=0.184, bias=+0.098)        (Top: E6 26.1%, E8 21.6%)         (Friedman & Wilcoxon p < 0.05)
```

---

## 📊 Results with Figures

### Figure 1: Human Evaluation Radar across 6 Dimensions
![Human Evaluation Radar](research_upgrade/figures/fig1_human_evaluation_radar_and_bars.png)
> **Takeaway:** Qwen2.5-3B achieves the highest descriptive human ratings across fluency and overall quality, though pairwise superiority over Qwen2.5-7B remains statistically non-significant ($p_{\text{adj}} = 0.1341$).

### Figure 2: Human Calibration vs. Mistral-7B Judge Alignment
![Human vs Mistral Judge Comparison](research_upgrade/figures/fig3_human_vs_mistral_judge_comparison.png)
> **Takeaway:** Mistral-7B shows positive rank correlation ($\rho = +0.184$) but exhibits dimension-specific bias (strict on Hindi grammar $-0.534$, lenient on spelling $+0.842$), disproving uniform leniency assumptions.

### Figure 3: Code-Mixing Index (CMI) Distribution
![Code-Mixing Distribution](research_upgrade/figures/fig4_das_gamback_cmi_distribution.png)
> **Takeaway:** Qwen models maintain balanced Hindi-English code-mixing ($CMI \approx 20\text{--}30$), whereas HingGPT shows collapsed bilingual distributions and severe unigram looping.

### Figure 4: Information-Theoretic Compression & Lexical Diversity
![Compression and Lexical Diversity](research_upgrade/figures/fig5_compression_and_lexical_diversity.png)
> **Takeaway:** Qwen2.5-7B achieves highest lexical diversity ($Distinct\text{-}2 = 0.853$), but elevated diversity does not inherently yield higher human overall quality.

### Figure 5: E1–E10 Error Taxonomy Breakdown
![Error Taxonomy Breakdown](research_upgrade/figures/fig6_e1_e10_error_taxonomy_breakdown.png)
> **Takeaway:** Generation failures are heavily dominated by E6 Prompt Misunderstanding (26.1%) and E8 Spelling Inconsistencies (21.6%), while factual hallucinations (E9) require external KG verifiers.

### Figure 6: Evaluator Robustness Under Rubric Perturbations
![Robustness Perturbation Degradation](research_upgrade/figures/fig7_robustness_perturbation_degradation.png)
> **Takeaway:** Minor rubric phrasing perturbations alter LLM judge scores by up to 0.41 points, demonstrating the sensitivity of uncalibrated automated grading.

### Figure 7: Benchmark Data Contamination Audit
![Data Leakage and Jaccard Overlap](research_upgrade/figures/fig8_data_leakage_jaccard_overlap.png)
> **Takeaway:** 8-gram Jaccard auditing quarantined 8 moderate near-duplicates ($0.80 \le J < 0.90$) to establish a verified 992-item leakage-free evaluation benchmark.

---

## 🔬 Method (Summary)

* **Evaluation Dimensions:** Six dimensions rated on a 1–5 Likert scale: *Fluency*, *Code-Mixing Naturalness*, *Hindi Grammar*, *Prompt Adherence*, *Spelling Consistency*, and *Overall Quality*.
* **Evaluators & Audits:** Primary judge: Mistral-7B-Instruct-v0.3 (3,990 valid); Cross-validation: Qwen2.5-3B-Instruct (3,996 valid); Overlap $N = 3,986$. Compact evaluator OLMo-2-1B failed completely (970 crash tracebacks passed) and was excluded. Frontier API judges (GPT-4o-mini, Claude-3.5-Haiku) were prepared but marked NOT RUN due to API quota constraints.
* **Statistical Testing:** Non-parametric Friedman repeated-measures tests and paired Wilcoxon signed-rank tests across $N = 990$ complete benchmark blocks with Holm-Bonferroni FWER control; independent two-sided Mann-Whitney $U$ tests with Holm correction for disjoint human calibration samples ($N = 125$/model). *(Full theoretical derivations in [`paper.md`](paper.md)).*

---

## ⚠️ Limitations

1. **Human Evaluation Scale:** While 500 items were rigorously calibrated by language experts, the larger 4,000 double-annotation pass showed session-level fatigue and low/negative inter-annotator agreement ($\alpha < 0$), reinforcing that LLM judges require careful per-dimension calibration rather than blind trust.
2. **Zero-Frequency Hallucination Bounds (E9):** E9 yielded 0 automated detections because heuristic classifiers cannot verify world knowledge without external knowledge-graph tools; factual hallucinations occurred in reality but went unflagged.
3. **Romanized Script Focus:** The benchmark targets Latin-script Romanized Hinglish; Devanagari script mixing was observed only as incidental transliteration intrusions rather than intentional dual-script composition.
4. **Lineage Evaluation Bias:** Qwen2.5-3B-Instruct shares model architecture and tokenizer lineage with two generator models (Qwen2.5-3B and Qwen2.5-7B), creating a potential evaluation bias.
5. **Frontier API Evaluators:** Proprietary models (GPT-4o-mini, Claude-3.5-Haiku) could not be executed due to API credential and quota limits; all conclusions are bounded by open-weight evaluators.

---

## 📁 Repository Structure

```text
HinglishEval/
├── chatbot/                 # Standalone terminal chatbot (2.05 GB VRAM)
├── data/benchmarks/         # hinglish_bench_1000.csv & leakage-free subsets
├── models/                  # QLoRA CPT adapter checkpoints (checkpoint-17340)
├── outputs/controlled_1000/ # 4,000 model generations & judge rating logs
├── research_upgrade/
│   ├── figures/             # Publication PNG charts & figures
│   ├── scripts/             # Qwen judge, table generators, & audit scripts
│   └── tables/              # Canonical CSV publication tables
├── src/evaluation/          # Evaluation metrics, CMI, and E1-E10 detectors
├── paper.md                 # Full research manuscript
├── requirements.txt         # Single unified pip requirements
└── validate_paper_results.py# Fast 19-check scientific reproduction script
```

---

## 🔁 Reproducibility

* **Deterministic Random Seeds:** Seed `42` was strictly fixed across benchmark sampling, train/validation splitting, and deterministic model generation (`temp=0.7`, `top_p=0.9`, `repetition_penalty=1.05`).
* **Hardware & Runtime Environment:** Python 3.11.9, PyTorch 2.14.0+cu132, Transformers 5.17.0, PEFT 0.21.0, bitsandbytes 4-bit NF4 precision on NVIDIA RTX 4050 (6,141 MiB VRAM).
* **Key Reproduction Scripts:**
  * `python validate_paper_results.py` — Verifies all 19 empirical claims, data integrity, and statistical tests in seconds.
  * `python research_upgrade/scripts/generate_scientific_tables_and_figures.py` — Regenerates all publication figures and tables from raw logs.
  * `python research_upgrade/scripts/run_qwen_judge_evaluation.py` — Re-runs cross-validation judging on Qwen2.5-3B.
  * `python chatbot/app.py --test` — Runs unit tests on the edge conversational chatbot.
* **Pretrained Weights & Checkpoints:**
  * Base models: [`Qwen/Qwen2.5-3B-Instruct`](https://huggingface.co/Qwen/Qwen2.5-3B-Instruct), [`Qwen/Qwen2.5-7B-Instruct`](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct), [`microsoft/Phi-3.5-mini-instruct`](https://huggingface.co/microsoft/Phi-3.5-mini-instruct).
  * QLoRA CPT Adapter Checkpoints (`checkpoint-17340`): [Hugging Face Hub (`kancharla-vyshnavi`)](https://huggingface.co/kancharla-vyshnavi).

---

## 📑 Citation & Contact

If you find HinglishEval useful in your research or applications, please cite:

```bibtex
@article{kancharla2026hinglisheval,
  title={HinglishEval: Multi-Dimensional LLM-as-a-Judge Reliability and Benchmark for Hindi-English Code-Mixed Generation},
  author={Kancharla, Vyshnavi},
  journal={arXiv preprint},
  year={2026},
  url={https://github.com/kancharla-vyshnavi/A-Multi-Dimensional-Benchmark-of-LLMs-for-Hindi-English-Code-Mixed-Generation}
}
```

* **Manuscript:** Full research paper available in [`paper.md`](paper.md) and [`HinglishEval_Output_Tables.pdf`](HinglishEval_Output_Tables.pdf).
* **License:** Released under the [MIT License](LICENSE).
* **Contact & Questions:** For feedback or inquiries, open an issue or pull request on [GitHub](https://github.com/kancharla-vyshnavi/A-Multi-Dimensional-Benchmark-of-LLMs-for-Hindi-English-Code-Mixed-Generation).
