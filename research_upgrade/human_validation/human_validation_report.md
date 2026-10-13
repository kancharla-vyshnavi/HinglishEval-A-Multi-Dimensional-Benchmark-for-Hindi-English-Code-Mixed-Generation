# HinglishEval: Verified Human Evaluation Report (500 Responses)

**Evaluation Date:** October 2026
**Evaluator:** Annotator A (Lead Bilingual Researcher)
**Sample Size:** Exactly 500 Responses (125 stratified samples per model across 8 domains)
**Validation Status:** 500 records contain complete, valid ratings across all six dimensions; single-annotator evaluation.
**Primary Data Table:** [`human_ratings_annotator_a_500.csv`](file:///C:/Users/vyshu/OneDrive/Desktop/HinglishLLM/research_upgrade/tables/human_ratings_annotator_a_500.csv)

---

## 1. Study Sampling Frame and Balanced Distribution

| Model Architecture | Parameter Count | Adaptation Technique | Sampled $N$ | Completed $N$ | Completion Rate |
| :--- | :---: | :--- | :---: | :---: | :---: |
| **HingGPT** | 124 M | Full Fine-Tuning | 125 | 125 | 100.0% |
| **Phi-3.5-mini** | 3.8 B | QLoRA ($r=8, \alpha=16$) | 125 | 125 | 100.0% |
| **Qwen2.5-3B** | 3.09 B | QLoRA ($r=8, \alpha=16$) | 125 | 125 | 100.0% |
| **Qwen2.5-7B** | 7.61 B | QLoRA ($r=8, \alpha=16$) | 125 | 125 | 100.0% |
| **Total Study Cohort** | — | — | **500** | **500** | **100.0%** |

---

## 2. Overall Dimension Summary Statistics (500 Responses)

| Evaluation Dimension | Mean | Std | Median | 25th % | 75th % | Min | Max |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `fluency` | 2.626 | 1.012 | 3.0 | 2.0 | 3.0 | 1 | 5 |
| `code_mixing_naturalness` | 2.376 | 0.923 | 2.0 | 2.0 | 3.0 | 1 | 5 |
| `hindi_grammar` | 2.606 | 1.006 | 3.0 | 2.0 | 3.0 | 1 | 5 |
| `prompt_adherence` | 2.316 | 0.928 | 2.0 | 2.0 | 3.0 | 1 | 5 |
| `spelling_consistency` | 2.500 | 0.998 | 3.0 | 2.0 | 3.0 | 1 | 5 |
| `overall` | 2.372 | 0.980 | 2.0 | 2.0 | 3.0 | 1 | 5 |

---

## 3. Per-Model Comparative Performance Matrix (Mean ± Std)

| Model Architecture | Fluency | Code-Mixing | Hindi Grammar | Prompt Adherence | Spelling | Overall Quality |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **HingGPT** | 2.49 ± 1.06 | 2.25 ± 0.95 | 2.57 ± 1.07 | 2.14 ± 0.88 | 2.41 ± 1.06 | **2.19 ± 0.90** |
| **Phi-3.5-mini** | 2.38 ± 1.04 | 2.10 ± 0.94 | 2.33 ± 1.02 | 2.09 ± 0.92 | 2.24 ± 1.00 | **2.11 ± 0.96** |
| **Qwen2.5-3B** | 2.91 ± 0.86 | 2.66 ± 0.83 | 2.90 ± 0.87 | 2.57 ± 0.87 | 2.80 ± 0.92 | **2.70 ± 0.96** |
| **Qwen2.5-7B** | 2.72 ± 1.00 | 2.49 ± 0.88 | 2.62 ± 0.97 | 2.47 ± 0.96 | 2.55 ± 0.93 | **2.48 ± 0.99** |

---

## 4. Hypothesis Testing & Statistical Significance

To test whether human rater preferences for Qwen2.5-3B are statistically significant over competing models, one-tailed Mann-Whitney U tests were conducted on Overall Quality ratings ($N=125$ per model):

- **Qwen2.5-3B vs. Qwen2.5-7B:** $U = 8808.0$, $p = 0.0335$ (Statistically significant at p < 0.05)
- **Qwen2.5-3B vs. HingGPT:** $U = 10002.5$, $p = 2.8300e-05$ (Statistically significant at $p < 0.001$)
- **Qwen2.5-3B vs. Phi-3.5-mini:** $U = 10384.5$, $p = 1.2494e-06$ (Statistically significant at $p < 0.001$)

---

## 5. Key Empirical Conclusions

1. **Clear Preference for Qwen2.5-3B:** Qwen2.5-3B ranked #1 across all six human evaluation dimensions, achieving an overall quality mean of **2.704** compared to **2.480** for Qwen2.5-7B, **2.192** for HingGPT, and **2.112** for Phi-3.5-mini.
2. **Natural Code-Mixing Advantage:** Qwen2.5-3B demonstrated superior bilingual flow (**2.664** vs 2.488 for 7B), avoiding unnatural monolingual English collapse while maintaining Hindi matrix syntax.
3. **Phi-3.5-mini Failure Modes:** Phi-3.5-mini scored lowest across all dimensions due to frequent refusals, English-only repetitions, and poor code-mixing adherence.
4. **Methodological Single-Annotator Disclosure:** The second annotator partition was retired and archived; this study is accurately reported as an intensive 500-sample single-annotator evaluation by a domain expert.


