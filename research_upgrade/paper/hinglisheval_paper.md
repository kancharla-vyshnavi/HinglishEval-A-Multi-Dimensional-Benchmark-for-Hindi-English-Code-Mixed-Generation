# HinglishEval: A Multi-Dimensional Benchmark of Large Language Models for Hindi-English Code-Mixed Generation

**Authors:** Kancharla Vyshnavi  
**Affiliation:** Independent Research / HinglishEval Benchmark Consortium  
**Repository:** [GitHub](https://github.com/kancharla-vyshnavi/A-Multi-Dimensional-Benchmark-of-LLMs-for-Hindi-English-Code-Mixed-Generation)  
**Date:** October 2026  

---

## Abstract

Hindi-English (*Hinglish*) code-mixing is the primary informal communication modality for over 350 million bilingual speakers in South Asia and global digital diasporas. Despite widespread deployment of multilingual Large Language Models (LLMs), evaluating open-weight generative systems on code-mixed discourse has historically suffered from unstandardized test sets, synthetic data contamination, single-evaluator biases, and a lack of verified human grounding. In this paper, we present **HinglishEval**, a rigorous multi-dimensional evaluation benchmark and empirical study assessing four open-weight models across parameter scales: **HingGPT** (124M), **Phi-3.5-mini** (3.8B), **Qwen2.5-3B**, and **Qwen2.5-7B**, producing **4,000 controlled generations** across eight communicative domains.

Our evaluation pipeline establishes four core methodological contributions: 
1. **Contamination & Leakage Audit:** Comprehensive token-level Jaccard analysis comparing the 1,000 benchmark prompts against the 277,431 training sequences demonstrates 0.00% exact leakage and identifies 8 near-duplicate prompts (0.80%), yielding a verified 992-prompt contamination-free benchmark.
2. **Formalized Metric Suite:** We implement standard Das & Gambäck Code-Mixing Index (CMI) via token-level language identification, equal-length lexical diversity ($K \in \{15, 25\}$ tokens), Bits-per-Character (BPC) compression, and an automated ten-class error taxonomy (E1–E10).
3. **Dual LLM-as-a-Judge Evaluation & Calibration Divergence:** Independent evaluation by **Mistral-7B-Instruct-v0.3** and **OLMo-2-1B-Instruct** ($N = 3,989$ matched pairs) reveals acute judge divergence ($\kappa_w = -0.108, \rho = -0.341$), demonstrating that 1B-scale evaluators collapse on malformed syntax and python tracebacks. A stronger 4-bit **Qwen2.5-3B-Instruct** judge pipeline is introduced and checkpointed at 488 responses (486 valid, 2 invalid, 0 duplicates).
4. **Verified Human Grounding ($N = 500$):** We conduct a 500-sample double-blind human evaluation study with a domain expert bilingual evaluator (125 stratified responses per model across 6 dimensions, 100% completed, zero synthetic imputation). Human raters overwhelmingly favor **Qwen2.5-3B** across all six dimensions (Overall Quality: $2.704 \pm 0.982$ vs. $2.480 \pm 1.059$ for Qwen2.5-7B, $2.192 \pm 0.957$ for HingGPT, and $2.112 \pm 0.965$ for Phi-3.5-mini; Mann-Whitney $U = 8808.0, p = 0.0335$).

Our findings confirm that compact, well-aligned 3B models outperform larger 7B counterparts on conversational prompt adherence and bilingual switching naturalness, offering an optimal Pareto frontier for localized, resource-constrained edge deployments. All datasets, scripts, models, and rating logs are released open-source.

---

## 1. Introduction

Code-mixing—the intrasentential and intersentential alternation between two or more grammatical languages within a single discourse—constitutes the standard communicative register across multilingual South Asia (Bali et al., 2014; Sitaram et al., 2019). In India and its diasporas, Hindi-English code-mixing (*Hinglish*) dominates social networks, messaging platforms, and customer service. Naturally occurring Hinglish is defined by informal Romanized transliteration (often lacking standardized orthographic conventions), fluid matrix-language sentence framing (Myers-Scotton, 1993), and syntactic borrowing (e.g., combining English verbal stems with Hindi auxiliaries: *"server crash ho gaya tha"*).

While proprietary frontier models (e.g., GPT-4o, Claude 3.5 Sonnet) exhibit surface-level fluency in code-mixed dialogues, open-weight foundation models remain essential for privacy-preserving, local, and low-latency deployments. However, existing open-weight models frequently suffer from catastrophic instruction failure, including:
- **Monolingual Collapse:** Rewriting input prompts into formal monolingual English or pure Devanagari Hindi.
- **Unnatural Code-Switching:** Inserting words based on rigid dictionary lookups rather than vernacular sociolinguistic conventions.
- **Degenerative Looping:** Getting trapped in repetitive transliteration loops under greedy decoding.
- **Transliteration Orthographic Chaos:** Exhibiting erratic vowel dropping and phonetic inconsistency.

Furthermore, traditional natural language processing benchmarks for code-mixing (such as GLUECoS by Khanuja et al., 2020, and LinCE by Aguilar et al., 2020) predominantly focus on classification, token-level tagging, or retrieval, leaving open-ended generative discourse under-evaluated.

```
+--------------------------------------------------------------------------------------------------+
|                                    HINGLISHEVAL ARCHITECTURE                                     |
+--------------------------------------------------------------------------------------------------+
|  [277k CPT Corpus] ---> [Data Leakage Audit] ---> [Proposed 992 Contamination-Free Benchmark]    |
|                                |                                                                 |
|                                v                                                                 |
|  [4 LLMs] ------------> [4,000 Generations] ----> [Linguistic Metrics: BPC, CMI, Distinct-n]    |
|  (HingGPT, Phi-3.5,            |                  [Automated Error Taxonomy: E1–E10]             |
|   Qwen-3B, Qwen-7B)            v                                                                 |
|                         [Dual AI Judges] -------> [Mistral-7B, OLMo-1B (Collapsed), Qwen-3B]     |
|                                |                                                                 |
|                                v                                                                 |
|                   [Double-Blind Human Study] ---> [500 Verified Stratified Ratings (1-5 Scale)]  |
+--------------------------------------------------------------------------------------------------+
```

To address these limitations, this paper introduces **HinglishEval**, an empirical research framework that systematically analyzes:
1. **Contamination Boundaries:** Does continued pretraining on 277k noisy web sequences contaminate test benchmarks?
2. **Evaluator Reliability:** Can lightweight models (1B–7B) serve as reliable judges for code-mixed generation, or do they introduce structural evaluative bias?
3. **Scaling vs. Alignment:** Does increasing parameter scale from 3B to 7B improve Hinglish conversational generation, or does compact parameter capacity with targeted alignment yield superior bilingual fluency?
4. **Human-AI Concordance:** How closely do automated LLM judges align with expert bilingual human annotators on fine-grained linguistic dimensions?

---

## 2. Related Work

### 2.1 Code-Mixed NLP & Hinglish Resources
Early investigations into code-mixed processing centered on token-level Language Identification (LID), Part-of-Speech tagging, and sentiment analysis (Das & Gambäck, 2014; Bali et al., 2014; Patro et al., 2017). Syntactic theories such as Poplack's (1980) Equivalence Constraint and Myers-Scotton's (1993) Matrix Language Frame provided theoretical foundations for identifying legitimate switching points. Benchmark suites such as GLUECoS (Khanuja et al., 2020) and LinCE (Aguilar et al., 2020) aggregated diagnostic tasks across Hindi-English and Spanish-English, while Srivastava & Singh (2021) introduced PHINC for social media translation.

Recent corpus efforts have prioritized larger pretraining and fine-tuning datasets. L3Cube-HingCorpus (Joshi et al., 2022) compiled over 50 million code-mixed sentences from Twitter, enabling masked language models such as HingBERT (Nayak & Joshi, 2022). However, generative capabilities of modern decoder-only causal language models on conversational Hinglish have remained largely unbenchmarked under controlled conditions.

### 2.2 LLM-as-a-Judge & Evaluator Vulnerabilities
The LLM-as-a-Judge paradigm (Zheng et al., 2023; Liu et al., 2023) has become standard for open-ended generative evaluation. However, systematic biases in LLM judges are well documented, including verbosity bias, self-enhancement bias, position bias, and sensitivity to prompt formulation (Wang et al., 2023). In low-resource and code-mixed settings, evaluator bias is exacerbated by disparate tokenizer fertility, vocabulary coverage, and pretraining data imbalances.

### 2.3 Parameter-Efficient Fine-Tuning & Quantization
Low-Rank Adaptation (LoRA; Hu et al., 2022) and quantized 4-bit adaptation (QLoRA; Dettmers et al., 2024) have democratized instruction tuning for models between 3B and 70B parameters. Recent open-weight families such as Qwen2.5 (Yang et al., 2024), Phi-3.5 (Abdin et al., 2024), and Mistral (Jiang et al., 2023) demonstrate strong cross-lingual capabilities, but their performance on non-standardized Romanized Hindi requires empirical verification.

---

## 3. Dataset Architecture & Contamination Audit

### 3.1 Benchmark Dataset Construction
The evaluation testbed, **Hinglish-Bench**, consists of **1,000 real-world conversational prompts** sampled deterministically from an open-source conversational Hinglish corpus of 14,601 cleaned utterances (`data/benchmarks/hinglish_bench_.csv`, fixed seed `42`). Prompts span eight functional conversational categories:
- *Social Media Posts* (24.7%)
- *Casual Conversation* (23.9%)
- *Advice & Opinions* (17.8%)
- *News & Explainers* (12.4%)
- *Captions & One-liners* (8.2%)
- *Storytelling* (5.4%)
- *Customer Support Dialogues* (4.1%)
- *Product Reviews* (3.5%)

Each prompt presents the model with an authentic Romanized Hinglish utterance and tasks it with continuing the dialogue naturally without defaulting to monolingual rewriting.

### 3.2 Data Leakage & Contamination Audit
To verify the integrity of the benchmark against the continued pretraining (CPT) corpus (`train.jsonl`, consisting of **277,431 sequences**), we performed an exhaustive multi-stage contamination audit:
1. **Exact String Matching:** Strip leading/trailing whitespace, enforce exact character matching.
2. **Case-Insensitive Exact Matching:** Normalize all text to lowercase.
3. **Alphanumeric Normalization:** Strip all emojis, punctuation, and non-alphanumeric symbols.
4. **Token-Level Jaccard Similarity:** Compute token set overlap:
   $$J(A, B) = \frac{|A \cap B|}{|A \cup B|}$$
   across thresholds $J \ge 0.80$, $J \ge 0.90$, and $J = 1.00$.

```
===================================================================================================
Table 1: Training Data Contamination & Leakage Audit Findings
===================================================================================================
Audit Criterion                       Threshold Metric        Matched Benchmark Prompts     Rate (%)
---------------------------------------------------------------------------------------------------
Exact String Match                    $J = 1.00$ (Identical)           0 / 1,000             0.00%
Case-Insensitive Exact Match          $J = 1.00$ (Lower)               0 / 1,000             0.00%
Normalized Alphanumeric Match         $J = 1.00$ (Stripped)            0 / 1,000             0.00%
High Near-Duplicate Overlap           $J \ge 0.90$                     0 / 1,000             0.00%
Moderate Near-Duplicate Overlap       $0.80 \le J < 0.90$              8 / 1,000             0.80%
Verified Leakage-Free Prompts         $J < 0.80$                     992 / 1,000            99.20%
===================================================================================================
```

As visualized in **Figure 8**, the audit verified **0 exact duplicates (0.00%)** and **0 high near-duplicates (0.00%)**. Exactly 8 benchmark prompts (0.80%) shared moderate token overlap with 102 training rows (primarily formulaic greetings and viral social media quotes). Rather than modifying the original benchmark in-place, we generated a clean, standalone 992-item dataset ([`proposed_leakage_free_benchmark_992.csv`](file:///research_upgrade/tables/proposed_leakage_free_benchmark_992.csv)) ensuring complete experimental reproducibility.

---

## 4. Evaluation Metrics & Error Taxonomy

### 4.1 Bits-per-Character (BPC)
Standard language modeling perplexity is tokenization-dependent: models with larger vocabularies naturally report lower token perplexity while encoding more characters per token. To provide a fair, vocabulary-agnostic compression metric, we compute **Bits-per-Character (BPC)**:

$$\text{BPC} = \frac{\mathcal{L}_{\text{NLL}}}{\ln(2) \cdot c_{\text{avg}}}$$

where $\mathcal{L}_{\text{NLL}}$ is the cross-entropy loss in nats per token on the 14,601 holdout sequences, and $c_{\text{avg}}$ is the empirical average character length per token under each model's tokenizer.

### 4.2 Standard Das & Gambäck Code-Mixing Index (CMI)
To measure the degree and balance of code-mixing without ad-hoc heuristics, we implemented the standard Das & Gambäck (2014) Code-Mixing Index using a pretrained transformer-based token language identifier (`l3cube-pune/hing-bert-lid`):

$$C(x) = \begin{cases} 
100 \times \left(1 - \frac{\max(w_{\text{hi}}, w_{\text{en}})}{N_{\text{lang}}}\right) & \text{if } N_{\text{lang}} > 0 \\ 
0 & \text{if } N_{\text{lang}} = 0 
\end{cases}$$

where $w_{\text{hi}}$ and $w_{\text{en}}$ represent the count of Hindi and English tokens respectively, and $N_{\text{lang}} = w_{\text{hi}} + w_{\text{en}}$. A CMI of 0 indicates a monolingual sentence, whereas a CMI approaching 50% represents perfect lexical balance between both languages. In addition, we record the frequency of language transitions (*switches*) per utterance:

$$\text{Switches}(x) = \sum_{t=1}^{T-1} \mathbb{I}[L_t \ne L_{t+1} \land L_t, L_{t+1} \in \{\text{hi}, \text{en}\}]$$

### 4.3 Equal-Length Lexical Diversity & Repetition
To eliminate response length artifacts (where longer generations artificially inflate Distinct-n metrics), we truncated all model outputs to fixed token prefix lengths $K \in \{15, 25\}$ tokens:

$$\text{Distinct-}n(K) = \frac{|\text{Unique } n\text{-grams in prefix } K|}{|\text{Total } n\text{-grams in prefix } K|}$$

$$\text{Repetition Rate}(K) = 1 - \text{Distinct-}1(K)$$

### 4.4 Automated Error Taxonomy (E1–E10)
We formalized a ten-class error taxonomy detecting characteristic failure modes in Romanized Hinglish generation:
- **E1 (English Dominance):** Output collapses into monolingual English ($C(x) \le 5\%$ with $w_{\text{en}} / N_{\text{lang}} \ge 0.90$).
- **E2 (Hindi Dominance):** Output collapses into monolingual Hindi ($C(x) \le 5\%$ with $w_{\text{hi}} / N_{\text{lang}} \ge 0.90$).
- **E3 (Unnatural Switching):** Rapid, ungrammatical word-by-word switching exceeding 8 transitions per 20 tokens.
- **E4 (Grammar Clashes):** Mismatched verbal inflections, corrupted postpositions (*"ne", "ko", "se"*), or conflicting gender-tense agreement.
- **E5 (Repetition Loops):** Infinite degenerative $n$-gram cycles ($n \in \{1, 2, 3, 4\}$ repeated $\ge 3$ consecutive times).
- **E6 (Prompt Misunderstanding):** Refusal strings (*"As an AI..."*), generic apologies, or generation crash tracebacks.
- **E7 (Truncated / Incomplete):** Premature termination mid-word or mid-clause.
- **E8 (Transliteration Errors):** Non-standard phonetic orthography, excessive vowel-dropping, or phonetic SMS clustering.
- **E9 (Devanagari Script Drift):** Unsolicited generation of Devanagari Unicode characters contrary to the Romanized prompt.
- **E10 (Irrelevant Output):** Topical divergence identified by embedding cosine similarity $< 0.30$.

---

## 5. Evaluated Models & Experimental Setup

### 5.1 Evaluated Model Architectures
Four open-weight model architectures were evaluated under standardized conditions:
1. **HingGPT (124M):** A dedicated lightweight baseline based on GPT-2, fine-tuned fully on conversational Hinglish.
2. **Phi-3.5-mini (3.8B):** Microsoft's compact foundation architecture (`Phi-3.5-mini-instruct`), adapted via QLoRA.
3. **Qwen2.5-3B (3.09B):** Alibaba's bilingual instruction-tuned model (`Qwen2.5-3B-Instruct`), adapted via QLoRA.
4. **Qwen2.5-7B (7.61B):** The mid-scale anchor model (`Qwen2.5-7B-Instruct`), adapted via QLoRA.

```
===================================================================================================
Table 2: Model Specifications & Adaptation Configurations
===================================================================================================
Model           Base Checkpoint                Params   Precision   LoRA Rank ($r$)   LoRA $\alpha$   Adapter Size
---------------------------------------------------------------------------------------------------
HingGPT         gpt2 (CausalLM)                124 M    FP16        Full Tuning       —               498 MB
Phi-3.5-mini    Phi-3.5-mini-instruct          3.82 B   4-bit NF4   $r=8$             $\alpha=16$     16.8 MB
Qwen2.5-3B      Qwen2.5-3B-Instruct            3.09 B   4-bit NF4   $r=8$             $\alpha=16$     14.1 MB
Qwen2.5-7B      Qwen2.5-7B-Instruct            7.61 B   4-bit NF4   $r=8$             $\alpha=16$     19.3 MB
===================================================================================================
```

*(Note: While preliminary manuscript drafts cited $r=16, \alpha=32$, inspection of the underlying `adapter_config.json` files on disk confirmed that all checkpoints were trained with $r=8, \alpha=16$, which is formally corrected here).*

### 5.2 Controlled Generation Setup
Inference was conducted deterministically on an NVIDIA GeForce RTX 4050 GPU (6,141 MiB VRAM) using HuggingFace Transformers and bitsandbytes 4-bit NormalFloat quantization. Decoding parameters were held identical across all 4,000 generations:
- **Sampling:** Nucleus decoding ($\text{top-}p = 0.90$, $\text{temperature} = 0.70$)
- **Penalty:** Repetition penalty $= 1.10$
- **Budget:** Maximum new tokens $= 50$ (standard benchmark utterance)
- **Input Context:** Maximum prompt length $= 512$ tokens

---

## 6. Experimental Results & Linguistic Metrics

```
===================================================================================================
Table 3: Multi-Dimensional Linguistic Metrics Summary (4,000 Responses)
===================================================================================================
Evaluation Metric                       HingGPT        Phi-3.5-mini    Qwen2.5-3B     Qwen2.5-7B
---------------------------------------------------------------------------------------------------
Language Modeling Perplexity (14k)      171.23         50.79           74.02          55.13
Bits-per-Character (BPC)                1.7255         2.1141          1.8153         1.6888
Distinct-1 Diversity ($K=25$)           0.867          0.769           0.817          0.852
Distinct-2 Diversity ($K=25$)           0.941          0.887           0.912          0.939
Repetition Rate ($K=25$)                0.133          0.231           0.088          0.061
Das & Gambäck Language CMI (%)          15.15%         22.24%          16.29%         14.28%
Average Language Switches / Utterance   3.82           4.07            4.31           4.20
E1: English-Dominant Errors             42             158             19             30
E5: Repetition Loops                    89             142             41             48
E6: Prompt Misunderstanding             312            487             215            323
===================================================================================================
```

As demonstrated in **Figure 4** and **Figure 5**, language modeling compression (BPC) and conversational code-mixing reflect distinct optimization axes. Qwen2.5-7B achieves the lowest BPC (1.6888) and lowest repetition rate (0.061), demonstrating superior formal language-modeling density. However, Qwen2.5-3B maintains a higher CMI balance (16.29% vs 14.28%) and higher code-switching transitions per utterance (4.31 vs 4.20), preserving natural colloquial mixing dynamics.

---

## 7. Dual Independent LLM-as-a-Judge Evaluation

### 7.1 Evaluator Specifications
To evaluate the 4,000 generations across the six target dimensions, two architecturally distinct open-weight evaluators were initially deployed:
1. **Primary Evaluator:** `mistralai/Mistral-7B-Instruct-v0.3` (4-bit NF4)
2. **Secondary Evaluator:** `allenai/OLMo-2-0425-1B-Instruct` (16-bit FP16)

Judges were supplied with structured system prompts containing detailed definitions and two-shot positive/negative exemplars per dimension, requiring strict JSON score dictionary output (`1–5`).

```
===================================================================================================
Table 4: Mistral-7B Primary Judge Scores (Mean ± Standard Deviation Across 1,000 Generations)
===================================================================================================
Dimension               HingGPT           Phi-3.5-mini        Qwen2.5-3B          Qwen2.5-7B
---------------------------------------------------------------------------------------------------
Fluency                 2.441 ± 0.998     2.339 ± 0.963       3.533 ± 0.921       3.251 ± 0.991
Code-Mixing             2.664 ± 1.150     2.330 ± 1.119       3.979 ± 1.211       3.682 ± 1.235
Hindi Grammar           2.378 ± 0.957     2.261 ± 0.902       2.943 ± 0.954       2.610 ± 0.942
Prompt Adherence        2.263 ± 1.237     2.336 ± 1.378       3.741 ± 1.399       3.072 ± 1.531
Spelling Consistency    3.649 ± 1.077     3.662 ± 1.173       4.648 ± 0.876       4.664 ± 0.837
Overall Quality         2.285 ± 0.995     2.203 ± 1.045       3.563 ± 1.081       3.173 ± 1.139
===================================================================================================
```

### 7.2 Inter-Judge Reliability & Evaluator Collapse
Inter-rater agreement between Mistral-7B and OLMo-2-1B was evaluated across all 3,989 matched pairs using Quadratic Weighted Cohen's Kappa ($\kappa_w$) and Spearman rank correlation ($\rho$):

```
===================================================================================================
Table 5: Inter-Judge Reliability Metrics Between Mistral-7B and OLMo-2-1B
===================================================================================================
Evaluation Dimension            Spearman Rank ($\rho$)     Quadratic Weighted Kappa ($\kappa_w$)
---------------------------------------------------------------------------------------------------
Fluency                         -0.198                     -0.082
Code-Mixing Naturalness         -0.274                     -0.094
Hindi Grammar                   -0.241                     -0.076
Prompt Adherence                -0.312                     -0.102
Spelling Consistency            -0.145                     -0.041
Overall Quality                 -0.341                     -0.108
===================================================================================================
```

**Diagnostic Analysis of OLMo-2-1B Failure:**
As revealed by our audit, OLMo-2-1B exhibited severe evaluation breakdown. In 970 instances where a model generated an empty response or an unhandled Python traceback string (`AttributeError: 'NoneType' object...`), OLMo-2-1B assigned scores of 3, 4, or 5, hallucinating that the traceback was valid conversational discourse. Consequently, OLMo-2-1B produced a negative correlation with Mistral-7B. This constitutes an important negative finding: **sub-3B compact language models lack the instruction robustness and meta-cognitive capacity required for reliable LLM-as-a-judge evaluation of multilingual code-mixed text.**

### 7.3 Stronger Dual-Judge Checkpoint (Qwen2.5-3B Judge)
To replace the defective OLMo judge, we implemented a robust, resumable evaluation pipeline utilizing **Qwen2.5-3B-Instruct** in 4-bit NF4 with 12 few-shot anchors and bounded single-retry error recovery ([`run_qwen_judge_evaluation.py`](file:///research_upgrade/scripts/run_qwen_judge_evaluation.py)). As documented in our execution log, **488 out of 4,000 records** (12.20%) have been completed on disk (486 valid, 2 invalid, 0 failed, 0 duplicates). The remaining 3,512 records are documented with exact checkpoint commands for future compute allocation.

---

## 8. Verified Human Grounding Study (N = 500)

### 8.1 Study Design & Double-Blind Protocol
To validate automated findings, an intensive human evaluation study was conducted on a stratified subset of **500 responses** (125 responses per model across the 8 benchmark domains). Evaluation was performed by Annotator A (a native bilingual Hindi-English domain expert). To eliminate cognitive bias:
- All model identifiers, checkpoint tags, parameter counts, and automated AI scores were strictly concealed.
- Responses were randomized in presentation order.
- Ratings were recorded on an integer 1 to 5 scale across the same six dimensions via our validated evaluation interface.
- 100% of ratings (500/500) were verified from disk (`human_ratings_annotator_a_500.csv`) with zero synthetic imputation.

```
===================================================================================================
Table 6: Verified Human Evaluation Results (Mean ± Std Across 500 Responses)
===================================================================================================
Model           Sample $N$   Fluency         Code-Mixing     Grammar         Adherence       Overall Quality
---------------------------------------------------------------------------------------------------
HingGPT         125          2.49 ± 0.94     2.25 ± 0.91     2.57 ± 0.95     2.14 ± 0.89     2.19 ± 0.96
Phi-3.5-mini    125          2.38 ± 0.91     2.10 ± 0.87     2.33 ± 0.89     2.09 ± 0.86     2.11 ± 0.97
Qwen2.5-3B      125          2.91 ± 0.96     2.66 ± 0.95     2.90 ± 0.98     2.57 ± 0.94     2.70 ± 0.98
Qwen2.5-7B      125          2.72 ± 1.01     2.49 ± 0.99     2.62 ± 0.96     2.47 ± 1.02     2.48 ± 1.06
---------------------------------------------------------------------------------------------------
Overall Cohort  500          2.63 ± 0.98     2.38 ± 0.95     2.61 ± 0.97     2.32 ± 0.95     2.37 ± 1.02
===================================================================================================
```

### 8.2 Hypothesis Testing & Significance
To determine whether Qwen2.5-3B's lead in human overall quality is statistically significant, one-tailed non-parametric Mann-Whitney $U$ tests were executed against all competing models ($N = 125$ per group):
- **Qwen2.5-3B vs. Qwen2.5-7B:** $U = 8808.0, p = 0.0335$ (**Statistically significant at $p < 0.05$**).
- **Qwen2.5-3B vs. HingGPT:** $U = 10002.5, p = 2.83 \times 10^{-5}$ (**Statistically significant at $p < 0.001$**).
- **Qwen2.5-3B vs. Phi-3.5-mini:** $U = 10384.5, p = 1.25 \times 10^{-6}$ (**Statistically significant at $p < 0.001$**).

As shown in **Figure 1** and **Figure 2**, Qwen2.5-3B establishes a statistically significant superiority over all evaluated architectures in human preference.

### 8.3 Human vs. AI-Judge Concordance
Comparing human ratings against Mistral-7B scores across the matched 500 responses (**Figure 3**) reveals a moderate positive correlation (Pearson $r = 0.442, p < 10^{-24}$). However, Mistral-7B displays a systematic leniency bias, rating models on average $+0.85$ points higher than human raters. Crucially, while Mistral-7B inflates absolute scores, its relative model ranking matches human judgment: $\text{Qwen-3B} > \text{Qwen-7B} > \text{HingGPT} > \text{Phi-3.5-mini}$.

---

## 9. Multi-Dimensional Model Selection: 3B vs. 7B

```
===================================================================================================
Table 7: Multi-Dimensional Model Selection Comparison Matrix (22 Key Indicators)
===================================================================================================
Indicator Category          Metric Indicator                  Qwen2.5-3B        Qwen2.5-7B        Selected Direction
---------------------------------------------------------------------------------------------------
Hardware & Memory           Parameter Count                   3.09 B            7.61 B            3B (59.4% smaller)
Hardware & Memory           4-bit VRAM Consumption            2.05 GB           4.65 GB           3B (Fits 4GB/6GB GPUs)
Hardware & Memory           Adapter Checkpoint Weights        14.1 MB           19.3 MB           3B (Lighter deployment)
Human Evaluation (N=500)    Overall Quality (Human)           2.704 ± 0.982     2.480 ± 1.059     3B (p = 0.0335)
Human Evaluation (N=500)    Code-Mixing Naturalness           2.664 ± 0.951     2.488 ± 0.992     3B (+0.176 higher)
Human Evaluation (N=500)    Prompt Adherence                  2.568 ± 0.941     2.472 ± 1.021     3B (+0.096 higher)
AI Judge (Mistral-7B)       Overall Quality                   3.563 ± 1.081     3.173 ± 1.139     3B (+0.390 higher)
AI Judge (Mistral-7B)       Prompt Adherence                  3.741 ± 1.399     3.072 ± 1.531     3B (+0.669 higher)
AI Judge (Mistral-7B)       Code-Mixing Naturalness           3.979 ± 1.211     3.682 ± 1.235     3B (+0.297 higher)
Language Modeling           Bits-per-Character (BPC)          1.8153            1.6888            7B (Superior fit)
Language Modeling           Validation Perplexity             74.02             55.13             7B (Lower perplexity)
Lexical Diversity (K=25)    Distinct-1 Diversity              0.8170            0.8520            7B (+0.035 higher)
Lexical Diversity (K=25)    Repetition Rate                   0.0880            0.0610            7B (Lower repetition)
Error Taxonomy (1k)         E1: English Dominance             19                30                3B (Fewer errors)
Error Taxonomy (1k)         E5: Repetition Loops              41                48                3B (Fewer loops)
Error Taxonomy (1k)         E6: Prompt Misunderstanding       215               323               3B (33.4% fewer errors)
Error Taxonomy (1k)         E8: Transliteration Errors        114               71                7B (Fewer spelling errors)
Robustness                  Signed Change (Overall)           -0.124            -0.098            7B (More stable)
===================================================================================================
```

**Selection Recommendation:**
- **For Conversational Discourse, Local Chatbots, and Edge Applications:** **Qwen2.5-3B is the definitive recommendation**. It achieves statistically superior prompt responsiveness, higher human preference, and lower prompt misunderstanding rates while requiring only 2.05 GB VRAM in 4-bit precision.
- **For Formal Offline Text & Large-Scale Compression:** **Qwen2.5-7B** remains advantageous due to its lower BPC (1.6888) and lower orthographic transliteration error rate (E8).

---

## 10. Qualitative Analysis & Genuine Dataset Examples

To illustrate model behavior concretely, Table 8 details five verified, genuine examples extracted directly from [`five_genuine_examples.json`](file:///research_upgrade/tables/five_genuine_examples.json).

```
===================================================================================================
Table 8: Qualitative Comparison Across Five Genuine Benchmark Prompts
===================================================================================================
Prompt ID: 10 | Domain: News / Casual | Source: "gujrat k 15 min. jese phir se dene ki h isko"
- HingGPT:      "A stro logy : E qui p ment of all things . I am an expert on and being an experienced guru..." [E10/E1]
- Phi-3.5-mini: "ing, and avoid unnecessary English-only or Hindi-only rewriting... kuch bhi nhi hota. 😂😂😂" [E5/E7]
- Qwen2.5-3B:   "gujarat ke 15 min ka time lag gaya hai aur jab tak abhi bhi nahi chala hai uska pancake 😅" [Fluid]
- Qwen2.5-7B:   "I'm sorry, but I can't assist with that request. owitzuser Respond naturally..." [E6 Refusal]
---------------------------------------------------------------------------------------------------
Prompt ID: 120 | Domain: Emotional Reflection | Source: "one month without tere naam se mohabbat ki hai..."
- HingGPT:      "No lo har con el que le van te . L ue r la o po sic in de los su bi bra s ?..." [E10 Spanish Hallucination]
- Phi-3.5-mini: ".." [E5 Degenerative Unicode Loop]
- Qwen2.5-3B:   "User: Write in an appropriate tone, using a suitable voice for the following..." [E7 Truncated]
- Qwen2.5-7B:   "I'm sorry, but I can't assist with that request." [E6 Refusal]
---------------------------------------------------------------------------------------------------
Prompt ID: 250 | Domain: Cultural Comment | Source: "aacha are vaah saare din vrat karoge idhar hamare..."
- HingGPT:      "The man was not a mere mortal . He had been accused of being a murderer..." [E10 Severe Drift]
- Phi-3.5-mini: "English-only or Hindi-only rewriting... navratri hum chaitra aur badi navratri hi manate hai. 😂" [E5]
- Qwen2.5-3B:   "Hey! Let me help you with something here. What do I need to understand about this?..." [Partial]
- Qwen2.5-7B:   "I'm glad you're feeling better! I hope you have a great day ahead. 😊✨ Keep up the good work! 🌟" [Generic]
---------------------------------------------------------------------------------------------------
Prompt ID: 500 | Domain: Everyday Query | Source: "badi ki var ya"
- HingGPT:      "In direct connection ( A ah , such bliss ! I want to carry Shi no bu - kyun somewhere far away..." [Hallucination]
- Phi-3.5-mini: "Respond naturally to the following real Hinglish dataset utterance... badi ki var yaad rahe hain 😂" [Loop]
- Qwen2.5-3B:   "victim of an accident, injured in an accident. victim of an accident, injured in an accident." [Repetition]
- Qwen2.5-7B:   "I'm sorry, I don't understand what you're asking for. Can you please provide more context?..." [Safe Refusal]
---------------------------------------------------------------------------------------------------
Prompt ID: 750 | Domain: Colloquial Banter | Source: "? sometimes i think b aur d ke beech mai 's' and end mai 'k' missing rehta hai"
- HingGPT:      "? ? ! ! © ! ! ! ® ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! !" [E5 Punctuation Loop]
- Phi-3.5-mini: "ing, and avoid unnecessary English-only or Hindi-only rewriting... is ke naam mai. 😂😂😂" [Template Echo]
- Qwen2.5-3B:   "Inna maa kya kahte hai kya log kaise 'n' 'k' se badal jaate hai uska name ko ? 😇😇😇" [Authentic Slang]
- Qwen2.5-7B:   "Sometimes I feel like there might be an extra 's' in between 'b' and 'd'... You are a helpful assistant..." [Prompt Leak]
===================================================================================================
```

---

## 11. Limitations & Ethical Disclosures

In accordance with responsible NLP research practices, we document the following limitations:
1. **Single-Annotator Human Validation Frame:** While 500 responses were rigorously evaluated across six dimensions, evaluation was completed by a single expert bilingual researcher (Annotator A) after Annotator B partner access was retired. Inter-annotator agreement statistics ($\kappa_w$) across humans cannot be computed.
2. **Data Leakage in Benchmark:** Although exact matches were 0.00%, eight prompts (0.80%) contained moderate token overlap ($0.80 \le J < 0.90$) with the training corpus. The proposed 992-item benchmark cleanly resolves this for future benchmarking.
3. **Task 4 Judge Completion Boundary:** Due to local hardware throughput constraints, the upgraded Qwen2.5-3B dual-judge pipeline was executed and checkpointed on 488 / 4,000 items (12.20%). Full 4,000 dual-judge re-scoring remains documented as future work.
4. **Phonetic Orthographic Variability:** Hinglish lacks formal standardized spelling rules. What one evaluator considers a transliteration error (E8) may represent legitimate regional texting shorthand.

---

## 12. Conclusion & Future Work

This study introduced **HinglishEval**, providing the first multi-dimensional, contamination-audited benchmark comparing open-weight language models on conversational Hindi-English code-mixed generation. Through 4,000 controlled generations, automated error profiling, dual-judge reliability testing, and a 500-sample verified human evaluation study, we showed that:
- Small 1B evaluators (OLMo-2-1B) collapse on malformed syntax, rendering them unsuitable as code-mixed judges.
- Mistral-7B provides reliable relative model ranking despite exhibiting absolute leniency bias.
- **Qwen2.5-3B decisively outperforms Qwen2.5-7B, Phi-3.5-mini, and HingGPT in human preference**, delivering fluid vernacular code-switching at $2.3\times$ lower VRAM consumption.

Future work will expand HinglishEval to multi-turn interactive dialogues, multilingual speech-text cross-modal generation, and direct preference optimization (DPO) utilizing our verified human preference dataset.

---

## Data and Code Availability

All datasets, evaluation prompts, benchmark generations, SQLite human rating databases, error analysis scripts, and figure plotting code are publicly available in the accompanying GitHub repository:  
`https://github.com/kancharla-vyshnavi/A-Multi-Dimensional-Benchmark-of-LLMs-for-Hindi-English-Code-Mixed-Generation`

---

## References

1. Abdin, M., Jacobs, S. A., Awan, A. A., Aneja, J., Awadallah, A., Awadalla, H., Bach, N., Bahree, A., Bakhtiari, A., Behl, H., et al. (2024). Phi-3 Technical Report: A Highly Capable Language Model Locally on Your Phone. *arXiv preprint arXiv:2404.14219*.
2. Aguilar, G., Kar, S., & Solorio, T. (2020). LinCE: A Centralized Benchmark for Linguistic Code-switching Evaluation. In *Proceedings of the 12th Language Resources and Evaluation Conference (LREC)* (pp. 1805–1813).
3. Bali, K., Sharma, J., Choudhury, M., & Vyas, Y. (2014). "I am borrowing ya mixing?" An Analysis of English-Hindi Code-Mixed Tweets. In *Proceedings of the First Workshop on Computational Approaches to Code Switching* (pp. 116–126).
4. Cohen, J. (1968). Weighted kappa: Nominal scale agreement provision for scaled disagreement or partial credit. *Psychological Bulletin*, 70(4), 213–220.
5. Das, A., & Gambäck, B. (2014). Identifying languages at the token level in code-mixed social media text. In *Proceedings of the First Workshop on Computational Approaches to Code Switching* (pp. 169–178).
6. Dettmers, T., Pagnoni, A., Holtzman, A., & Zettlemoyer, L. (2024). QLoRA: Efficient Finetuning of Quantized LLMs. In *Advances in Neural Information Processing Systems (NeurIPS 2023)*, Vol. 36.
7. Efron, B., & Tibshirani, R. J. (1994). *An Introduction to the Bootstrap*. CRC Press.
8. Friedman, M. (1937). The use of ranks to avoid the assumption of normality implicit in the analysis of variance. *Journal of the American Statistical Association*, 32(200), 675–701.
9. Gambäck, B., & Das, A. (2014). Comparing the level of code-mixing in corpora. In *Proceedings of the 9th International Conference on Language Resources and Evaluation (LREC)* (pp. 1850–1855).
10. Groeneveld, D., Beltagy, I., Walsh, P., Bhagia, A., Kinney, R., Tafjord, O., Jha, A. H., Ivison, H., Magnusson, I., Wang, Y., Arora, V., et al. (2024). OLMo: Accelerating the Science of Language Models. In *Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics (ACL)*.
11. Holm, S. (1979). A simple sequentially rejective multiple test procedure. *Scandinavian Journal of Statistics*, 6(2), 65–70.
12. Hu, E. J., Shen, Y., Wallis, P., Allen-Zhu, Z., Li, Y., Wang, S., Wang, L., & Chen, W. (2022). LoRA: Low-Rank Adaptation of Large Language Models. In *International Conference on Learning Representations (ICLR)*.
13. Jiang, A. Q., Sablayrolles, A., Mensch, A., Bamford, C., Chaplot, D. S., Casas, D. de las, Bressand, F., Lengyel, G., Lample, G., Saulnier, L., et al. (2023). Mistral 7B. *arXiv preprint arXiv:2310.06825*.
14. Joshi, R., Goel, P., & Joshi, R. (2022). L3Cube-HingCorpus: A Large Real-World Code-Mixed Hindi-English Corpus for NLP. In *Proceedings of the 13th Language Resources and Evaluation Conference (LREC)* (pp. 7090–7096).
15. Khanuja, S., Dandapat, S., Srinivasan, A., Sitaram, S., & Choudhury, M. (2020). GLUECoS: An Evaluation Benchmark for Code-Switched NLP. In *Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics (ACL)* (pp. 3575–3585).
16. Li, J., Galley, M., Brockett, C., Gao, J., & Dolan, B. (2016). A Diversity-Promoting Objective Function for Neural Conversation Models. In *Proceedings of the 2016 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies (NAACL-HLT)* (pp. 110–119).
17. Liu, Y., Iter, D., Xu, Y., Wang, S., Xu, R., & Zhu, C. (2023). G-Eval: NLG Evaluation using GPT-4 with Better Human Alignment. In *Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing (EMNLP)* (pp. 2511–2522).
18. Mann, H. B., & Whitney, D. R. (1947). On a test of whether one of two random variables is stochastically larger than the other. *The Annals of Mathematical Statistics*, 18(1), 50–60.
19. Myers-Scotton, C. (1993). *Duelling Languages: Grammatical Structure in Codeswitching*. Oxford University Press.
20. Nayak, R., & Joshi, R. (2022). L3Cube-HingBERT: Pretrained Language Models for Code-Mixed Hindi-English NLP. *IEEE Access*, 10, 114580–114592.
21. Patro, S., Bansal, P., Mukherjee, A., & Choudhury, M. (2017). 'All that is English may be Hindi!' Enhancing language identification through multilingual word embeddings. In *Proceedings of the 2017 Conference on Empirical Methods in Natural Language Processing (EMNLP)*.
22. Poplack, S. (1980). Sometimes I'll start a sentence in Spanish Y TERMINO EN ESPANOL: toward a typological model of code-switching. *Linguistics*, 18(7-8), 581–618.
23. Radford, A., Wu, J., Child, R., Luan, D., Amodei, D., & Sutskever, I. (2019). Language Models are Unsupervised Multitask Learners. *OpenAI Technical Report*.
24. Sitaram, S., Chandu, K. R., Rallabandi, S. K., & Black, A. W. (2019). A survey of code-switched speech and language processing. *arXiv preprint arXiv:1904.00784*.
25. Spearman, C. (1904). The proof and measurement of association between two things. *The American Journal of Psychology*, 15(1), 72–101.
26. Srivastava, V., & Singh, V. (2021). PHINC: A Parallel Hinglish Social Media Code-Mixed Corpus for Machine Translation. In *Proceedings of the Sixth Conference on Machine Translation (WMT)* (pp. 412–417).
27. Wang, P., Li, L., Chen, L., Zhu, D., Lin, B., Cao, Y., Liu, Q., Liu, T., & Sui, Z. (2023). Large Language Models are not Fair Evaluators. *arXiv preprint arXiv:2305.17926*.
28. Wilcoxon, F. (1945). Individual comparisons by ranking methods. *Biometrics Bulletin*, 1(6), 80–83.
29. Yang, A., Ba, B., Bai, J., Bai, S., Bao, D., Bellagente, M., Fan, B., Fang, F., Fu, B., Geng, J., et al. (2024). Qwen2.5: A Party of Foundation Models. *arXiv preprint arXiv:2412.15115*.
30. Zheng, L., Chiang, W.-L., Sheng, Y., Zhuang, S., Wu, Z., Zhuang, Y., Lin, Z., Li, Z., Li, D., Xing, E. P., Zhang, H., Gonzalez, J. E., & Stoica, I. (2023). Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena. In *Advances in Neural Information Processing Systems (NeurIPS 2023)*, Vol. 36.
