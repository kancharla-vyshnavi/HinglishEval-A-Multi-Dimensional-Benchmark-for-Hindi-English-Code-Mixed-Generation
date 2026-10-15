# HinglishEval: A Multi-Dimensional Benchmark for Hindi-English Code-Mixed Generation

**Author:** Vyshnavi Kancharla  
**Repository:** `https://github.com/kancharla-vyshnavi/A-Multi-Dimensional-Benchmark-of-LLMs-for-Hindi-English-Code-Mixed-Generation`  
**Outputs & Canonical Artifacts:** `research_upgrade/v3/`  

---

## Abstract

Hindi-English code-mixing (*Hinglish*) is the primary communicative medium for hundreds of millions of multilingual speakers across South Asia and digital diaspora communities. Despite rapid advancements in large language models (LLMs), evaluating and generating natural code-mixed text remains severely constrained by lack of standardized, contamination-audited evaluation protocols, fragile prompt-formatting conventions, and uncalibrated automated evaluators. In this paper, we introduce **HinglishEval**, a multi-dimensional benchmark evaluating open-weight language models on conversational Hinglish generation across six linguistic dimensions: **Fluency**, **Code-Mixing Naturalness**, **Hindi Grammar**, **Prompt Adherence**, **Spelling Consistency**, and **Overall Quality**. 

We execute a rigorous four-phase investigation:
1. **Contamination & Leakage Audit:** Systematic n-gram Jaccard matching across the 277k-sentence L3Cube-HingCorpus pretraining dataset and the evaluation benchmark detects 0 exact matches (0.00%) and 8 moderate-overlap prompts (0.80%), establishing a verified 992-item leakage-free benchmark.
2. **Controlled Model Evaluation:** We evaluate Continued Pretrained (CPT) models against Base and Instruction-tuned baselines across four model families (Qwen2.5-3B, Qwen2.5-7B, Phi-3.5-mini, and HingGPT). Continued pretraining reduces cross-entropy loss from 5.04 to 4.06 (a 62.7% validation perplexity reduction).
3. **Calibrated Human Evaluation & Statistical Overhaul:** An empirical human evaluation study across 500 matched responses analyzed with two-sided Mann-Whitney $U$ tests and Holm-Bonferroni correction demonstrates that while Qwen2.5-3B achieves the highest numerical human preference (mean Overall Quality = 2.704 vs 2.480 for Qwen2.5-7B), the pairwise difference is not statistically significant ($p = 0.0671$, adjusted $p_{\text{adj}} = 0.1341$). We therefore distinguish practical deployment and VRAM efficiency ($2.3\times$ lower compute footprint) from statistical superiority. Both Qwen models significantly outperform Phi-3.5-mini ($p_{\text{adj}} < 0.001$) and HingGPT ($p_{\text{adj}} < 0.001$).
4. **Judge Alignment & Evaluator Bias:** Evaluating automated LLM judges against human ratings disproves previous claims of a uniform "+0.85 leniency bias" for Mistral-7B; true Overall Quality bias is merely $+0.098$ points (95% CI $[-0.036, +0.232]$), with Mistral acting leniently on spelling ($+0.842$) but strict on Hindi syntax ($-0.534$). Conversely, smaller 1B evaluators (OLMo-2-1B) collapse on ungrammatical outputs (Quadratic Weighted Kappa $\kappa_w = -0.0135$).
5. **Prompt-Format Construct Validity:** Controlled diagnostics reveal that forcing ChatML wrappers onto Base Causal LMs without turn-ending stopping criteria induces catastrophic prompt echoing (83% in Phi-3.5), spurious token emissions (`owitzuser`), and safety refusals (12% in Qwen-7B), indicating that benchmark scores reflect an interaction between code-mixing fluency and template compliance.

All code, canonical data records, evaluation sheets, and publication-ready figures are made publicly available.

---

## 1. Introduction

Linguistic code-switching—the alternation between two or more languages within a single conversational discourse—is a ubiquitous hallmark of multilingual speech and digital communication (Poplack, 1980; Myers-Scotton, 1993). In the Indian subcontinent, Hindi-English code-mixing (*Hinglish*) has emerged as the default lingua franca across social media, messaging platforms, e-commerce, and entertainment (Bali et al., 2014; Sitaram et al., 2019). Hinglish is characterized by structural asymmetry: speakers typically employ Hindi as the matrix grammatical frame while embedding English lexical items, verb complements, and colloquial discourse markers, written predominantly in the Roman alphabet rather than the native Devanagari script (Gambäck & Das, 2014; Joshi et al., 2022).

Despite remarkable progress in frontier autoregressive language models (Radford et al., 2019; Yang et al., 2024), generating natural, grammatically coherent, and contextually appropriate Hinglish remains exceptionally difficult for open-weight models. Prior evaluation benchmarks such as LinCE (Aguilar et al., 2020) and GLUECoS (Khanuja et al., 2020) focused almost exclusively on discriminative classification tasks (e.g., sentiment analysis, token-level language identification, named entity recognition). The generative capabilities of small and medium open-weight language models on free-form code-mixed dialogue have remained largely unbenchmarked.

Moreover, existing generation studies suffer from three severe methodological limitations:
1. **Contamination Blind Spots:** Generative benchmarks rarely verify whether test utterances overlap with public code-mixed web corpora used during pretraining, leading to inflated performance estimates.
2. **Overstated Statistical Claims & Multiple-Testing Fallacies:** Small-sample human evaluation studies frequently conduct directional, one-sided hypothesis tests without multiple-comparison corrections, conflating practical engineering trade-offs (e.g., VRAM constraints) with statistically supported human superiority.
3. **Uncalibrated Automated Judges:** Evaluating code-mixed text using large language models as judges (Zheng et al., 2023; Liu et al., 2023) has introduced severe dimension-dependent leniency and strictness biases that distort model rankings when uncalibrated.

### Contributions
To resolve these challenges, this study presents **HinglishEval**, providing the following contributions:
- **Contamination-Audited Benchmark:** We perform an exhaustive 8-gram Jaccard overlap audit between the 277k-sentence L3Cube-HingCorpus pretraining corpus (Nayak & Joshi, 2022) and 1,000 real-world social media utterances, identifying and isolating a strictly leakage-free 992-prompt benchmark.
- **Controlled Generation & Automated Error Taxonomy:** We generate and analyze 4,000 controlled responses across four continued-pretrained model families (Qwen2.5-3B, Qwen2.5-7B, Phi-3.5-mini, and HingGPT), profiling ten discrete error classes ($E_1$ through $E_{10}$) alongside information-theoretic Bits-per-Character (BPC) and Code-Mixing Index (CMI) distributions.
- **Corrected Human Evaluation Statistics:** On 500 validated human ratings across six dimensions, we demonstrate that Qwen2.5-3B's numerical lead over Qwen2.5-7B on Overall Quality (2.704 vs 2.480) is not statistically significant ($p_{\text{adj}} = 0.1341$). We update the model-selection rationale to reflect compute efficiency ($2.07$ GB vs $4.65$ GB VRAM) rather than unsupported human superiority.
- **Disproving Blanket Evaluator Bias:** We evaluate Mistral-7B and OLMo-2-1B against human ratings across all six dimensions, disproving previous claims of a uniform $+0.85$ leniency bias. We show that Mistral's bias is dimension-specific (lenient on spelling $+0.842$, strict on Hindi grammar $-0.534$, and calibrated on Overall Quality $+0.098$).
- **Prompt Format & Construct Validity Diagnostics:** We audit tokenizer special tokens, BOS/EOS handling, and chat templates, identifying how omission of end-of-turn tokens caused prompt echoing in Phi-3.5-mini and subword token corruption (`owitzuser`) in Qwen-7B.
- **Scientific Transparency & Reproducibility:** We provide complete disclosures regarding single-annotator provenance, stage blinded 100-item second-rater sheets, provide an automated consistency validator, and make all code and canonical tables open source.

---

## 2. Related Work

### Code-Mixed Benchmarks & Processing
Early computational research in code-mixing centered on linguistic rule formalisms and token-level language identification (Das & Gambäck, 2014; Patro et al., 2017). LinCE (Aguilar et al., 2020) and GLUECoS (Khanuja et al., 2020) established standardized evaluation suites for Hindi-English and Spanish-English code-switching, benchmarking masked language models on POS tagging, NER, and sentiment classification. For machine translation, PHINC (Srivastava & Singh, 2020) introduced a parallel Hinglish-English corpus. Nayak & Joshi (2022) created L3Cube-HingCorpus, a 277k-sentence monolingual Hinglish social corpus, and trained HingBERT (Nayak & Joshi, 2022b). While these efforts advanced discriminative understanding, open-ended conversational generation has remained underserved.

### Parameter-Efficient Fine-Tuning & Adaptation
Adapting foundation models to low-resource or non-standard linguistic varieties requires parameter-efficient fine-tuning (PEFT). Low-Rank Adaptation (LoRA; Hu et al., 2022) injects low-rank decomposition matrices into attention weights. QLoRA (Dettmers et al., 2023) introduced 4-bit NormalFloat (NF4) quantization with Double Quantization, enabling domain adaptation of 3B and 7B models on accessible consumer hardware.

### LLM-as-a-Judge and Evaluator Calibration
The LLM-as-a-judge paradigm (Zheng et al., 2023; Liu et al., 2023) has gained widespread adoption due to the prohibitive financial and temporal expense of human annotation. However, Wang et al. (2023) demonstrated that LLM judges exhibit egocentric bias, verbosity bias, and positional bias. In multilingual and code-mixed settings, calibrating automated evaluators against human ground truth across multiple linguistic dimensions is essential to ensure evaluation fidelity.

---

## 3. Dataset and Benchmark Construction

### Source Utterances and Filtering
The evaluation prompts for HinglishEval were drawn from natural, conversational social media discourses in Roman-script Hinglish across news, everyday inquiries, cultural observations, colloquial banter, and technical discussions. 

### Data Leakage and Contamination Audit
To ensure that benchmark scores reflect genuine zero-shot generalization rather than memorization of pretraining sequences, we conducted an automated contamination audit comparing all 1,000 candidate benchmark prompts against the 277,434 training sequences of L3Cube-HingCorpus.

We computed token-level 8-gram Jaccard similarity coefficients:
$$J(P, T) = \frac{|N(P) \cap N(T)|}{|N(P) \cup N(T)|}$$
where $N(S)$ represents the set of word 8-grams in sequence $S$.

| Overlap Threshold ($J$) | Contamination Classification | Prompt Count | Proportion (%) | Corrective Action |
| :--- | :--- | :---: | :---: | :--- |
| $J = 1.00$ | Exact Pretraining Duplicate | 0 | 0.00% | Verified uncontaminated |
| $0.90 \le J < 1.00$ | High Verbatim Overlap | 0 | 0.00% | Verified uncontaminated |
| $0.80 \le J < 0.90$ | Moderate Syntactic Overlap | 8 | 0.80% | **Quarantined & Excluded** |
| $J < 0.80$ | Leakage-Free Discourse | 992 | 99.20% | **Retained as Canonical Benchmark** |

*Table 1: Forensic Contamination Audit between L3Cube-HingCorpus Pretraining Data and Benchmark Prompts.*

The eight moderate-overlap prompts were quarantined, establishing a canonical **992-item leakage-free benchmark**.

---

## 4. Model Training and Experimental Setup

### Model Architecture and Checkpoints
We investigate four diverse open-weight model architectures:
1. **Qwen2.5-3B:** 3.09B parameter foundation model (Yang et al., 2024), 151k vocabulary.
2. **Qwen2.5-7B:** 7.61B parameter foundation model, 151k vocabulary.
3. **Phi-3.5-mini:** 3.82B parameter instruction-tuned model (Abdin et al., 2024), 32k vocabulary.
4. **HingGPT:** 124M parameter GPT-2 causal language model pretrained on Hinglish tweets (L3Cube Pune), 30.5k vocabulary.

### Continued Pretraining (CPT) Protocol
All models underwent Continued Pretraining on the 277,434 natural Hinglish sentences of L3Cube-HingCorpus. Training was performed using 4-bit QLoRA ($r=8, \alpha=16$) with AdamW optimizer ($\beta_1=0.9, \beta_2=0.999$, weight decay 0.01), initial learning rate $5 \times 10^{-5}$ with linear warmup and cosine decay over 17,340 steps (batch size 8, gradient accumulation 2).

### Reconciling Perplexity Discrepancies
Earlier technical notes reported conflicting validation perplexity values of 57.78 and 74.02 for Qwen2.5-3B-CPT. Our forensic inspection resolved this discrepancy completely:
- **Full Validation Corpus ($N = 14,601$ sequences):** Final cross-entropy loss was $4.3043$, yielding a perplexity of **74.02**.
- **Diagnostic Ablation Slice ($N = 100$ sequences):** Evaluated on conversational utterances within context length 128, cross-entropy loss was $4.0566$, yielding a perplexity of **57.78**.
- **Pretraining Trajectory:** Pre-CPT base model perplexity was $154.97$ ($\text{loss} = 5.0432$). CPT achieved a **62.7% reduction in validation perplexity**.

---

## 5. Multi-Dimensional Human Evaluation

### Evaluation Setup and Transparency Disclosure
Human evaluation was conducted on 500 randomly sampled, stratified model responses (125 items per model across 4 models). In accordance with research disclosure guidelines:
- **Sole Primary Evaluator:** All 500 responses were scored by the primary author (Annotator A) using a blinded, randomized evaluation interface.
- **Dimensions Evaluated:** Every response was scored on an integer 1-to-5 Likert scale across six discrete dimensions: Fluency, Code-Mixing Naturalness, Hindi Grammar, Prompt Adherence, Spelling Consistency, and Overall Quality.
- **Statistical Independence:** Prompt IDs were not identical across all four models in the 500-sample set (each model had 125 distinct prompt IDs with partial overlap). Consequently, between-model comparisons must be analyzed using **independent-samples non-parametric tests (Mann-Whitney $U$)** rather than paired Wilcoxon signed-rank tests.

### Human Evaluation Results Across All Six Dimensions

| Model | Fluency Mean (95% CI) | Code-Mixing Mean (95% CI) | Hindi Grammar Mean (95% CI) | Prompt Adherence Mean (95% CI) | Spelling Consistency Mean (95% CI) | Overall Quality Mean (95% CI) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Qwen2.5-3B** | **2.912** `[2.712, 3.120]` | **2.664** `[2.456, 2.872]` | **2.904** `[2.704, 3.104]` | **2.568** `[2.352, 2.784]` | **2.800** `[2.592, 3.008]` | **2.704** `[2.440, 2.968]` |
| **Qwen2.5-7B** | 2.720 `[2.512, 2.928]` | 2.488 `[2.288, 2.688]` | 2.624 `[2.432, 2.816]` | 2.472 `[2.256, 2.688]` | 2.552 `[2.352, 2.752]` | 2.480 `[2.240, 2.728]` |
| **Phi-3.5-mini** | 2.384 `[2.248, 2.520]` | 2.104 `[1.952, 2.256]` | 2.328 `[2.184, 2.472]` | 2.088 `[1.944, 2.232]` | 2.240 `[2.088, 2.392]` | 2.112 `[1.928, 2.296]` |
| **HingGPT** | 2.488 `[2.312, 2.664]` | 2.248 `[2.072, 2.424]` | 2.568 `[2.392, 2.744]` | 2.136 `[1.968, 2.304]` | 2.408 `[2.232, 2.584]` | 2.192 `[1.968, 2.424]` |

*Table 2: Canonical Human Evaluation Summary Across All Six Dimensions ($N=125$ per model, 10,000 bootstrap iterations).*

![Human Evaluation Ratings](/figures/human_evaluation_six_dimensions.png)
*Figure 1: Human Evaluation Ratings across all six linguistic dimensions with 95% bootstrap confidence intervals.*

### Two-Sided Hypothesis Testing & Multiplicity Correction
To prevent false-positive discovery across pairwise model comparisons, we conduct two-sided Mann-Whitney $U$ tests with **Holm-Bonferroni step-down correction** across all six pairwise comparisons within each dimension.

| Evaluation Dimension | Comparison | Mann-Whitney $U$ | Raw $p$-value | Holm Adjusted $p_{\text{adj}}$ | Rank-Biserial Effect Size ($r_{\text{rb}}$) | Significance ($\alpha=0.05$) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Overall Quality** | Qwen2.5-3B vs Qwen2.5-7B | 8808.0 | $6.71 \times 10^{-2}$ | $1.34 \times 10^{-1}$ | +0.1274 | **Not Significant** |
| **Overall Quality** | Qwen2.5-3B vs HingGPT | 9884.0 | $1.49 \times 10^{-4}$ | $5.96 \times 10^{-4}$ | +0.2652 | **Significant** |
| **Overall Quality** | Qwen2.5-3B vs Phi-3.5-mini | 10072.0 | $1.89 \times 10^{-5}$ | $9.44 \times 10^{-5}$ | +0.2892 | **Significant** |
| **Overall Quality** | Qwen2.5-7B vs HingGPT | 8887.5 | $5.16 \times 10^{-2}$ | $1.34 \times 10^{-1}$ | +0.1376 | **Not Significant** |
| **Overall Quality** | Qwen2.5-7B vs Phi-3.5-mini | 9256.0 | $1.02 \times 10^{-2}$ | $3.06 \times 10^{-2}$ | +0.1848 | **Significant** |
| **Overall Quality** | HingGPT vs Phi-3.5-mini | 8092.5 | $6.30 \times 10^{-1}$ | $6.30 \times 10^{-1}$ | +0.0358 | **Not Significant** |
| **Hindi Grammar** | Qwen2.5-3B vs Qwen2.5-7B | 8876.5 | $5.32 \times 10^{-2}$ | $1.06 \times 10^{-1}$ | +0.1362 | **Not Significant** |
| **Hindi Grammar** | Qwen2.5-3B vs Phi-3.5-mini | 10398.5 | $1.16 \times 10^{-6}$ | $6.98 \times 10^{-6}$ | +0.3310 | **Significant** |
| **Code-Mixing** | Qwen2.5-3B vs Phi-3.5-mini | 10228.0 | $5.07 \times 10^{-6}$ | $3.04 \times 10^{-5}$ | +0.3092 | **Significant** |

*Table 3: Pairwise Two-Sided Non-Parametric Tests with Holm-Bonferroni Correction.*

### Critical Finding: Overturning the "Statistical Superiority" Claim
Earlier project drafts asserted that Qwen2.5-3B "decisively outperformed" and was "statistically superior" to Qwen2.5-7B based on an uncorrected, one-sided $p$-value ($p = 0.0335$). 

Under proper statistical standards:
- The two-sided test yields a raw $p$-value of **$0.0671$**.
- After Holm-Bonferroni correction across the six pairwise model comparisons, the adjusted $p$-value is **$p_{\text{adj}} = 0.1341$**, which exceeds the $\alpha = 0.05$ threshold.
- Therefore, **the hypothesis of statistical superiority between Qwen2.5-3B and Qwen2.5-7B on human ratings is not supported by the data**.
- **Model Selection Rationale:** Qwen2.5-3B is selected as the primary recommended model not due to statistically proven human preference, but because it delivers comparable generative quality at **$2.3\times$ lower VRAM consumption** (2.07 GB vs 4.65 GB), higher inference throughput (41.2 tok/s vs 18.4 tok/s), and greater resilience against chat-template refusal degradation.

---

## 6. Automated Linguistic and Diversity Metrics

To complement human ratings, we evaluate all 992 leakage-free generations using automated linguistic and information-theoretic metrics:
- **Code-Mixing Index (CMI):** Quantifies the ratio of Hindi to English tokens according to the formulation of Gambäck & Das (2014).
- **Lexical Diversity (Distinct-N):** Measures the proportion of unique unigrams (Distinct-1) and bigrams (Distinct-2) across generated responses (Li et al., 2016).
- **Bits-per-Character (BPC):** Information-theoretic compression metric reflecting model probability assigned to reference characters.

| Model Variant | Evaluated $N$ | CMI (%) | Distinct-1 | Distinct-2 | Distinct-3 | BPC (Nats/Char) | Automated Error Rate ($E_1$–$E_{10}$) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Qwen2.5-3B** | 992 | **28.45** | **0.428** | **0.781** | **0.912** | **1.482** | **14.8%** |
| **Qwen2.5-7B** | 992 | 27.12 | 0.415 | 0.764 | 0.898 | 1.498 | 28.4% |
| **Phi-3.5-mini** | 992 | 19.34 | 0.284 | 0.512 | 0.638 | 1.842 | 84.6% |
| **HingGPT** | 992 | 15.62 | 0.312 | 0.548 | 0.684 | 2.415 | 46.2% |

*Table 4: Information-Theoretic, Lexical Diversity, and Error Metrics across 992 Leakage-Free Responses.*

![Linguistic Metrics](/figures/linguistic_and_diversity_metrics.png)
*Figure 2: Distribution of Code-Mixing Index (CMI), Lexical Diversity (Distinct-N), and Bits-per-Character (BPC).*

---

## 7. Error Taxonomy Analysis ($E_1$–$E_{10}$)

We classify model generation defects into a standardized 10-category error taxonomy ($E_1$ to $E_{10}$):
- **$E_1$ (Unnatural Mixing):** Awkward intra-sentential boundary switching violating matrix language frame constraints.
- **$E_2$ (Severe Grammar Defect):** Erroneous Hindi postposition or gender-verb agreement.
- **$E_3$ (Spelling Distortion):** Extreme transliteration distortion rendering Roman Hindi illegible.
- **$E_4$ (Off-Topic Drift):** Generation drifts into unrelated domain content.
- **$E_5$ (Degenerative Loop):** Repetitive token or n-gram loops (e.g., repeating a single phrase 5+ times).
- **$E_6$ (Unwarranted Refusal):** Over-aligned safety refusal ("I'm sorry, but I can't assist with that request") on benign colloquial prompts.
- **$E_7$ (Sentence Truncation):** Utterance cuts off abruptly without terminal punctuation due to generation token caps.
- **$E_8$ (Inappropriate Script):** Spurious Devanagari script emission when Roman transliteration was requested.
- **$E_9$ (Semantic Incoherence):** Syntactically well-formed words yielding nonsensical discourse.
- **$E_{10}$ (Foreign Language Hallucination):** Hallucination of third languages (e.g., Spanish/Portuguese phrases in HingGPT).

![Error Taxonomy](/figures/error_taxonomy_e1_e10.png)
*Figure 3: Frequency of occurrence for error categories $E_1$ through $E_{10}$ across all four evaluated models.*

Phi-3.5-mini suffered from an extreme degenerative loop rate ($E_5 = 48.6\%$), while Qwen2.5-7B exhibited an elevated safety refusal rate ($E_6 = 12.0\%$).

---

## 8. Calibration of LLM Judges and Disproving Blanket Evaluator Bias

### Evaluating Mistral-7B Bias
Earlier project drafts claimed that Mistral-7B displayed a uniform global "+0.85 leniency bias" across all evaluation dimensions. We recalculated evaluator bias ($\text{Bias} = \text{Score}_{\text{Mistral}} - \text{Score}_{\text{Human}}$) across all 500 matched responses with 10,000 bootstrap resamples.

| Evaluation Dimension | Human Mean | Mistral Mean | Mean Bias ($M - H$) | 95% Bootstrap CI | Spearman $\rho$ | Pearson $r$ | Quadratic Weighted Kappa ($\kappa_w$) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Fluency** | 2.626 | 2.516 | **-0.110** | `[-0.242, +0.018]` | +0.1579 | +0.1769 | 0.1706 |
| **Code-Mixing** | 2.376 | 2.826 | **+0.450** | `[+0.298, +0.594]` | +0.2215 | +0.2155 | 0.1761 |
| **Hindi Grammar** | 2.606 | 2.072 | **-0.534** | `[-0.652, -0.414]` | +0.1270 | +0.1388 | 0.1223 |
| **Prompt Adherence** | 2.316 | 2.476 | **+0.160** | `[+0.006, +0.310]` | +0.1914 | +0.1781 | 0.1530 |
| **Spelling Consistency** | 2.500 | 3.342 | **+0.842** | `[+0.680, +1.002]` | +0.1754 | +0.1891 | 0.1388 |
| **Overall Quality** | 2.372 | 2.470 | **+0.098** | `[-0.036, +0.232]` | +0.1837 | +0.1788 | 0.1691 |

*Table 5: Dimension-Wise Mistral-7B Bias and Correlation Metrics across 500 Matched Responses.*

![Mistral Bias Calibration](/figures/human_vs_mistral_bias.png)
*Figure 4: Panel A: Evaluator bias disaggregated by dimension and generator model (disproving the old +0.85 blanket claim). Panel B: Jittered scatter plot of Mistral vs Human Overall Quality scores.*

**Forensic Explanation:**
1. The "+0.85 leniency" claim arose from conflating **Spelling Consistency** (where bias is indeed $+0.842$) with Overall Quality.
2. On Overall Quality, Mistral is calibrated, with a bias of only **$+0.098$ points**.
3. Mistral is actually **strict** on Hindi Grammar ($-0.534$), heavily penalizing inflection errors.
4. Mistral achieves statistically significant positive rank correlation across all six dimensions ($p < 0.005$), validating its utility as a comparative ranking evaluator.

### Collapse of Small 1B Evaluators (OLMo-2-1B)
By contrast, OLMo-2-1B-Instruct completely collapsed when scoring Hinglish generations:
- Assigned a mean Overall score of **$4.26$** to corrupt, repetitive outputs.
- Quadratic Weighted Kappa against human ground truth was negative ($\kappa_w = -0.0135$).
- Small 1B evaluators lack the cross-lingual semantic capacity to identify code-mixed syntactic corruption.

---

## 9. Prompt Format Diagnostics and Construct Validity

### Investigating `owitzuser` and Prompt Echoing
Forensic token-level analysis of generation outputs revealed critical defects in the original inference pipeline (`run_controlled.py`):
1. **The `owitzuser` Anomaly:** In Qwen2.5-7B, over 2,100 responses contained the sequence `owitzuser`. Vocabulary inspection showed token 52331 is `"owitz"` and token 872 is `"user"`. Because Qwen2.5-7B is a base model trained on plain text, forcing ChatML `<|im_start|>` headers caused the BPE tokenizer to emit subword phonetic approximations (`owitz` + `user`).
2. **Missing End-of-Turn Tokens:** `run_controlled.py` set `eos_token_id = tokenizer.eos_token_id` (`<|endoftext|>`). In ChatML, the turn-ending token is `<|im_end|>` (151645), and in Phi-3.5 it is `<|end|>` (32007). Omitting these tokens caused models to generate past the assistant turn and echo prompt instructions.
3. **Construct Validity Verdict:** HinglishEval benchmark scores reflect a combination of intrinsic code-mixing fluency and out-of-distribution template compliance. When evaluated under plain continuation matching pretraining, valid response rates rise from 60% to 94% in Qwen-7B.

---

## 10. Baseline Comparisons and Ablation Studies

### LoRA Rank Scaling Specifications
We modeled parameter scaling across LoRA ranks $r \in \{8, 16, 64\}$ on Qwen2.5-3B:

| LoRA Rank ($r$) | Scaling Alpha ($\alpha$) | Trainable Parameters | Trainable % | Adapter Size | Optimizer VRAM | 6GB Feasibility |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **8** | 16 | 8,257,536 | 0.268% | 15.75 MB | 126.0 MB | **Feasible (QLoRA 4-bit)** |
| **16** | 32 | 16,515,072 | 0.535% | 31.50 MB | 252.0 MB | **Feasible (QLoRA 4-bit)** |
| **64** | 128 | 66,060,288 | 2.141% | 126.00 MB | 1,008.0 MB | **Approaches VRAM ceiling** |

*Table 6: LoRA Rank Scaling Specifications for Domain Adaptation.*

![CPT and Ablations](/figures/cpt_perplexity_and_rank_ablation.png)
*Figure 5: Panel A: Perplexity reduction across pre-CPT and CPT checkpoints. Panel B: Parameter scaling across LoRA ranks.*

---

## 11. Limitations and Ethical Disclosures

1. **Single Human Annotator:** The 500 human ratings were evaluated by a single expert researcher (Annotator A). While rigorous, single-annotator ratings cannot establish inter-annotator agreement ($\kappa_w$). A 100-item blinded sheet (`second_rater_annotation_sheet_100.csv`) is staged awaiting completion by an independent native speaker.
2. **Washout Test-Retest:** The author test-retest protocol (`author_test_retest_sheet_100.csv`) will be scored after a 1-to-2 week washout period to estimate intra-annotator reliability.
3. **Single-Turn Scope:** HinglishEval evaluates single-turn responses; multi-turn conversational dynamics remain future work.
4. **AI Assistance Disclosure:** An AI coding assistant executed software engineering scripts under human oversight. The AI is not an independent auditor. The human author assumes full intellectual responsibility.

---

## 12. Conclusion

HinglishEval establishes a multi-dimensional benchmark for Hindi-English code-mixed generation. By conducting an empirical contamination audit, rectifying statistical testing with two-sided Holm-corrected tests, calibrating automated evaluators, and diagnosing prompt-formatting interactions, we demonstrate that Qwen2.5-3B provides the optimal balance of code-mixing fluency and practical deployment efficiency.

---

## References

1. Abdin, M., et al. (2024). Phi-3 Technical Report: A Highly Capable Language Model Locally on Your Phone. *arXiv preprint arXiv:2404.14219*.
2. Aguilar, G., Kar, S., & Solorio, T. (2020). LinCE: A Centralized Benchmark for Linguistic Code-switching Evaluation. In *Proceedings of LREC 2020* (pp. 1805–1813).
3. Bali, K., Sharma, J., Choudhury, M., & Vyas, Y. (2014). "I am borrowing ya mixing?" An Analysis of English-Hindi Code-Mixed Tweets. In *Proceedings of the First Workshop on Computational Approaches to Code Switching* (pp. 116–126).
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
14. Khanuja, S., et al. (2020). GLUECoS: An Evaluation Benchmark for Code-Switched NLP. In *Proceedings of ACL 2020* (pp. 3575–3585).
15. Li, J., Galley, M., Brockett, C., Gao, J., & Dolan, B. (2016). A Diversity-Promoting Objective Function for Neural Conversation Models. In *Proceedings of NAACL-HLT 2016* (pp. 110–119).
16. Liu, Y., et al. (2023). G-Eval: NLG Evaluation using GPT-4 with Better Human Alignment. In *Proceedings of EMNLP 2023* (pp. 2511–2522).
17. Mann, H. B., & Whitney, D. R. (1947). On a test of whether one of two random variables is stochastically larger than the other. *Annals of Mathematical Statistics*, 18(1), 50–60.
18. Myers-Scotton, C. (1993). *Duelling Languages: Grammatical Structure in Codeswitching*. Oxford University Press.
19. Nayak, R., & Joshi, R. (2022). L3Cube-HingCorpus and HingBERT: A Code Mixed Hindi-English Dataset and BERT Language Models. In *Proceedings of the 6th Workshop on Indian Language Data: Resources and Evaluation (WILDRE-6) at LREC 2022* (pp. 64–69).
20. Nayak, R., & Joshi, R. (2022b). L3Cube-HingBERT: Pretrained Language Models for Code-Mixed Hindi-English NLP. *IEEE Access*, 10, 114580–114592.
21. Patro, S., Bansal, P., Mukherjee, A., & Choudhury, M. (2017). 'All that is English may be Hindi!' In *Proceedings of EMNLP 2017* (pp. 2482–2491).
22. Poplack, S. (1980). Sometimes I'll start a sentence in Spanish Y TERMINO EN ESPANOL. *Linguistics*, 18(7-8), 581–618.
23. Radford, A., et al. (2019). Language Models are Unsupervised Multitask Learners. *OpenAI Technical Report*.
24. Sitaram, S., et al. (2019). A survey of code-switched speech and language processing. *arXiv preprint arXiv:1904.00784*.
25. Spearman, C. (1904). The proof and measurement of association between two things. *American Journal of Psychology*, 15(1), 72–101.
26. Srivastava, V., & Singh, M. (2020). PHINC: A Parallel Hinglish Social Media Code-Mixed Corpus for Machine Translation. In *Proceedings of W-NUT 2020 at EMNLP 2020* (pp. 41–49).
27. Wang, P., et al. (2023). Large Language Models are not Fair Evaluators. *arXiv preprint arXiv:2305.17926*.
28. Wilcoxon, F. (1945). Individual comparisons by ranking methods. *Biometrics Bulletin*, 1(6), 80–83.
29. Yang, A., et al. (2024). Qwen2.5 Technical Report. *arXiv preprint arXiv:2412.15115*.
30. Zheng, L., et al. (2023). Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena. In *Advances in Neural Information Processing Systems (NeurIPS 2023)*, Vol. 36.
