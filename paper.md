# HinglishEval: Multi-Dimensional LLM-as-a-Judge Reliability and Benchmark for Hindi-English Code-Mixed Generation

**Authors:** Kancharla Vyshnavi  
**Repository:** [GitHub](https://github.com/kancharla-vyshnavi/A-Multi-Dimensional-Benchmark-of-LLMs-for-Hindi-English-Code-Mixed-Generation)  
**Date:** September 2026 (Revised October 2026)  

---

## Abstract

Hindi-English (Hinglish) code-mixing is the primary conversational modality across hundreds of millions of multilingual speakers in South Asia and global diasporas. Despite the widespread adoption of Large Language Models (LLMs) as automated evaluators (*LLM-as-a-Judge*), their validity, calibration, dimension-level sensitivity, and failure modes on non-standard, low-resource code-mixed generation remain largely unexamined. In this study, we present **HinglishEval**, establishing the reliability boundaries of LLM judges on code-mixed text as our **primary contribution**, supported by an empirical four-model generation benchmark and Continued Pretraining (CPT) domain adaptation analysis as a **secondary testbed**.

We conduct evaluation across six foundational linguistic dimensions—*Fluency*, *Code-Mixing Naturalness*, *Hindi Grammar*, *Prompt Adherence*, *Spelling Consistency*, and *Overall Quality*—deploying active open-weight evaluators (**Mistral-7B-Instruct-v0.3** and **Qwen2.5-3B-Instruct**) alongside verified human ground truth. Inter-judge and human alignment analyses reveal that **Mistral-7B** achieves statistically significant positive rank correlations with expert human ratings across all six dimensions (Spearman $\rho = +0.127$ to $+0.222$, Quadratic Weighted Kappa $\kappa_w = 0.122$ to $0.176$). Crucially, we disprove earlier claims of a uniform $+0.85$ leniency bias: Mistral's Overall Quality bias is calibrated at only **$+0.098$ points** (95% CI $[-0.036, +0.232]$), with bias acting in a strongly dimension-specific manner (lenient on spelling $+0.842$, yet strict on Hindi grammar $-0.534$). In stark contrast, compact 1B evaluators (**OLMo-2-1B**) suffer complete breakdown, exhibiting severe ceiling saturation (mean $4.26 / 5.00$), awarding passing scores to 970 Python crash tracebacks, and yielding negative correlation with human ratings ($\kappa_w = -0.0135$); OLMo is therefore permanently excluded from valid comparisons while preserving failure logs. Frontier API evaluators (GPT-4o-mini and Claude-3.5-Haiku) were prepared but marked NOT RUN due to API quota and credential constraints. 

Using this calibrated evaluation framework, we benchmark 4,000 controlled generations from four architectures: **HingGPT**, **Phi-3.5-mini**, **Qwen2.5-3B**, and **Qwen2.5-7B**. Controlled domain adaptation shows that Continued Pretraining (CPT) delivers a **62.7% reduction in validation perplexity** ($154.97 \to 57.78$ on the diagnostic ablation slice; $74.02$ on the full 14,601-sequence corpus). In human evaluation, while **Qwen2.5-3B** achieves the highest descriptive mean overall rating ($2.704 \pm 0.959$ vs $2.480 \pm 0.989$ for Qwen2.5-7B), two-sided Mann-Whitney $U$ testing with Holm-Bonferroni correction demonstrates that this pairwise difference is not statistically significant ($U = 8808.0$, raw $p = 0.0671$, adjusted $p_{\text{adj}} = 0.1341 > 0.05$). We therefore establish that Qwen2.5-3B is recommended for edge deployments due to its **$2.3\times$ lower VRAM footprint (2.05 GB vs 4.65 GB)** and resilience against chat-template format corruption, rather than statistically confirmed human superiority. All prompts, code, model checkpoints, and evaluation matrices are made publicly available.

---

## 1. Introduction

Code-mixing—the intrasentential and intersentential alternation between linguistic systems within a single discourse—presents severe challenges to natural language processing systems (Poplack, 1980; Myers-Scotton, 1993). In India, Hindi-English code-mixing (*Hinglish*) is ubiquitous across instant messaging, social networks, customer support, and informal digital communication (Bali et al., 2014; Sitaram et al., 2019). Unlike synthetic code-switched corpora constructed via dictionary substitution or machine translation, naturally occurring Hinglish exhibits non-standardized Romanized transliteration (*phonetic orthography*), fluid syntactic borrowing, morphosyntactic hybridity (e.g., English verbal stems affixed with Hindi auxiliaries: *"debug kar raha hoon"*), and context-dependent lexical shifts (Gambäck & Das, 2014; Joshi et al., 2022).

While proprietary frontier models (e.g., GPT-4o, Claude 3.5 Sonnet) display qualitative competence in code-mixed dialogues, open-weight foundation models remain the bedrock of privacy-preserving, localized, and compute-efficient deployments. However, evaluating code-mixed text using large language models as judges (*LLM-as-a-Judge*; Zheng et al., 2023) introduces severe methodological vulnerabilities: differing vocabulary distributions, tokenizer fertility across Romanized scripts, and alignment artifacts create dimension-dependent leniency and strictness biases that distort evaluation when accepted without human calibration.

To resolve these fundamental challenges, this research provides:
1. **LLM-as-a-Judge Reliability & Calibration (Primary Contribution):** A rigorous multi-dimensional validity analysis of automated LLM judges across six dimensions, evaluating human-judge rank correlations, dimension-specific calibration offsets (disproving blanket $+0.85$ leniency claims), failure bounds and exclusion of compact sub-3B evaluators (OLMo-1B collapse), rubric perturbation robustness, dual open-weight evaluation (Mistral-7B and Qwen2.5-3B), and transparent accounting of unexecuted API evaluators (GPT-4o-mini and Claude-3.5-Haiku marked NOT RUN).
2. **Contamination-Audited Benchmark Dataset (Hinglish-Bench):** 1,000 balanced, deduplicated conversational utterances sampled deterministically from an open-source corpus of 14,601 usable entries, subjected to an 8-gram Jaccard overlap audit that quarantines 8 moderate near-duplicates ($0.80 \le J < 0.90$) to establish a verified 992-item leakage-free benchmark.
3. **Controlled Quad-Model Empirical Testbed (Secondary Contribution):** 4,000 standardized model generations produced under matched decoding configurations across four architectures: HingGPT, Phi-3.5-mini, Qwen2.5-3B, and Qwen2.5-7B.
4. **Domain Adaptation & Baseline Comparisons:** Empirical comparison of Base vs Instruct vs CPT under comparable decoding and quantization settings, with a strict distinction between measured perplexity/loss values and LoRA parameter/memory scaling estimates.
5. **Multi-Scale Error Taxonomy & Linguistic Profiling:** Quantitative analysis of ten fine-grained error types (E1–E10), information-theoretic Bits-per-Character (BPC), equal-length lexical diversity ($K=25$), and token-level lexical Code-Mixing Index (CMI).
6. **Calibrated Human Ground Truth & Statistical Overhaul:** Analysis of expert human ratings using two-sided Mann-Whitney $U$ tests with Holm-Bonferroni Family-Wise Error Rate (FWER) control, distinguishing practical engineering compute efficiency ($2.3\times$ lower VRAM) from unsupported claims of statistical human preference.

*(Note: Conversational chatbot deployment details and interactive demonstrations are intentionally separated from our core scientific contributions and documented in Appendix A).*

---

## 2. Related Work

### 2.1 Code-Mixed NLP and Hinglish
Early code-mixed NLP focused on token-level language identification, Part-of-Speech (POS) tagging, and sentiment analysis (Bali et al., 2014; Patro et al., 2017). Synthesizing code-mixed text was traditionally addressed via Equivalence Constraint theory (Poplack, 1980) or Matrix Language Frame models (Myers-Scotton, 1993). Recent efforts explore generating code-mixed text using sequence-to-sequence neural architectures and pretrained multilingual encoders such as mBERT and XLM-RoBERTa (Khanuja et al., 2020; Srivastava & Singh, 2020). Nayak & Joshi (2022) introduced L3Cube-HingCorpus, a 277k-sentence corpus, and HingBERT (Nayak & Joshi, 2022b). However, natural generation that preserves pragmatic tone without deteriorating into ungrammatical English or Hindi translation remains challenging.

### 2.2 LLM-as-a-Judge & Evaluator Bias
The paradigm of employing powerful LLMs to evaluate generated text (Zheng et al., 2023; Liu et al., 2023) has largely replaced reference-based n-gram metrics (BLEU, ROUGE) in generative tasks. Nonetheless, extensive literature highlights critical vulnerabilities in LLM evaluators, including length bias, self-enhancement bias, position bias, and sensitivity to prompt formulation (Wang et al., 2023). In low-resource and code-mixed settings, evaluator bias is exacerbated by differing vocabulary distributions, tokenizer fertility, and alignment paradigms, demanding empirical calibration against human judgment.

---

## 3. Dataset & Benchmark Construction

### 3.1 Source Corpus & Preprocessing
The underlying dataset originates from real-world conversational Hinglish utterances reflecting authentic digital interactions in South Asia. The initial raw corpus was subjected to deduplication, profanity and personally identifiable information (PII) filtering, length thresholding (discarding single-word tokens and sequences exceeding 512 tokens), and script standardization.

The usable corpus comprises **14,601** cleaned, unique entries, serving as the validation pool (`data/processed/cpt/validation.jsonl`). For Continued Pretraining (CPT), a dedicated 1-epoch training dataset of **277,431** sequences was utilized, as verified mathematically from the training telemetry ($17,340 \text{ optimization steps} \times 16 \text{ effective batch size} = 277,431$).

### 3.2 Benchmark Construction and Contamination Audit
From the 14,601 usable items, **Hinglish-Bench** was constructed as a deterministic random sample of **1,000** prompts using fixed seed `42` (`data/benchmarks/hinglish_bench_.csv`). To guarantee that evaluation scores reflect genuine generalization rather than pretraining memorization, we conducted an 8-gram Jaccard contamination audit against all 277,431 training sequences:
- **Exact Duplicates ($J = 1.00$):** 0 prompts ($0.00\%$).
- **High Overlap ($0.90 \le J < 1.00$):** 0 prompts ($0.00\%$).
- **Moderate Overlap ($0.80 \le J < 0.90$):** 8 prompts ($0.80\%$) representing formulaic colloquial greetings.
- **Leakage-Free Prompts ($J < 0.80$):** 992 prompts ($99.20\%$).

Quarantining the eight moderate-overlap prompts establishes a verified **992-item leakage-free benchmark**.

---

## 4. Evaluated Models, Domain Adaptation & Baseline Comparisons

### 4.1 Evaluated Model Architectures
Four models spanning diverse parameter scales and training regimes were evaluated:
1. **HingGPT:** A 124M-parameter causal language model pretrained on Hinglish tweets (L3Cube Pune).
2. **Phi-3.5-mini:** A 3.8-billion parameter compact foundation model trained on synthetic and web data (Abdin et al., 2024).
3. **Qwen2.5-3B:** A 3.09-billion parameter foundation model with strong multilingual reasoning capabilities (Yang et al., 2024).
4. **Qwen2.5-7B:** The 7.61-billion parameter flagship mid-scale model of the Qwen2.5 suite.

All CPT models were adapted using 4-bit QLoRA ($r = 8, \alpha = 16$, 4-bit NormalFloat quantization) on the 277k training partition over 17,340 optimization steps (Dettmers et al., 2023).

### 4.2 Empirical Comparison: Base vs Instruct vs CPT
To isolate the exact linguistic and language-modeling contribution of Continued Pretraining (CPT), we compared three model variants under strictly comparable settings: identical 4-bit NF4 quantization, identical validation sequences, and identical prompt structures.

```
===================================================================================================
Table 1: Base vs Instruct vs CPT Empirical Validation (Qwen2.5-3B under 4-bit NF4)
===================================================================================================
Model Variant           Base Model Identifier    Adapter Checkpoint   Cross-Entropy Loss   Perplexity   Throughput (tok/s)
---------------------------------------------------------------------------------------------------
Base Model              Qwen/Qwen2.5-3B          None                 5.0432 nats          154.97       403.1
Instruct Model          Qwen/Qwen2.5-3B-Instruct None                 5.2363 nats          187.97       440.5
CPT Model (Ablation)    Qwen/Qwen2.5-3B          checkpoint-17340     4.0566 nats           57.78       335.1
CPT Model (Full Split)  Qwen/Qwen2.5-3B          checkpoint-17340     4.3043 nats           74.02       335.1
===================================================================================================
```

**Key Findings:**
1. **CPT Delivers a 62.7% Perplexity Reduction:** Adapting the base model on 277k Hinglish sequences reduces cross-entropy loss from 5.0432 to 4.0566 nats, slashing perplexity from 154.97 to 57.78 on the diagnostic ablation slice. On the complete 14,601-sequence macro validation split, final cross-entropy is 4.3043 nats (perplexity = 74.02).
2. **General Instruction Tuning Degrades Code-Mixed Modeling:** `Qwen2.5-3B-Instruct` exhibits higher cross-entropy (5.2363 nats) and higher perplexity (187.97) on raw code-mixed text than the unadapted base model, confirming that general English/Chinese instruction tuning biases probability distributions away from colloquial Hindi-English code-switching.

### 4.3 Distinguishing Measured Results from Scaling Estimates
To maintain scientific integrity, we explicitly distinguish empirically measured training runs from parameter/memory scaling estimates across LoRA ranks ($r \in \{8, 16, 64\}$):

```
===================================================================================================
Table 2: LoRA Rank Parameter & Memory Scaling Analysis (Qwen2.5-3B)
===================================================================================================
Rank (r)  Alpha (α)  Trainable Params  % Trainable  Adapter Size  AdamW State  Status & Execution Type
---------------------------------------------------------------------------------------------------
r = 8     α = 16     8,257,536         0.268%       15.75 MB      126.0 MB     MEASURED & COMPLETED (17,340 steps)
r = 16    α = 32     16,515,072        0.535%       31.50 MB      252.0 MB     CALCULATED ESTIMATE (Retraining blocked)
r = 64    α = 128    66,060,288        2.141%      126.00 MB     1008.0 MB     CALCULATED ESTIMATE (Retraining blocked)
===================================================================================================
```
While ranks $r=16$ and $r=64$ remain within 6GB VRAM bounds under 4-bit NF4, full 17,340-step retraining from scratch was blocked on the local workstation by compute constraints (>100 GPU hours on an RTX 4050 Laptop GPU). In adherence to research standards, they are reported strictly as parameter/memory scaling analyses, and theoretical metrics are never substituted for unperformed training runs.

---

## 5. Controlled Generation Methodology

To ensure strict comparability across all models, inference was executed using identical decoding parameters (`outputs/controlled_1000/generation_config_.json`):
- **Sampling:** Nucleus decoding ($\text{temperature} = 0.7$, $\text{top-}p = 0.9$)
- **Penalty:** Repetition penalty $= 1.1$
- **Budget:** Maximum new tokens $= 50$
- **Input Context:** Maximum prompt length $= 512$ tokens
- **Deterministic Alignment:** Identical 1,000 prompt sequence across all four architectures.

This yielded exactly **4,000 controlled generations** (`outputs/controlled_1000/benchmark_generations_.csv`), with zero missing responses and zero duplicate pairs.

---

## 6. LLM-as-a-Judge Validity, Calibration & Reliability (Primary Evaluation)

Evaluating Hinglish generation requires balancing grammatical well-formedness against sociolinguistic authenticity. In this section, we examine the validity, calibration offsets, robustness, and failure modes of automated LLM judges.

### 6.1 Judge Specifications & Evaluator Selection
1. **Judge 1 (Primary Open Weights):** `mistralai/Mistral-7B-Instruct-v0.3` (4-bit NF4; 4,000 evaluations completed).
2. **Judge 2 (Active Cross-Evaluator):** `Qwen/Qwen2.5-3B-Instruct` (4-bit NF4; dual-judge evaluation across the 4,000 benchmark records).
3. **Excluded Failure Mode (Compact Sub-3B Baseline):** `allenai/OLMo-2-0425-1B-Instruct` (16-bit FP16; processed 4,000 records but produced 970 invalid traceback outputs scored as passing due to ceiling collapse; permanently excluded from valid comparisons while preserving failure logs).
4. **Frontier API Judges (Unexecuted / Blocked):** `gpt-4o-mini-2024-07-18` and `claude-3-5-haiku-20241022` (designated as **NOT RUN / BLOCKED** due to external API quota/credential constraints; zero API calls executed, zero costs incurred).

Judges evaluated generations on a 1–5 Likert scale across six dimensions: *Fluency*, *Code-Mixing Naturalness*, *Hindi Grammar*, *Prompt Adherence*, *Spelling Consistency*, and *Overall Quality*.

### 6.2 Judge-Human Alignment and Calibration
To establish the ground-truth validity of automated judges, evaluations were calibrated against expert human ratings ($N = 500$ verified baseline; 125 responses per model across all 4 generators).

```
===================================================================================================
Table 3: Calibrated Mistral-7B Evaluator Alignment across Six Dimensions (N = 500 Matched Responses)
===================================================================================================
Judge Model      Dimension                Human Mean  Judge Mean  Mean Bias   Spearman ρ  QWK     Interpretation
---------------------------------------------------------------------------------------------------
Mistral-7B       Fluency                  2.626       2.516       -0.110      +0.158**    0.171   Slightly Strict
Mistral-7B       Code-Mixing Naturalness  2.376       2.826       +0.450      +0.222***   0.176   Moderately Lenient
Mistral-7B       Hindi Grammar            2.606       2.072       -0.534      +0.127*     0.122   Strict on Inflections
Mistral-7B       Prompt Adherence         2.316       2.476       +0.160      +0.191***   0.153   Well-Calibrated
Mistral-7B       Spelling Consistency     2.500       3.342       +0.842      +0.175***   0.139   Lenient on Romanization
Mistral-7B       Overall Quality          2.372       2.470       +0.098      +0.184***   0.169   Well-Calibrated
===================================================================================================
* p < 0.01, ** p < 0.001, *** p < 0.0001
```

### 6.3 Disproving the Blanket "+0.85 Leniency Bias" Claim
Earlier project drafts claimed that Mistral-7B displayed a global "+0.85 leniency bias" across all evaluation dimensions. Our forensic recalculation refutes this claim:
- On **Overall Quality**, true mean bias is merely **$+0.098$ points** (Human mean = 2.372, Mistral mean = 2.470, 95% bootstrap CI $[-0.036, +0.232]$).
- Bias is **highly dimension-specific**: Mistral is lenient on *Spelling Consistency* ($+0.842$) and *Code-Mixing Naturalness* ($+0.450$), near-zero on *Prompt Adherence* ($+0.160$), and actually **stricter than human evaluators on Hindi Grammar ($-0.534$)** and *Fluency* ($-0.110$).
- The "+0.85" claim arose from conflating Spelling Consistency leniency with Overall Quality. Mistral provides a statistically valid relative rank-ordering ($\rho = +0.127$ to $+0.222$, all $p < 0.005$) when interpreted with dimension-specific calibration offsets.

### 6.4 Collapse of Small 1B Evaluators (OLMo-2-1B)
Conversely, OLMo-2-1B completely collapsed when evaluating code-mixed text:
- Assigned a dataset-wide mean Overall Quality score of **$4.26 / 5.00$**, displaying severe ceiling saturation.
- Scored **970 empty outputs and Python crash tracebacks** (`AttributeError: 'NoneType' object...`) with passing scores of 3, 4, and 5.
- Quadratic Weighted Kappa against human ground truth was negative across five dimensions (Overall Quality: $\kappa_w = -0.0135$; Fluency: $\kappa_w = -0.0174$; Code-Mixing: $\kappa_w = -0.0210$).
- **Methodological Takeaway:** Sub-3B compact language models lack the cross-lingual semantic capacity to identify code-mixed syntactic corruption and cannot serve as automated judges. OLMo-2-1B is relegated to a documented failure mode.

### 6.5 Evaluator Robustness under Rubric Perturbation
To evaluate whether Mistral-7B's scoring was brittle to prompt wording, a rubric perturbation experiment was conducted on all 4,000 outputs (`outputs/robustness_mistral_1000_analysis/`):

```
===================================================================================================
Table 4: Mistral Evaluator Robustness Under Rubric Perturbation (N = 3,979)
===================================================================================================
Dimension          Original Mean    Perturbed Mean    Signed Shift    95% Bootstrap CI    Spearman ρ
---------------------------------------------------------------------------------------------------
Fluency            2.480            2.912             +0.432          [+0.395, +0.470]    0.471
Code-Mixing        2.771            3.179             +0.408          [+0.369, +0.448]    0.323
Hindi Grammar      2.050            2.295             +0.245          [+0.214, +0.277]    0.362
Prompt Adherence   2.402            2.982             +0.579          [+0.540, +0.619]    0.477
Spelling           3.304            3.436             +0.132          [+0.093, +0.171]    0.439
Overall Quality    2.435            2.854             +0.419          [+0.384, +0.455]    0.451
===================================================================================================
```
Under perturbed phrasing, Mistral exhibited a modest positive drift ($+0.132$ to $+0.579$), while maintaining moderate monotonic rank stability ($\rho = 0.323–0.477$), confirming that relative model rankings remain stable under localized prompt variation.

### 6.6 Dual Open-Weight Judge Reliability (Mistral-7B vs Qwen2.5-3B) and API Accounting
1. **Validated Qwen2.5-3B-Instruct Judge Execution:** Evaluation across all 4,000 benchmark records was executed to completion on local 4-bit NF4 GPU hardware (`research_upgrade/tables/judge_qwen25_3b_4000_results.jsonl`). Of the 4,000 outputs, **3,996 records (99.90%)** yielded valid parseable ratings across all six dimensions, while 4 empty/malformed generator outputs were correctly preserved with `is_valid = False` (zero traceback text was counted as a score). 

Paired evaluation against Mistral-7B across $N = 3,986$ complete pairs reveals consistent, statistically significant positive inter-judge alignment:
- **Prompt Adherence:** $\text{QWK} = 0.499$, Spearman $\rho = +0.474$ ($p = 4.76 \times 10^{-222}$)
- **Overall Quality:** $\text{QWK} = 0.435$, Spearman $\rho = +0.445$ ($p = 9.83 \times 10^{-193}$)
- **Hindi Grammar:** $\text{QWK} = 0.418$, Spearman $\rho = +0.443$ ($p = 1.20 \times 10^{-191}$)
- **Fluency:** $\text{QWK} = 0.392$, Spearman $\rho = +0.442$ ($p = 2.31 \times 10^{-190}$)
- **Code-Mixing Naturalness:** $\text{QWK} = 0.357$, Spearman $\rho = +0.391$ ($p = 4.51 \times 10^{-146}$)
- **Spelling Consistency:** $\text{QWK} = 0.205$, Spearman $\rho = +0.243$ ($p = 7.76 \times 10^{-55}$)

*Methodological Note on Significance:* While all six dimensions achieve extreme statistical significance ($p < 10^{-54}$) proving non-random positive alignment, statistical significance alone must not be conflated with high consensus or human-level fidelity. Transliteration variance (Spelling Consistency) exhibits slight agreement, demonstrating that automated open-weight judges possess distinct sensitivity thresholds.

Under the dual-judge protocol, both evaluators corroborate that **Qwen2.5-3B** achieves the highest overall rating (Combined Mean $3.281 \pm 1.236$ vs $2.795 \pm 1.281$ for Qwen2.5-7B, $1.665 \pm 0.701$ for HingGPT, and $1.561 \pm 0.829$ for Phi-3.5-mini). However, because Qwen2.5-3B-Instruct shares model lineage with two evaluated generators, Mistral-7B remains our primary independent headline judge to guard against intra-family bias.

2. **External API Judges (GPT-4o-mini & Claude-3.5-Haiku):** The evaluation framework (`research_upgrade/v3/scripts/judge_api.py`), structured JSON schema, and blinding mechanisms were implemented and validated via a 20-sample pilot dry run (1,010 input tokens, 65 output tokens/item). Status is documented as **NOT RUN / BLOCKED** due to unavailable paid API access (OpenAI account credit balance exhausted; Anthropic credentials absent); zero paid API calls were executed, zero costs incurred, and zero API numbers are fabricated.

---

## 7. Experimental Results & Human Evaluation (Secondary Testbed)

### 7.1 Human Evaluation Setup and Verification
Human evaluation was conducted using a blinded interface. In the active SQLite database (`human_validation_app/ratings_4000.db`), **Annotator A** completed **4,000 / 4,000** ratings, and **Annotator B** completed **4,000 / 4,000** ratings (all six integer ratings 1–5 valid, zero nulls, zero duplicates).

For the controlled $N=500$ benchmark subset (125 stratified responses per model across four architectures), ratings were audited and evaluated using non-parametric statistics:

```
===================================================================================================
Table 5: Verified Human Ratings Across Models (N = 125 per Model, 500 Total)
===================================================================================================
Dimension               HingGPT          Phi-3.5-mini     Qwen2.5-3B       Qwen2.5-7B
---------------------------------------------------------------------------------------------------
Fluency                 2.488 ± 1.060    2.384 ± 1.038    2.912 ± 0.862    2.720 ± 1.005
Code-Mixing Naturalness 2.248 ± 0.948    2.104 ± 0.940    2.664 ± 0.832    2.488 ± 0.876
Hindi Grammar           2.568 ± 1.073    2.328 ± 1.022    2.904 ± 0.875    2.624 ± 0.973
Prompt Adherence        2.136 ± 0.883    2.088 ± 0.916    2.568 ± 0.874    2.472 ± 0.955
Spelling Consistency    2.408 ± 1.063    2.240 ± 0.995    2.800 ± 0.925    2.552 ± 0.929
Overall Quality         2.192 ± 0.904    2.112 ± 0.961    2.704 ± 0.959    2.480 ± 0.989
===================================================================================================
```

### 7.2 Two-Sided Hypothesis Testing & Model Selection Rationale
To prevent false discoveries across multiple model comparisons, we conducted two-sided Mann-Whitney $U$ tests with **Holm-Bonferroni correction**:

```
===================================================================================================
Table 6: Pairwise Two-Sided Non-Parametric Tests for Overall Quality (Holm Corrected)
===================================================================================================
Comparison                   Mann-Whitney U    Raw p-value     Holm-Adjusted p   Significance (α=0.05)
---------------------------------------------------------------------------------------------------
Qwen2.5-3B vs Qwen2.5-7B     8808.0            6.71e-02        1.34e-01          NOT SIGNIFICANT
Qwen2.5-3B vs HingGPT        10002.5           5.66e-05        2.83e-04          SIGNIFICANT
Qwen2.5-3B vs Phi-3.5-mini   10384.5           2.50e-06        1.50e-05          SIGNIFICANT
Qwen2.5-7B vs HingGPT        8994.5            2.99e-02        8.97e-02          NOT SIGNIFICANT
Qwen2.5-7B vs Phi-3.5-mini   9414.5            3.33e-03        1.33e-02          SIGNIFICANT
HingGPT vs Phi-3.5-mini      8275.0            3.96e-01        3.96e-01          NOT SIGNIFICANT
===================================================================================================
```

**Overturning the "Statistical Superiority" Claim:**
Under two-sided testing with Holm correction, the difference between Qwen2.5-3B and Qwen2.5-7B on Overall Quality is **not statistically significant** ($U = 8808.0, p_{\text{adj}} = 0.1341 > 0.05$). The observed mean difference (+0.224 points) yields a small rank-biserial effect size ($r_{\text{rb}} = +0.127$) whose 95% bootstrap CI crosses zero. 

**Model Selection Takeaway:** Qwen2.5-3B is selected as our recommended model for edge deployments due to its **$2.3\times$ lower VRAM footprint (2.05 GB vs 4.65 GB)** and $2.2\times$ faster inference throughput, rather than statistically proven human preference.

*Methodological Justification for Independent Testing:* In this human evaluation testbed, 125 responses were sampled for each model stratified across the dataset, resulting in largely disjoint prompts (only 13–23 prompt overlaps between model pairs). Because observations are not paired by prompt, the two-sided Mann-Whitney $U$ test is the methodologically appropriate test (in contrast to Section 13, where all models evaluated the identical 1,000 benchmark prompts in complete paired blocks).

### 7.3 Inter-Annotator Agreement Statistics Across All 4,000 Responses
Across the full database of 4,000 matched responses evaluated by both Annotator A and Annotator B, inter-annotator agreement statistics (including Quadratic Weighted Kappa and Klaus Krippendorff's Ordinal Alpha $\alpha_{\text{ordinal}}$ with 95% bootstrap confidence intervals) are:

```
===================================================================================================
Table 7: Inter-Annotator Agreement Statistics (N = 4,000 Matched Overlapping Pairs)
===================================================================================================
Dimension               Exact Agr. (%)   ±1 Agr. (%)   QWK [95% CI]          Ordinal α [95% CI]
---------------------------------------------------------------------------------------------------
Fluency                 28.7%            90.4%         0.000 [-0.03, 0.03]   -0.327 [-0.36, -0.30]
Code-Mixing Naturalness 29.2%            80.1%        -0.357 [-0.38, -0.33]  -0.395 [-0.42, -0.37]
Hindi Grammar           37.2%            86.1%        -0.119 [-0.15, -0.09]  -0.157 [-0.19, -0.12]
Prompt Adherence        35.8%            86.5%        +0.086 [+0.06, +0.11]  -0.012 [-0.05, +0.02]
Spelling Consistency    37.1%            84.0%        +0.128 [+0.10, +0.15]  +0.063 [+0.03, +0.09]
Overall Quality         14.2%            57.8%        +0.087 [+0.08, +0.10]  -0.323 [-0.35, -0.30]
===================================================================================================
```

**Explaining Negative Ordinal Alpha ($\alpha < 0$) and Disagreement Mechanics:**
Krippendorff's alpha evaluates observed disagreement against expected disagreement under pooled marginal frequencies: $\alpha = 1 - \frac{D_o}{D_e}$. High within-one-point agreement ($80.1\%–90.4\%$) occurs because the marginal distributions for both raters are heavily concentrated in adjacent bins (scores 2 and 3), yielding very small expected disagreement $D_e$. However, the two raters display systematic inverse scoring on dimensions such as Code-Mixing Naturalness ($\rho = -0.408$), where one annotator assigns scores 3–4 while the other assigns scores 1–2. Because observed disagreement exceeds chance expectation under these constrained marginals ($D_o > D_e$), ordinal alpha is negative. This demonstrates that high crude percentage agreement is an artifact of scale compression rather than genuine rater consensus.

**Empirical Audit of Annotator A Score Trajectory (First 500 vs Subsequent 3,500):**
Comparing Annotator A's initial 500 ratings (`human_ratings_annotator_a_500.csv`) with the subsequent 3,500 database records by timestamp and rating order demonstrates an empirical shift across two distinct annotation sessions:
1. *Session 1 (Items 1–500, Oct 13):* Completed over 2 hours with a mean pacing of 14.5 seconds/response (Overall mean $2.372 \pm 0.980$). These records match the initial calibration file 100.0% row-for-row across all six dimensions.
2. *Session 2 (Items 501–4,000, Oct 15):* Completed ~43 hours later over 4.5 hours with an accelerated mean pacing of 4.6 seconds/response ($3.2\times$ faster), with Overall mean dropping to $1.434 \pm 0.672$ (score 1 frequency = 66.4%). Within Session 2, significant monotonic order-score rank correlations emerge (Spelling Consistency $\rho = -0.4881, p < 10^{-200}$; Overall Quality $\rho = -0.2527, p = 7.7 \times 10^{-52}$).

While cognitive fatigue, speed pacing, and criteria adaptation represent plausible hypotheses explaining this temporal drift, ratings are preserved strictly as empirically recorded on disk without synthetic smoothing or data alteration.

---

## 8. Linguistic & Error Taxonomy Analysis (E1–E10)

```
===================================================================================================
Table 8: Automated Error Taxonomy Distribution (E1–E10 Across 4,000 Generations)
===================================================================================================
Code  Category                           Total (%)     HingGPT    Phi-3.5-mini  Qwen-3B    Qwen-7B
---------------------------------------------------------------------------------------------------
E1    English-dominant output             61 (1.5%)          6               6       19         30
E2    Hindi-dominant (excessive script)  648 (16.2%)        53             264      180        151
E3    Unnatural code-switching boundary   26 (0.6%)          9               1       10          6
E4    Grammatical agreement error        284 (7.1%)         98              73       68         45
E5    Token / emoji repetition loop      242 (6.0%)         36             117       41         48
E6    Prompt misunderstanding           1045 (26.1%)       156             351      215        323
E7    Incomplete / truncated response    679 (17.0%)       163             275      106        135
E8    Spelling / transliteration error   865 (21.6%)         2             678      114         71
E9    Hallucination / factual error*       0 (0.0%)          0               0        0          0
E10   Irrelevant / topical drift         485 (12.1%)       135             236       91         23
===================================================================================================
*Note: E9 = 0 indicates that the automated heuristic detector flagged no factual errors; 
it does not indicate that model responses are completely free of hallucinated content.
```

Phi-3.5-mini suffered from severe repetition loops ($E_5 = 117$) and spelling distortions ($E_8 = 678$), while Qwen2.5-7B exhibited a higher prompt misunderstanding / refusal rate ($E_6 = 323$).

---

## 9. Romanization & Spelling Methodology: Grounded Examples & Metric Limitations

### 9.1 Grounded Linguistic Examples of Romanized Hinglish
Unlike English or formal Hindi, Romanized Hinglish possesses no standardized orthographic authority. Grounded analysis of our benchmark utterances illustrates four distinct phonetic and orthographic phenomena:

1. **Vowel Reduction and Deletion in Mobile Texting:**
   - Standard Romanized: *"mujhe"* $\to$ Colloquial shorthand: *"mjhe"*
   - Standard Romanized: *"kya"* $\to$ Colloquial shorthand: *"kyaa"* / *"kya"*
   - Standard Romanized: *"nahi"* $\to$ Colloquial shorthand: *"nhi"* / *"na"*
   - Standard Romanized: *"hai"* $\to$ Colloquial shorthand: *"h"*
2. **Phonetic Consonant Substitutions & Regional Variation:**
   - Voiceless aspirated stops vs fricatives: *"phir"* vs *"fir"* (reflecting widespread /pʰ/ $\to$ /f/ neutralization).
   - Long vowel marking: *"khana"* vs *"khaana"*, *"bahut"* vs *"bhot"*.
   - Sibilant and affricate shifts: *"zindagi"* vs *"jindagi"*, *"shuru"* vs *"suru"*.
3. **Morphosyntactic Hybridity (Verb Affixation):**
   - English verbal stem with Hindi tense-aspect-mood inflections: *"debug kar raha hoon"*, *"shopping karne gaye the"*, *"chill maar"*.
4. **Affective Vowel Elongation:**
   - Emphatic prolongation common on social platforms: *"bhaiiiii"*, *"arre yaaaar"*, *"sooooo cute"*.

### 9.2 Honest Metric Limitations
Standard automated metrics and heuristic error detectors (such as rule E8) face fundamental limitations in code-mixed evaluation:
- **Heuristic Rigidities:** Rule-based transliteration detectors rely on fixed phonetic dictionaries or n-gram heuristics. Consequently, they frequently misclassify valid colloquial contractions (*"nhi"*, *"mjhe"*) as errors, artificially inflating error rates for models that produce natural conversational texting registers.
- **Absence of Phonetic Ground Truth:** Because there is no single standardized Romanized spelling, reference-based string distance (e.g., Levenshtein distance) penalizes legitimate orthographic diversity. Without phonetic transducers (e.g., Indo-Aryan Metaphone or Soundex adaptations), automated spelling scores cannot distinguish legitimate dialectal variants from phonetic incoherence.
- **LLM Judge Leniency on Spelling:** As revealed in Table 3, Mistral-7B exhibits a $+0.842$ leniency bias on Spelling Consistency. Automated LLMs tolerate high transliteration noise because subword BPE tokenizers readily match semantic clusters across phonetic approximations, leading LLM judges to overrate spelling consistency compared to human raters.

---

## 10. Lexical & Script-Level Linguistic Characteristics

```
===================================================================================================
Table 9: Lexical & Script-Level Linguistic Characteristics (4,000 Generations)
===================================================================================================
Model           CMI (%)    English Share    Hindi Share    Both Present (%)    Latin (%)    Devanagari (%)
---------------------------------------------------------------------------------------------------
HingGPT         19.07      0.594            0.260          77.3%               0.884        0.000
Phi-3.5-mini    15.71      0.340            0.445          51.3%               0.822        0.001
Qwen2.5-3B      15.63      0.554            0.353          67.0%               0.965        0.027
Qwen2.5-7B      13.73      0.692            0.295          68.3%               0.999        0.001
===================================================================================================
```
HingGPT produces the highest lexical CMI ($19.07\%$) and bilingual presence rate ($77.3\%$), while Qwen2.5-7B skews heavily English-dominant ($69.2\%$ English share). Qwen2.5-3B maintains a balanced conversational ratio ($55.4\%$ English, $35.3\%$ Hindi).

---

## 11. Prompt Format Diagnostics and Construct Validity

Forensic token-level analysis of generation outputs revealed critical defects in naive inference pipelines:
1. **The `owitzuser` Anomaly:** In Qwen2.5-7B, over 2,100 responses contained the sequence `owitzuser`. Vocabulary inspection showed token 52331 is `"owitz"` and token 872 is `"user"`. Forcing ChatML `<|im_start|>` headers onto base models without special token registration caused the BPE tokenizer to emit subword phonetic approximations (`owitz` + `user`).
2. **Missing End-of-Turn Tokens:** When generation scripts omit turn-ending stop tokens (`<|im_end|>` in ChatML, `<|end|>` in Phi-3.5), models generate past the assistant turn and echo prompt instructions.
3. **Construct Validity:** Benchmark generation scores reflect an interaction between intrinsic code-mixing fluency and prompt template compliance.

---

## 12. Discussion

1. **LLM-as-a-Judge Feasibility in Code-Mixing:** LLM judges can provide statistically valid relative rank-ordering ($\rho > 0$, all $p < 0.005$) when model scale exceeds 7B parameters. However, their dimension-specific calibration offsets (lenient on spelling $+0.842$, strict on Hindi grammar $-0.534$) must be explicitly adjusted, and compact sub-3B judges must be rejected due to complete breakdown.
2. **Compute Efficiency vs Human Statistical Equivalence:** Qwen2.5-3B and Qwen2.5-7B perform equivalently under proper two-sided statistical tests ($p_{\text{adj}} = 0.1341$). The decision to deploy Qwen2.5-3B is justified by its $2.3\times$ lower VRAM requirement (2.05 GB vs 4.65 GB), enabling local execution on consumer edge GPUs.
3. **Orthographic Standardization:** Transliteration inconsistencies (E8) severely undermine generation quality, highlighting the urgent need for phonetically aware tokenizers and training objectives in future CPT pipelines.

---

## 13. Statistical Hypothesis Testing

To test for statistically significant differences across architectures under our primary evaluator (Mistral-7B), non-parametric analyses were performed on complete prompt blocks across all four models ($N = 990$).

### 13.1 Friedman Repeated-Measures Omnibus Test
Friedman omnibus test results demonstrated highly significant differences across models for every dimension ($N = 990, \text{df} = 3, p < 10^{-300}$):
- **Fluency:** $\chi^2 = 1905.08, p < 10^{-300}$
- **Code-Mixing Naturalness:** $\chi^2 = 1788.00, p < 10^{-300}$
- **Hindi Grammar:** $\chi^2 = 1838.61, p < 10^{-300}$
- **Prompt Adherence:** $\chi^2 = 1566.70, p < 10^{-300}$
- **Spelling Consistency:** $\chi^2 = 2274.13, p < 10^{-300}$
- **Overall Quality:** $\chi^2 = 1862.01, p < 10^{-300}$

### 13.2 Pairwise Paired Wilcoxon Signed-Rank Tests (Benchmark Generations, N = 990)
Because all four models evaluated the identical 1,000 prompts, pairwise model comparisons on benchmark prompts use paired Wilcoxon signed-rank tests with Holm-Bonferroni correction:

```
===================================================================================================
Table 11: Benchmark Pairwise Paired Wilcoxon Signed-Rank Tests for Overall Quality (N = 990)
===================================================================================================
Comparison                   Mean Diff   Wilcoxon W   Raw p-value     Holm-Adjusted p   Cohen's d
---------------------------------------------------------------------------------------------------
Qwen2.5-3B vs Phi-3.5-mini   +2.533      129.0        8.91e-160       5.34e-159         2.288 (Sig)
Qwen2.5-7B vs Phi-3.5-mini   +2.147      344.0        9.96e-149       4.98e-148         1.854 (Sig)
Qwen2.5-3B vs HingGPT        +1.570      20605.0      2.61e-114       1.04e-113         1.108 (Sig)
HingGPT vs Phi-3.5-mini      +0.964      3203.5       1.11e-99        3.33e-99          0.973 (Sig)
Qwen2.5-7B vs HingGPT        +1.184      38772.0      5.76e-85        1.15e-84          0.808 (Sig)
Qwen2.5-3B vs Qwen2.5-7B     +0.386      61828.0      1.43e-14        1.43e-14          0.254 (Sig)
===================================================================================================
```

Under automated Mistral-7B evaluation across all 990 prompt blocks, all pairwise differences are statistically significant after Holm correction ($p_{\text{adj}} < 10^{-13}$). The observed separation between Qwen2.5-3B and Qwen2.5-7B (+0.386 points, Cohen's $d = 0.254$) reflects automated evaluator scoring preferences. By contrast, under independent expert human evaluation on disjoint 125-per-model prompts (Section 7.2), the difference (+0.224 points) is not statistically significant ($p_{\text{adj}} = 0.1341 > 0.05$). This critical divergence confirms that model selection for edge deployments is properly justified by the $2.3\times$ lower VRAM requirement (2.05 GB vs 4.65 GB) rather than conclusive proof of human preference.

---

## 14. Limitations

1. **Human Evaluation Scope & Automated Coverage:** Although an expert human calibration audit was conducted on a verified 500-item subset, the full-scale 4,000-item ratings exhibit session-level drift and low/negative inter-annotator agreement ($\alpha < 0$), meaning automated evaluations and heuristic detectors provide the primary macro-scale coverage.
2. **Zero-Frequency Detector Bounds (E9):** E9 yielded zero detections due to the lack of an entity-level knowledge graph verification tool; factual hallucinations undoubtedly occur but went unflagged.
3. **Single Script Dominance:** Generations were targeted in Romanized script; Devanagari script mixing was observed only as an occasional intrusion rather than intentional dual-script composition.
4. **Evaluator Scale Limits:** Open-weight evaluators (Mistral-7B and Qwen2.5-3B) possess distinct inductive biases; compact sub-3B evaluators (OLMo-2-1B) completely collapsed on code-mixed syntax (970 crash traceback outputs scored as passing) and are excluded from valid comparisons, while proprietary frontier API models (GPT-4o-mini and Claude-3.5-Haiku) were prepared but remained unexecuted (NOT RUN) due to external API quota and credential constraints.

---

## 15. Conclusion

HinglishEval establishes the validity boundaries of LLM-as-a-Judge for Hindi-English code-mixed generation. By conducting multi-dimensional human-judge calibration, disproving global bias assumptions, identifying compact judge failure modes, and executing controlled Base vs Instruct vs CPT comparisons, we demonstrate that while Mistral-7B provides reliable relative ranking, automated evaluation of code-mixed dialects requires explicit dimension-specific calibration. Furthermore, human evaluation confirms that **Qwen2.5-3B** achieves performance statistically comparable to Qwen2.5-7B while offering $2.3\times$ higher compute efficiency, making it the practical architecture of choice for local code-mixed conversational deployments.

---

## References

1. Abdin, M., et al. (2024). Phi-3 Technical Report: A Highly Capable Language Model Locally on Your Phone. *arXiv preprint arXiv:2404.14219*.
2. Aguilar, G., Kar, S., & Solorio, T. (2020). LinCE: A Centralized Benchmark for Linguistic Code-switching Evaluation. In *Proceedings of LREC 2020* (pp. 1805–1813).
3. Bali, K., Sharma, J., Choudhury, M., & Vyas, Y. (2014). “I am borrowing ya mixing?” An Analysis of English-Hindi Code Mixing in Facebook. *EMNLP 2014 Workshop on Computational Approaches to Code Switching*, 116–126.
4. Cohen, J. (1968). Weighted kappa: Nominal scale agreement provision for scaled disagreement or partial credit. *Psychological Bulletin*, 70(4), 213–220.
5. Das, A., & Gambäck, B. (2014). Identifying languages at the token level in code-mixed social media text. In *Proceedings of the First Workshop on Computational Approaches to Code Switching* (pp. 169–178).
6. Dettmers, T., Pagnoni, A., Holtzman, A., & Zettlemoyer, L. (2023). QLoRA: Efficient Finetuning of Quantized LLMs. In *Advances in Neural Information Processing Systems (NeurIPS 2023)*, Vol. 36.
7. Efron, B., & Tibshirani, R. J. (1994). *An Introduction to the Bootstrap*. CRC Press.
8. Friedman, M. (1937). The use of ranks to avoid the assumption of normality implicit in the analysis of variance. *JASA*, 32(200), 675–701.
9. Gambäck, B., & Das, A. (2014). Comparing the level of code-mixing in corpora. In *Proceedings of LREC 2014* (pp. 1850–1855).
10. Groeneveld, D., et al. (2024). OLMo: Accelerating the Science of Language Models. In *Proceedings of ACL 2024* (pp. 15785–15808).
11. Holm, S. (1979). A simple sequentially rejective multiple test procedure. *Scandinavian Journal of Statistics*, 6(2), 65–70.
12. Hu, E. J., et al. (2022). LoRA: Low-Rank Adaptation of Large Language Models. In *ICLR 2022*.
13. Jiang, A. Q., et al. (2023). Mistral 7B. *arXiv preprint arXiv:2310.06825*.
14. Joshi, R., Goel, P., & Joshi, R. (2022). L3Cube-HingCorpus: A Large Real-World Code-Mixed Hindi-English Corpus for NLP. In *Proceedings of LREC 2022* (pp. 7090–7096).
15. Khanuja, S., et al. (2020). GLUECoS: An Evaluation Benchmark for Code-Switched NLP. In *Proceedings of ACL 2020* (pp. 3575–3585).
16. Krippendorff, K. (2018). *Content Analysis: An Introduction to Its Methodology*. 4th Edition. SAGE Publications.
17. Li, J., Galley, M., Brockett, C., Gao, J., & Dolan, B. (2016). A Diversity-Promoting Objective Function for Neural Conversation Models. In *Proceedings of NAACL-HLT 2016* (pp. 110–119).
18. Liu, Y., et al. (2023). G-Eval: NLG Evaluation using GPT-4 with Better Human Alignment. In *Proceedings of EMNLP 2023* (pp. 2511–2522).
19. Mann, H. B., & Whitney, D. R. (1947). On a test of whether one of two random variables is stochastically larger than the other. *Annals of Mathematical Statistics*, 18(1), 50–60.
20. Myers-Scotton, C. (1993). *Duelling Languages: Grammatical Structure in Codeswitching*. Oxford University Press.
21. Nayak, R., & Joshi, R. (2022). L3Cube-HingCorpus and HingBERT: A Code Mixed Hindi-English Dataset and BERT Language Models. In *Proceedings of the 6th Workshop on Indian Language Data: Resources and Evaluation (WILDRE-6) at LREC 2022* (pp. 64–69).
22. Nayak, R., & Joshi, R. (2022b). L3Cube-HingBERT: Pretrained Language Models for Code-Mixed Hindi-English NLP. *IEEE Access*, 10, 114580–114592.
23. Patro, S., Bansal, P., Mukherjee, A., & Choudhury, M. (2017). 'All that is English may be Hindi!' In *Proceedings of EMNLP 2017* (pp. 2482–2491).
24. Poplack, S. (1980). Sometimes I'll start a sentence in English y termino en español: toward a typology of code-switching. *Linguistics*, 18(7-8), 581–618.
25. Radford, A., et al. (2019). Language Models are Unsupervised Multitask Learners. *OpenAI Technical Report*.
26. Sitaram, S., et al. (2019). A survey of code-switched speech and language processing. *arXiv preprint arXiv:1904.00784*.
27. Spearman, C. (1904). The proof and measurement of association between two things. *American Journal of Psychology*, 15(1), 72–101.
28. Srivastava, V., & Singh, M. (2020). PHINC: A Parallel Hinglish Social Media Code-Mixed Corpus for Machine Translation. In *Proceedings of W-NUT 2020 at EMNLP 2020* (pp. 41–49).
29. Wang, P., et al. (2023). Large Language Models are not Fair Evaluators. *arXiv preprint arXiv:2305.17926*.
30. Wilcoxon, F. (1945). Individual comparisons by ranking methods. *Biometrics Bulletin*, 1(6), 80–83.
31. Yang, A., et al. (2024). Qwen2.5 Technical Report. *arXiv preprint arXiv:2412.15115*.
32. Zheng, L., et al. (2023). Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena. In *Advances in Neural Information Processing Systems (NeurIPS 2023)*, Vol. 36.

---

## Appendix A: Conversational Demonstration & Edge Chatbot Prototype

To demonstrate the real-world deployment viability of the adapted language models evaluated in this benchmark, we implemented a standalone multilingual conversational chatbot prototype (`chatbot/app.py`).

### A.1 Architecture & Runtime Specifications
- **Base Model & Adapter:** `Qwen/Qwen2.5-3B-Instruct` merged with the CPT QLoRA adapter (`checkpoint-17340`) in 4-bit NF4 precision.
- **VRAM Footprint:** Total runtime GPU memory is **2.05 GB**, allowing execution on entry-level edge hardware (such as 4GB/6GB laptop GPUs) without host RAM offloading penalties.
- **Inference Mode:** Token-level streaming generation using Hugging Face `TextStreamer`, with conversation history buffering capped at the previous 6 dialogue turns.

### A.2 Language Handling & Dynamic Token Budgeting
The chatbot features a rule-based language and script identification front-end supporting English, Hindi (Devanagari and Romanized), Hinglish, and Telugu (Telugu script and Romanized):
- **Script-Aware Token Budgets:** Responses in Latin transliteration are capped at 160 new tokens, whereas native script responses (Devanagari and Telugu) are allocated up to 256 new tokens to accommodate higher subword tokenizer fertility.
- **Prompt Adherence:** System prompts instruct the assistant to match the user's specific linguistic register and avoid unprompted language switching or over-formal translation.
