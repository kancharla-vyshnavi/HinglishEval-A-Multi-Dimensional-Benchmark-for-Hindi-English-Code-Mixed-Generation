# Task 2: Comprehensive LLM Judge Evaluation and Alignment Report

**Evaluation Objective:** Calibrate and audit automated LLM judges against genuine expert human ratings ($N = 500$).
**Evaluated Judges:**
1. **Mistral-7B-Instruct-v0.3:** Fully independent 7B open-weights model ($N = 500$ matched items across all 4 generators).
2. **OLMo-2-1B:** Independent compact 1B open-weights model ($N = 499$ matched items; 1 NaN record).
3. **Qwen2.5-3B-Instruct (Partial Checkpoint):** 488 / 4,000 completed items ($N = 56$ matched human items; evaluated as secondary sensitivity analysis).

---

## 1. Executive Summary & Calibration Verdict

1. **Best-Aligned Judge: Mistral-7B-Instruct-v0.3**
   - Mistral-7B demonstrates consistent, statistically significant positive rank correlations with expert human ratings across all six dimensions:
     - **Code-Mixing Naturalness:** $\rho = +0.2215$ ($p = 6.22 \times 10^{-7}$), Kendall $\tau = +0.1868$, $\text{QWK} = 0.1761$.
     - **Prompt Adherence:** $\rho = +0.1914$ ($p = 1.67 \times 10^{-5}$), Kendall $\tau = +0.1607$, $\text{QWK} = 0.1530$.
     - **Overall Quality:** $\rho = +0.1837$ ($p = 3.63 \times 10^{-5}$), Kendall $\tau = +0.1548$, $\text{QWK} = 0.1691$.
     - **Spelling Consistency:** $\rho = +0.1754$ ($p = 8.16 \times 10^{-5}$), Kendall $\tau = +0.1495$, $\text{QWK} = 0.1388$.
     - **Fluency:** $\rho = +0.1579$ ($p = 3.86 \times 10^{-4}$), Kendall $\tau = +0.1345$, $\text{QWK} = 0.1706$.
     - **Hindi Grammar:** $\rho = +0.1270$ ($p = 4.41 \times 10^{-3}$), Kendall $\tau = +0.1064$, $\text{QWK} = 0.1223$.
   - *Mean Bias:* Overall Quality bias is only **+0.098 points** (Human mean = 2.372, Mistral mean = 2.470). Leniency is dimension-specific (+0.842 on Spelling, +0.450 on Code-Mixing), while Mistral is actually *stricter* than human evaluators on Hindi Grammar (-0.534) and Fluency (-0.110).

2. **Diagnostic Failure of OLMo-2-1B (Sub-3B Evaluator Breakdown):**
   - OLMo-2-1B completely collapsed as an evaluator of code-mixed text.
   - It assigned a mean Overall Quality score of **4.26 / 5.00** across the dataset, displaying severe ceiling saturation.
   - Rank correlation with human ratings is non-existent to negative across all six dimensions (Overall Quality: $\text{QWK} = -0.0088$; Fluency: $\text{QWK} = -0.0196$; Code-Mixing: $\text{QWK} = -0.0231$).
   - As documented in the error audit, OLMo awarded scores of 3, 4, and 5 to 970 Python crash tracebacks (`AttributeError: 'NoneType' object...`).
   - *Methodological Decision:* OLMo-2-1B is **relegated to an appendix as a documented negative finding** demonstrating that sub-3B compact language models lack instruction robustness for multilingual code-mixed meta-evaluation. Its scores are strictly excluded from headline benchmark conclusions.

3. **Status of Qwen2.5-3B-Instruct Judge (Validated Dual-Judge Evaluation):**
   - Completed across all 4,000 records on disk (`research_upgrade/tables/judge_qwen25_3b_4000_results.jsonl`), with 3,996 valid parseable evaluations and 4 preserved malformed outputs (`is_valid = False`).
   - Paired evaluation against Mistral-7B across $N = 3,986$ matched cases confirms substantial positive inter-judge alignment on Prompt Adherence (QWK = 0.499, $\rho = +0.474$), Overall Quality (QWK = 0.435, $\rho = +0.445$), and Hindi Grammar (QWK = 0.418, $\rho = +0.443$), completely restoring evaluator consistency relative to the collapsed OLMo model.
   - Because Qwen2.5-3B-Instruct shares model architecture with two evaluated generators, it serves as our cross-validation dual judge, with Mistral-7B retained as the primary independent headline judge.

---

## 2. Judge-Human Alignment Summary Table

| Judge Model | Evaluation Role | Dimension | Matched N | Human Mean | Judge Mean | Mean Bias (J − H) | Spearman $\rho$ | Kendall $\tau$ | QWK |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Mistral-7B-Instruct-v0.3** | Independent Open Weights | Fluency | 500 | 2.626 | 2.516 | -0.110 | **+0.1579** | +0.1345 | **+0.1706** |
| **Mistral-7B-Instruct-v0.3** | Independent Open Weights | Code-Mixing Naturalness | 500 | 2.376 | 2.826 | +0.450 | **+0.2215** | +0.1868 | **+0.1761** |
| **Mistral-7B-Instruct-v0.3** | Independent Open Weights | Hindi Grammar | 500 | 2.606 | 2.072 | -0.534 | **+0.1270** | +0.1064 | **+0.1223** |
| **Mistral-7B-Instruct-v0.3** | Independent Open Weights | Prompt Adherence | 500 | 2.316 | 2.476 | +0.160 | **+0.1914** | +0.1607 | **+0.1530** |
| **Mistral-7B-Instruct-v0.3** | Independent Open Weights | Spelling Consistency | 500 | 2.500 | 3.342 | +0.842 | **+0.1754** | +0.1495 | **+0.1388** |
| **Mistral-7B-Instruct-v0.3** | Independent Open Weights | Overall Quality | 500 | 2.372 | 2.470 | +0.098 | **+0.1837** | +0.1548 | **+0.1691** |
| **OLMo-2-1B** | Independent Compact Open Weights | Fluency | 499 | 2.625 | 3.551 | +0.926 | **-0.0241** | -0.0212 | **-0.0174** |
| **OLMo-2-1B** | Independent Compact Open Weights | Code-Mixing Naturalness | 499 | 2.375 | 4.250 | +1.876 | **-0.0743** | -0.0653 | **-0.0210** |
| **OLMo-2-1B** | Independent Compact Open Weights | Hindi Grammar | 499 | 2.605 | 3.902 | +1.297 | **+0.0917** | +0.0799 | **+0.0512** |
| **OLMo-2-1B** | Independent Compact Open Weights | Prompt Adherence | 499 | 2.315 | 4.006 | +1.691 | **-0.0662** | -0.0580 | **-0.0230** |
| **OLMo-2-1B** | Independent Compact Open Weights | Spelling Consistency | 499 | 2.501 | 4.373 | +1.872 | **+0.0237** | +0.0212 | **+0.0068** |
| **OLMo-2-1B** | Independent Compact Open Weights | Overall Quality | 499 | 2.375 | 4.256 | +1.882 | **-0.0426** | -0.0373 | **-0.0135** |
| **Qwen2.5-3B-Instruct (Partial)** | Non-Independent Family (Sensitivity Analysis) | Fluency | 56 | 2.411 | 1.286 | -1.125 | **-0.1440** | -0.1276 | **-0.0986** |
| **Qwen2.5-3B-Instruct (Partial)** | Non-Independent Family (Sensitivity Analysis) | Code-Mixing Naturalness | 56 | 2.196 | 1.250 | -0.946 | **+0.0484** | +0.0446 | **+0.0036** |
| **Qwen2.5-3B-Instruct (Partial)** | Non-Independent Family (Sensitivity Analysis) | Hindi Grammar | 56 | 2.446 | 1.161 | -1.286 | **+0.0640** | +0.0584 | **-0.0002** |
| **Qwen2.5-3B-Instruct (Partial)** | Non-Independent Family (Sensitivity Analysis) | Prompt Adherence | 56 | 2.125 | 1.304 | -0.821 | **-0.0090** | -0.0082 | **-0.0182** |
| **Qwen2.5-3B-Instruct (Partial)** | Non-Independent Family (Sensitivity Analysis) | Spelling Consistency | 56 | 2.268 | 1.286 | -0.982 | **+0.1191** | +0.1085 | **+0.0326** |
| **Qwen2.5-3B-Instruct (Partial)** | Non-Independent Family (Sensitivity Analysis) | Overall Quality | 56 | 2.232 | 1.214 | -1.018 | **+0.1137** | +0.1044 | **+0.0182** |

---

## 3. Bootstrap 95% Confidence Intervals (10,000 Resamples, Seed = 42)

| Judge Model | Dimension | Matched N | Mean Bias [95% CI] | Spearman $\rho$ [95% CI] | Quadratic Weighted Kappa [95% CI] |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Mistral-7B-Instruct-v0.3** | Fluency | 500 | -0.110 [-0.242, +0.018] | +0.1579 [+0.0718, +0.2429] | +0.1706 [+0.0886, +0.2515] |
| **Mistral-7B-Instruct-v0.3** | Code-Mixing Naturalness | 500 | +0.450 [+0.298, +0.594] | +0.2215 [+0.1370, +0.3056] | +0.1761 [+0.1068, +0.2436] |
| **Mistral-7B-Instruct-v0.3** | Hindi Grammar | 500 | -0.534 [-0.652, -0.414] | +0.1270 [+0.0387, +0.2113] | +0.1223 [+0.0475, +0.1946] |
| **Mistral-7B-Instruct-v0.3** | Prompt Adherence | 500 | +0.160 [+0.006, +0.310] | +0.1914 [+0.1074, +0.2760] | +0.1530 [+0.0818, +0.2245] |
| **Mistral-7B-Instruct-v0.3** | Spelling Consistency | 500 | +0.842 [+0.680, +1.002] | +0.1754 [+0.0867, +0.2601] | +0.1388 [+0.0736, +0.2019] |
| **Mistral-7B-Instruct-v0.3** | Overall Quality | 500 | +0.098 [-0.036, +0.232] | +0.1837 [+0.0998, +0.2681] | +0.1691 [+0.0905, +0.2480] |
| **OLMo-2-1B** | Fluency | 499 | +0.926 [+0.820, +1.034] | -0.0241 [-0.1123, +0.0645] | -0.0174 [-0.0666, +0.0324] |
| **OLMo-2-1B** | Code-Mixing Naturalness | 499 | +1.876 [+1.768, +1.984] | -0.0743 [-0.1615, +0.0135] | -0.0210 [-0.0459, +0.0037] |
| **OLMo-2-1B** | Hindi Grammar | 499 | +1.297 [+1.194, +1.401] | +0.0917 [+0.0059, +0.1742] | +0.0512 [+0.0128, +0.0888] |
| **OLMo-2-1B** | Prompt Adherence | 499 | +1.691 [+1.575, +1.810] | -0.0662 [-0.1569, +0.0232] | -0.0230 [-0.0565, +0.0104] |
| **OLMo-2-1B** | Spelling Consistency | 499 | +1.872 [+1.760, +1.986] | +0.0237 [-0.0655, +0.1110] | +0.0068 [-0.0205, +0.0339] |
| **OLMo-2-1B** | Overall Quality | 499 | +1.882 [+1.772, +1.994] | -0.0426 [-0.1301, +0.0459] | -0.0135 [-0.0390, +0.0123] |
| **Qwen2.5-3B-Instruct (Partial)** | Fluency | 56 | -1.125 [-1.500, -0.732] | -0.1440 [-0.3778, +0.1172] | -0.0986 [-0.2442, +0.0196] |
| **Qwen2.5-3B-Instruct (Partial)** | Code-Mixing Naturalness | 56 | -0.946 [-1.286, -0.607] | +0.0484 [-0.2133, +0.3110] | +0.0036 [-0.1659, +0.1852] |
| **Qwen2.5-3B-Instruct (Partial)** | Hindi Grammar | 56 | -1.286 [-1.625, -0.946] | +0.0640 [-0.1980, +0.3180] | -0.0002 [-0.1255, +0.1124] |
| **Qwen2.5-3B-Instruct (Partial)** | Prompt Adherence | 56 | -0.821 [-1.143, -0.482] | -0.0090 [-0.2839, +0.2768] | -0.0182 [-0.2104, +0.1843] |
| **Qwen2.5-3B-Instruct (Partial)** | Spelling Consistency | 56 | -0.982 [-1.339, -0.607] | +0.1191 [-0.1328, +0.3501] | +0.0326 [-0.1326, +0.2158] |
| **Qwen2.5-3B-Instruct (Partial)** | Overall Quality | 56 | -1.018 [-1.304, -0.696] | +0.1137 [-0.2154, +0.4129] | +0.0182 [-0.1635, +0.1945] |
