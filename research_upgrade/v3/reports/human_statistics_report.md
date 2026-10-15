# Rigorous Human-Rating Statistical Analysis Report

**Study Scope:** 500 validated responses (125 responses per model across 4 models, 6 dimensions)
**Design Type:** Independent Samples (Prompt IDs do not co-occur across all 4 models; pairwise overlap is only 13–23 prompts)
**Test Statistic:** Two-Sided Mann-Whitney U Test with Holm-Bonferroni Family-Wise Error Rate Multiplicity Correction
**Effect Size Formulation:** Cliff's Delta ($\delta$) / Rank-Biserial Correlation ($r_{\text{rb}}$)
**Resampling:** 10,000 non-parametric bootstrap iterations (fixed seed = 42)

---

## 1. Executive Summary & Critical Corrections to Previous Claims

1. **Correction on Qwen2.5-3B vs. Qwen2.5-7B Significance:**
   - *Previous Unsubstantiated Claim:* Qwen2.5-3B was claimed to 'decisively lead' or possess 'statistically significant superiority' over Qwen2.5-7B based on an uncorrected, one-sided p-value ($p = 0.0335$).
   - *Verified Empirical Fact:* Under the correct, two-sided Mann-Whitney $U$ test with family-wise Holm correction ($m = 6$ comparisons per dimension), **the difference between Qwen2.5-3B and Qwen2.5-7B is NOT statistically significant across ANY of the six dimensions**.
   - Specifically for **Overall Quality**: $U = 8808.0$, raw two-sided $p = 6.7062 \times 10^{-2}$ ($p = 0.0671$), Holm-adjusted **$p_{\text{adj}} = 0.1341$** ($p > 0.05$).
   - The observed mean difference (+0.2240 points on a 1–5 scale, $2.704$ vs $2.480$) corresponds to a small rank-biserial effect size of $r_{\text{rb}} = +0.1274$ with 95% bootstrap CI $[-0.0160, +0.4720]$, which crosses zero.
   - *Correct Scientific Conclusion:* Human evaluators rated Qwen2.5-3B slightly higher descriptively, but the empirical difference does not clear the threshold of statistical significance at $N=125$. The selection of Qwen2.5-3B over Qwen2.5-7B is technically justified by its **$2.3\times$ lower VRAM footprint (2.05 GB vs 4.65 GB)** and edge-deployment efficiency, **not by statistically confirmed human preference**.

2. **Verified Significant Contrasts:**
   - **Qwen2.5-3B significantly outperforms HingGPT** on Overall Quality ($p_{\text{adj}} = 2.83 \times 10^{-4}$), Fluency ($p_{\text{adj}} = 9.11 \times 10^{-3}$), Code-Mixing Naturalness ($p_{\text{adj}} = 1.00 \times 10^{-3}$), Prompt Adherence ($p_{\text{adj}} = 6.81 \times 10^{-4}$), and Spelling Consistency ($p_{\text{adj}} = 0.0273$).
   - **Qwen2.5-3B significantly outperforms Phi-3.5-mini** across **all six dimensions** ($p_{\text{adj}} < 5.1 \times 10^{-4}$ across all dimensions).
   - **Qwen2.5-7B significantly outperforms Phi-3.5-mini** on Overall Quality ($p_{\text{adj}} = 0.0133$), Code-Mixing ($p_{\text{adj}} = 3.01 \times 10^{-3}$), Prompt Adherence ($p_{\text{adj}} = 6.43 \times 10^{-3}$), and Spelling ($p_{\text{adj}} = 0.0431$).
   - **Qwen2.5-7B vs. HingGPT** is **NOT significant** on Overall Quality after Holm correction ($p_{\text{adj}} = 0.0897$), though Qwen2.5-7B shows significantly higher Prompt Adherence ($p_{\text{adj}} = 0.0156$).
   - **HingGPT vs. Phi-3.5-mini** differences are **NOT statistically significant** across any dimension ($p_{\text{adj}} > 0.12$).

---

## 2. Descriptive Summary Statistics by Dimension (N = 125 per Model)

| Dimension | Model | Mean | Std Dev | Median | IQR | Range |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| Fluency | **Qwen2.5-3B** | 2.9120 | 0.8615 | 3.0 | 0.0 | [1, 5] |
| Fluency | **Qwen2.5-7B** | 2.7200 | 1.0048 | 3.0 | 1.0 | [1, 5] |
| Fluency | **HingGPT** | 2.4880 | 1.0596 | 3.0 | 1.0 | [1, 5] |
| Fluency | **Phi-3.5-mini** | 2.3840 | 1.0379 | 3.0 | 2.0 | [1, 4] |
| Code-Mixing Naturalness | **Qwen2.5-3B** | 2.6640 | 0.8323 | 3.0 | 1.0 | [1, 5] |
| Code-Mixing Naturalness | **Qwen2.5-7B** | 2.4880 | 0.8764 | 2.0 | 1.0 | [1, 5] |
| Code-Mixing Naturalness | **HingGPT** | 2.2480 | 0.9475 | 2.0 | 1.0 | [1, 5] |
| Code-Mixing Naturalness | **Phi-3.5-mini** | 2.1040 | 0.9403 | 2.0 | 2.0 | [1, 5] |
| Hindi Grammar | **Qwen2.5-3B** | 2.9040 | 0.8746 | 3.0 | 1.0 | [1, 5] |
| Hindi Grammar | **Qwen2.5-7B** | 2.6240 | 0.9727 | 3.0 | 1.0 | [1, 5] |
| Hindi Grammar | **HingGPT** | 2.5680 | 1.0727 | 3.0 | 1.0 | [1, 5] |
| Hindi Grammar | **Phi-3.5-mini** | 2.3280 | 1.0221 | 2.0 | 2.0 | [1, 4] |
| Prompt Adherence | **Qwen2.5-3B** | 2.5680 | 0.8738 | 2.0 | 1.0 | [1, 5] |
| Prompt Adherence | **Qwen2.5-7B** | 2.4720 | 0.9553 | 2.0 | 1.0 | [1, 5] |
| Prompt Adherence | **HingGPT** | 2.1360 | 0.8830 | 2.0 | 1.0 | [1, 5] |
| Prompt Adherence | **Phi-3.5-mini** | 2.0880 | 0.9160 | 2.0 | 2.0 | [1, 4] |
| Spelling Consistency | **Qwen2.5-3B** | 2.8000 | 0.9246 | 3.0 | 1.0 | [1, 5] |
| Spelling Consistency | **Qwen2.5-7B** | 2.5520 | 0.9285 | 3.0 | 1.0 | [1, 5] |
| Spelling Consistency | **HingGPT** | 2.4080 | 1.0633 | 3.0 | 2.0 | [1, 4] |
| Spelling Consistency | **Phi-3.5-mini** | 2.2400 | 0.9951 | 2.0 | 2.0 | [1, 5] |
| Overall Quality | **Qwen2.5-3B** | 2.7040 | 0.9590 | 3.0 | 1.0 | [1, 5] |
| Overall Quality | **Qwen2.5-7B** | 2.4800 | 0.9886 | 2.0 | 1.0 | [1, 5] |
| Overall Quality | **HingGPT** | 2.1920 | 0.9043 | 2.0 | 1.0 | [1, 4] |
| Overall Quality | **Phi-3.5-mini** | 2.1120 | 0.9606 | 2.0 | 2.0 | [1, 5] |

---

## 3. Two-Sided Pairwise Mann-Whitney U Tests & Holm Multiplicity Correction

| Dimension | Comparison | Mean Diff | Mann-Whitney U | Raw p-value | Holm-Adjusted p | Significance ($\alpha=0.05$) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| Fluency | Qwen2.5-3B vs Qwen2.5-7B | +0.1920 | 8594.0 | `1.4475e-01` | `2.9808e-01` | Not Significant |
| Fluency | Qwen2.5-3B vs HingGPT | +0.4240 | 9487.0 | `1.8223e-03` | `9.1117e-03` | **SIGNIFICANT** |
| Fluency | Qwen2.5-3B vs Phi-3.5-mini | +0.5280 | 9924.0 | `8.4083e-05` | `5.0450e-04` | **SIGNIFICANT** |
| Fluency | Qwen2.5-7B vs HingGPT | +0.2320 | 8714.0 | `9.9361e-02` | `2.9808e-01` | Not Significant |
| Fluency | Qwen2.5-7B vs Phi-3.5-mini | +0.3360 | 9132.0 | `1.5795e-02` | `6.3179e-02` | Not Significant |
| Fluency | HingGPT vs Phi-3.5-mini | +0.1040 | 8217.0 | `4.5907e-01` | `4.5907e-01` | Not Significant |
| Code-Mixing Naturalness | Qwen2.5-3B vs Qwen2.5-7B | +0.1760 | 8692.0 | `1.0097e-01` | `2.0194e-01` | Not Significant |
| Code-Mixing Naturalness | Qwen2.5-3B vs HingGPT | +0.4160 | 9826.0 | `2.0097e-04` | `1.0049e-03` | **SIGNIFICANT** |
| Code-Mixing Naturalness | Qwen2.5-3B vs Phi-3.5-mini | +0.5600 | 10442.5 | `1.3298e-06` | `7.9787e-06` | **SIGNIFICANT** |
| Code-Mixing Naturalness | Qwen2.5-7B vs HingGPT | +0.2400 | 8998.5 | `2.8460e-02` | `8.5379e-02` | Not Significant |
| Code-Mixing Naturalness | Qwen2.5-7B vs Phi-3.5-mini | +0.3840 | 9643.0 | `7.5244e-04` | `3.0098e-03` | **SIGNIFICANT** |
| Code-Mixing Naturalness | HingGPT vs Phi-3.5-mini | +0.1440 | 8469.0 | `2.2785e-01` | `2.2785e-01` | Not Significant |
| Hindi Grammar | Qwen2.5-3B vs Qwen2.5-7B | +0.2800 | 9076.0 | `1.7920e-02` | `8.9599e-02` | Not Significant |
| Hindi Grammar | Qwen2.5-3B vs HingGPT | +0.3360 | 9042.5 | `2.1453e-02` | `8.9599e-02` | Not Significant |
| Hindi Grammar | Qwen2.5-3B vs Phi-3.5-mini | +0.5760 | 10196.5 | `1.0118e-05` | `6.0711e-05` | **SIGNIFICANT** |
| Hindi Grammar | Qwen2.5-7B vs HingGPT | +0.0560 | 7896.0 | `8.7797e-01` | `8.7797e-01` | Not Significant |
| Hindi Grammar | Qwen2.5-7B vs Phi-3.5-mini | +0.2960 | 9004.5 | `2.8489e-02` | `8.9599e-02` | Not Significant |
| Hindi Grammar | HingGPT vs Phi-3.5-mini | +0.2400 | 8817.5 | `6.4674e-02` | `1.2935e-01` | Not Significant |
| Prompt Adherence | Qwen2.5-3B vs Qwen2.5-7B | +0.0960 | 8312.5 | `3.5486e-01` | `7.0972e-01` | Not Significant |
| Prompt Adherence | Qwen2.5-3B vs HingGPT | +0.4320 | 9870.5 | `1.3613e-04` | `6.8067e-04` | **SIGNIFICANT** |
| Prompt Adherence | Qwen2.5-3B vs Phi-3.5-mini | +0.4800 | 10055.5 | `3.5778e-05` | `2.1467e-04` | **SIGNIFICANT** |
| Prompt Adherence | Qwen2.5-7B vs HingGPT | +0.3360 | 9324.5 | `5.1916e-03` | `1.5575e-02` | **SIGNIFICANT** |
| Prompt Adherence | Qwen2.5-7B vs Phi-3.5-mini | +0.3840 | 9528.0 | `1.6074e-03` | `6.4297e-03` | **SIGNIFICANT** |
| Prompt Adherence | HingGPT vs Phi-3.5-mini | +0.0480 | 8079.5 | `6.2167e-01` | `7.0972e-01` | Not Significant |
| Spelling Consistency | Qwen2.5-3B vs Qwen2.5-7B | +0.2480 | 8991.0 | `2.8236e-02` | `8.4708e-02` | Not Significant |
| Spelling Consistency | Qwen2.5-3B vs HingGPT | +0.3920 | 9320.0 | `5.4505e-03` | `2.7252e-02` | **SIGNIFICANT** |
| Spelling Consistency | Qwen2.5-3B vs Phi-3.5-mini | +0.5600 | 10242.5 | `8.3672e-06` | `5.0203e-05` | **SIGNIFICANT** |
| Spelling Consistency | Qwen2.5-7B vs HingGPT | +0.1440 | 8285.0 | `3.8465e-01` | `3.8465e-01` | Not Significant |
| Spelling Consistency | Qwen2.5-7B vs Phi-3.5-mini | +0.3120 | 9201.5 | `1.0771e-02` | `4.3084e-02` | **SIGNIFICANT** |
| Spelling Consistency | HingGPT vs Phi-3.5-mini | +0.1680 | 8566.0 | `1.6872e-01` | `3.3745e-01` | Not Significant |
| Overall Quality | Qwen2.5-3B vs Qwen2.5-7B | +0.2240 | 8808.0 | `6.7062e-02` | `1.3412e-01` | Not Significant |
| Overall Quality | Qwen2.5-3B vs HingGPT | +0.5120 | 10002.5 | `5.6601e-05` | `2.8300e-04` | **SIGNIFICANT** |
| Overall Quality | Qwen2.5-3B vs Phi-3.5-mini | +0.5920 | 10384.5 | `2.4988e-06` | `1.4993e-05` | **SIGNIFICANT** |
| Overall Quality | Qwen2.5-7B vs HingGPT | +0.2880 | 8994.5 | `2.9888e-02` | `8.9664e-02` | Not Significant |
| Overall Quality | Qwen2.5-7B vs Phi-3.5-mini | +0.3680 | 9414.5 | `3.3337e-03` | `1.3335e-02` | **SIGNIFICANT** |
| Overall Quality | HingGPT vs Phi-3.5-mini | +0.0800 | 8275.0 | `3.9563e-01` | `3.9563e-01` | Not Significant |

---

## 4. Effect Sizes (Rank-Biserial Correlation / Cliff's Delta) & Bootstrap 95% CIs

| Dimension | Comparison | Mean Diff [95% CI] | Cliff's $\delta$ / $r_{\text{rb}}$ [95% CI] | Magnitude |
| :--- | :--- | :---: | :---: | :--- |
| Fluency | Qwen2.5-3B vs Qwen2.5-7B | +0.1920 [-0.0400, +0.4240] | +0.1000 [-0.0351, +0.2319] | Negligible |
| Fluency | Qwen2.5-3B vs HingGPT | +0.4240 [+0.1840, +0.6640] | +0.2143 [+0.0811, +0.3442] | Small |
| Fluency | Qwen2.5-3B vs Phi-3.5-mini | +0.5280 [+0.2958, +0.7600] | +0.2703 [+0.1405, +0.3958] | Small |
| Fluency | Qwen2.5-7B vs HingGPT | +0.2320 [-0.0240, +0.4880] | +0.1154 [-0.0218, +0.2511] | Negligible |
| Fluency | Qwen2.5-7B vs Phi-3.5-mini | +0.3360 [+0.0880, +0.5920] | +0.1689 [+0.0346, +0.3025] | Small |
| Fluency | HingGPT vs Phi-3.5-mini | +0.1040 [-0.1520, +0.3680] | +0.0518 [-0.0832, +0.1903] | Negligible |
| Code-Mixing Naturalness | Qwen2.5-3B vs Qwen2.5-7B | +0.1760 [-0.0400, +0.3840] | +0.1126 [-0.0239, +0.2460] | Negligible |
| Code-Mixing Naturalness | Qwen2.5-3B vs HingGPT | +0.4160 [+0.1920, +0.6320] | +0.2577 [+0.1232, +0.3846] | Small |
| Code-Mixing Naturalness | Qwen2.5-3B vs Phi-3.5-mini | +0.5600 [+0.3360, +0.7760] | +0.3366 [+0.2065, +0.4609] | Medium |
| Code-Mixing Naturalness | Qwen2.5-7B vs HingGPT | +0.2400 [+0.0160, +0.4640] | +0.1518 [+0.0188, +0.2838] | Small |
| Code-Mixing Naturalness | Qwen2.5-7B vs Phi-3.5-mini | +0.3840 [+0.1600, +0.6080] | +0.2343 [+0.1002, +0.3670] | Small |
| Code-Mixing Naturalness | HingGPT vs Phi-3.5-mini | +0.1440 [-0.0880, +0.3760] | +0.0840 [-0.0517, +0.2166] | Negligible |
| Hindi Grammar | Qwen2.5-3B vs Qwen2.5-7B | +0.2800 [+0.0560, +0.5040] | +0.1617 [+0.0296, +0.2905] | Small |
| Hindi Grammar | Qwen2.5-3B vs HingGPT | +0.3360 [+0.0960, +0.5760] | +0.1574 [+0.0239, +0.2865] | Small |
| Hindi Grammar | Qwen2.5-3B vs Phi-3.5-mini | +0.5760 [+0.3440, +0.8080] | +0.3052 [+0.1782, +0.4293] | Small |
| Hindi Grammar | Qwen2.5-7B vs HingGPT | +0.0560 [-0.1920, +0.3120] | +0.0107 [-0.1213, +0.1469] | Negligible |
| Hindi Grammar | Qwen2.5-7B vs Phi-3.5-mini | +0.2960 [+0.0560, +0.5440] | +0.1526 [+0.0194, +0.2872] | Small |
| Hindi Grammar | HingGPT vs Phi-3.5-mini | +0.2400 [-0.0160, +0.5040] | +0.1286 [-0.0047, +0.2659] | Negligible |
| Prompt Adherence | Qwen2.5-3B vs Qwen2.5-7B | +0.0960 [-0.1360, +0.3200] | +0.0640 [-0.0722, +0.2003] | Negligible |
| Prompt Adherence | Qwen2.5-3B vs HingGPT | +0.4320 [+0.2160, +0.6480] | +0.2634 [+0.1341, +0.3882] | Small |
| Prompt Adherence | Qwen2.5-3B vs Phi-3.5-mini | +0.4800 [+0.2560, +0.7040] | +0.2871 [+0.1575, +0.4132] | Small |
| Prompt Adherence | Qwen2.5-7B vs HingGPT | +0.3360 [+0.1120, +0.5600] | +0.1935 [+0.0636, +0.3234] | Small |
| Prompt Adherence | Qwen2.5-7B vs Phi-3.5-mini | +0.3840 [+0.1520, +0.6160] | +0.2196 [+0.0869, +0.3523] | Small |
| Prompt Adherence | HingGPT vs Phi-3.5-mini | +0.0480 [-0.1760, +0.2720] | +0.0342 [-0.0986, +0.1711] | Negligible |
| Spelling Consistency | Qwen2.5-3B vs Qwen2.5-7B | +0.2480 [+0.0160, +0.4800] | +0.1508 [+0.0169, +0.2840] | Small |
| Spelling Consistency | Qwen2.5-3B vs HingGPT | +0.3920 [+0.1520, +0.6320] | +0.1930 [+0.0605, +0.3247] | Small |
| Spelling Consistency | Qwen2.5-3B vs Phi-3.5-mini | +0.5600 [+0.3200, +0.8000] | +0.3110 [+0.1825, +0.4390] | Small |
| Spelling Consistency | Qwen2.5-7B vs HingGPT | +0.1440 [-0.1040, +0.3920] | +0.0605 [-0.0776, +0.1957] | Negligible |
| Spelling Consistency | Qwen2.5-7B vs Phi-3.5-mini | +0.3120 [+0.0800, +0.5520] | +0.1778 [+0.0461, +0.3135] | Small |
| Spelling Consistency | HingGPT vs Phi-3.5-mini | +0.1680 [-0.0800, +0.4320] | +0.0964 [-0.0370, +0.2367] | Negligible |
| Overall Quality | Qwen2.5-3B vs Qwen2.5-7B | +0.2240 [-0.0160, +0.4640] | +0.1274 [-0.0113, +0.2595] | Negligible |
| Overall Quality | Qwen2.5-3B vs HingGPT | +0.5120 [+0.2800, +0.7440] | +0.2803 [+0.1464, +0.4066] | Small |
| Overall Quality | Qwen2.5-3B vs Phi-3.5-mini | +0.5920 [+0.3520, +0.8320] | +0.3292 [+0.1997, +0.4540] | Small |
| Overall Quality | Qwen2.5-7B vs HingGPT | +0.2880 [+0.0560, +0.5200] | +0.1513 [+0.0189, +0.2840] | Small |
| Overall Quality | Qwen2.5-7B vs Phi-3.5-mini | +0.3680 [+0.1280, +0.6080] | +0.2051 [+0.0738, +0.3349] | Small |
| Overall Quality | HingGPT vs Phi-3.5-mini | +0.0800 [-0.1520, +0.3120] | +0.0592 [-0.0760, +0.1951] | Negligible |

---

## 5. Statistical Power Analysis

| Target Power | Sample Size ($n_1 = n_2$) | Nominal $\alpha$ | Detectable Cohen's $d$ (Uncorrected) | Holm $\alpha$ ($0.05/6$) | Detectable Cohen's $d$ (Holm) | Empirical Interpretation |
| :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| 70% | 125 | 0.05 | 0.3143 | 0.00833 | 0.4 | Adequate for Medium-to-Large effects (d >= 0.42); Underpowered for Small effects (d < 0.30) |
| 80% | 125 | 0.05 | 0.3544 | 0.00833 | 0.4402 | Adequate for Medium-to-Large effects (d >= 0.42); Underpowered for Small effects (d < 0.30) |
| 90% | 125 | 0.05 | 0.41 | 0.00833 | 0.4958 | Adequate for Medium-to-Large effects (d >= 0.42); Underpowered for Small effects (d < 0.30) |
| 95% | 125 | 0.05 | 0.456 | 0.00833 | 0.5418 | Adequate for Medium-to-Large effects (d >= 0.42); Underpowered for Small effects (d < 0.30) |

### Power Analysis Takeaways:
1. At $n_1 = n_2 = 125$, the study achieved $\ge 80\%$ statistical power to detect **medium-to-large effects** ($d \ge 0.417$, corresponding to a mean difference of $\ge 0.40$ points on a 5-point scale).
2. The study was **underpowered ($< 45\%$ power)** to detect subtle differences ($d \le 0.23$) between Qwen2.5-3B and Qwen2.5-7B (where observed $d \approx 0.23$, mean difference $= +0.2240$).
3. **Crucial Scientific Caveat:** A non-significant result between Qwen2.5-3B and Qwen2.5-7B ($p_{\text{adj}} = 0.1341$) **does NOT prove statistical equivalence**. It demonstrates that any latent human preference difference between the two architectures is small ($|r_{\text{rb}}| \le 0.13$) and cannot be distinguished from sampling variability at $N = 125$.
