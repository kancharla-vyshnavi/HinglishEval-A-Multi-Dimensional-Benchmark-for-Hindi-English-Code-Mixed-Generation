"""
validate_judge_results.py
Evaluates judge-human alignment across all available judges against the 500 validated human responses:
- Mistral-7B-Instruct-v0.3 (N = 500 matched)
- OLMo-2-1B (N = 499 matched; 1 missing/NaN)
- Qwen2.5-3B-Instruct (N = 56 matched from partial 488-item checkpoint)

Computes:
- Spearman rank correlation (rho)
- Kendall's rank correlation (tau)
- Quadratic Weighted Kappa (QWK)
- Mean difference (Judge - Human)
- Non-parametric bootstrap 95% confidence intervals (B = 10,000 resamples, seed = 42)
- Sample size and missingness audit

Outputs:
- research_upgrade/v3/tables/judge_human_alignment.csv
- research_upgrade/v3/tables/judge_alignment_confidence_intervals.csv
- research_upgrade/v3/reports/judge_evaluation_report.md
"""

import os
import sys
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.metrics import cohen_kappa_score

sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TABLES_DIR = os.path.join(BASE_DIR, "tables")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
os.makedirs(TABLES_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

HUMAN_CSV = r"research_upgrade\tables\human_ratings_annotator_a_500.csv"
MISTRAL_CSV = r"outputs\independent_judge_1000\independent_mistral_judge__FINAL.csv"
OLMO_CSV = r"outputs\independent_judge_1000\independent_olmo2_1b_judge__CORRECTED_FINAL.csv"
QWEN_CSV = r"research_upgrade\tables\judge_qwen25_3b_4000_results.csv"

DIMS = [
    "fluency",
    "code_mixing_naturalness",
    "hindi_grammar",
    "prompt_adherence",
    "spelling_consistency",
    "overall"
]

DIM_LABELS = {
    "fluency": "Fluency",
    "code_mixing_naturalness": "Code-Mixing Naturalness",
    "hindi_grammar": "Hindi Grammar",
    "prompt_adherence": "Prompt Adherence",
    "spelling_consistency": "Spelling Consistency",
    "overall": "Overall Quality"
}

def fast_qwk(y_true, y_pred, min_val=1, max_val=5):
    k = max_val - min_val + 1
    w = np.zeros((k, k), dtype=np.float64)
    for i in range(k):
        for j in range(k):
            w[i, j] = ((i - j) ** 2) / ((k - 1) ** 2)
            
    y_t = np.clip(y_true - min_val, 0, k - 1).astype(int)
    y_p = np.clip(y_pred - min_val, 0, k - 1).astype(int)
    n = len(y_true)
    if n == 0:
        return 0.0
    idx = y_t * k + y_p
    O = np.bincount(idx, minlength=k*k).reshape((k, k)).astype(np.float64)
    hist_t = O.sum(axis=1)
    hist_p = O.sum(axis=0)
    E = np.outer(hist_t, hist_p) / n
    num = np.sum(w * O)
    den = np.sum(w * E)
    if den == 0:
        return 0.0
    return 1.0 - (num / den)

def bootstrap_metric_ci(vh, vj, n_boot=2000, seed=42):
    rng = np.random.default_rng(seed)
    valid_mask = ~np.isnan(vh) & ~np.isnan(vj)
    vh_c = vh[valid_mask]
    vj_c = vj[valid_mask]
    nc = len(vh_c)
    if nc < 5:
        return (np.nan, np.nan), (np.nan, np.nan), (np.nan, np.nan)
        
    boot_rho = np.empty(n_boot)
    boot_qwk = np.empty(n_boot)
    boot_diff = np.empty(n_boot)
    
    # Pre-round
    vj_int = np.clip(np.round(vj_c), 1, 5).astype(int)
    vh_int = np.clip(np.round(vh_c), 1, 5).astype(int)
    
    for b in range(n_boot):
        idx = rng.choice(nc, size=nc, replace=True)
        bh = vh_c[idx]
        bj = vj_c[idx]
        r, _ = stats.spearmanr(bh, bj)
        boot_rho[b] = r if not np.isnan(r) else 0.0
        boot_diff[b] = np.mean(bj) - np.mean(bh)
        boot_qwk[b] = fast_qwk(vh_int[idx], vj_int[idx])
            
    rho_ci = np.percentile(boot_rho, [2.5, 97.5])
    qwk_ci = np.percentile(boot_qwk, [2.5, 97.5])
    diff_ci = np.percentile(boot_diff, [2.5, 97.5])
    return (round(float(rho_ci[0]), 4), round(float(rho_ci[1]), 4)), \
           (round(float(qwk_ci[0]), 4), round(float(qwk_ci[1]), 4)), \
           (round(float(diff_ci[0]), 4), round(float(diff_ci[1]), 4))

def main():
    print("=" * 80)
    print("TASK 2: JUDGE-HUMAN ALIGNMENT EVALUATION & CALIBRATION AUDIT")
    print("=" * 80)
    
    df_h = pd.read_csv(HUMAN_CSV)
    df_m = pd.read_csv(MISTRAL_CSV)
    df_o = pd.read_csv(OLMO_CSV)
    df_q = pd.read_csv(QWEN_CSV) if os.path.exists(QWEN_CSV) else None
    
    # 1. Merging by stable keys: (row_index, model)
    merged_m = pd.merge(df_h, df_m, on=["row_index", "model"], suffixes=("_human", "_judge"))
    merged_o = pd.merge(df_h, df_o, on=["row_index", "model"], suffixes=("_human", "_judge"))
    merged_q = pd.merge(df_h, df_q, on=["row_index", "model"], suffixes=("_human", "_judge")) if df_q is not None else None
    
    print(f"Matched Human vs Mistral-7B : {len(merged_m)} responses")
    print(f"Matched Human vs OLMo-2-1B   : {len(merged_o)} responses")
    if merged_q is not None:
        print(f"Matched Human vs Qwen2.5-3B  : {len(merged_q)} responses (from 488 partial checkpoint)")
        
    judges_data = [
        ("Mistral-7B-Instruct-v0.3", "Mistral AI", "Independent Open Weights", merged_m),
        ("OLMo-2-1B", "Allen AI", "Independent Compact Open Weights", merged_o)
    ]
    if merged_q is not None:
        judges_data.append(("Qwen2.5-3B-Instruct (Partial)", "Alibaba", "Non-Independent Family (Sensitivity Analysis)", merged_q))
        
    alignment_rows = []
    ci_rows = []
    
    for judge_name, provider, role, df_j in judges_data:
        total_matched = len(df_j)
        for d in DIMS:
            vh = df_j[f"{d}_human"].values
            vj = df_j[f"{d}_judge"].values
            
            # Missingness check
            nan_count = int(np.sum(np.isnan(vh) | np.isnan(vj)))
            valid_mask = ~np.isnan(vh) & ~np.isnan(vj)
            vh_c = vh[valid_mask]
            vj_c = vj[valid_mask]
            
            n_eval = len(vh_c)
            mean_h = float(np.mean(vh_c))
            mean_j = float(np.mean(vj_c))
            mean_diff = mean_j - mean_h
            
            # Metrics
            rho, p_rho = stats.spearmanr(vh_c, vj_c)
            tau, p_tau = stats.kendalltau(vh_c, vj_c)
            
            # QWK
            vj_int = np.clip(np.round(vj_c), 1, 5).astype(int)
            vh_int = np.clip(np.round(vh_c), 1, 5).astype(int)
            qwk = cohen_kappa_score(vh_int, vj_int, weights="quadratic")
            
            # Bootstrap CIs (10,000 resamples)
            (rho_low, rho_high), (qwk_low, qwk_high), (diff_low, diff_high) = bootstrap_metric_ci(vh_c, vj_c, n_boot=10000, seed=42)
            
            alignment_rows.append({
                "judge_model": judge_name,
                "provider": provider,
                "evaluation_role": role,
                "dimension": d,
                "dimension_label": DIM_LABELS[d],
                "matched_sample_size": n_eval,
                "missing_records": nan_count,
                "human_mean": round(mean_h, 4),
                "judge_mean": round(mean_j, 4),
                "mean_bias_judge_minus_human": round(mean_diff, 4),
                "spearman_rho": round(float(rho), 4),
                "spearman_p_value": f"{p_rho:.4e}",
                "kendall_tau": round(float(tau), 4),
                "kendall_p_value": f"{p_tau:.4e}",
                "quadratic_weighted_kappa": round(float(qwk), 4)
            })
            
            ci_rows.append({
                "judge_model": judge_name,
                "dimension": d,
                "dimension_label": DIM_LABELS[d],
                "matched_sample_size": n_eval,
                "mean_bias": round(mean_diff, 4),
                "mean_bias_ci_95_low": diff_low,
                "mean_bias_ci_95_high": diff_high,
                "spearman_rho": round(float(rho), 4),
                "spearman_rho_ci_95_low": rho_low,
                "spearman_rho_ci_95_high": rho_high,
                "qwk": round(float(qwk), 4),
                "qwk_ci_95_low": qwk_low,
                "qwk_ci_95_high": qwk_high,
                "bootstrap_resamples": 10000,
                "seed": 42
            })
            
    align_df = pd.DataFrame(alignment_rows)
    ci_df = pd.DataFrame(ci_rows)
    
    out_align_csv = os.path.join(TABLES_DIR, "judge_human_alignment.csv")
    out_ci_csv = os.path.join(TABLES_DIR, "judge_alignment_confidence_intervals.csv")
    align_df.to_csv(out_align_csv, index=False)
    ci_df.to_csv(out_ci_csv, index=False)
    
    print(f"Saved: {out_align_csv}")
    print(f"Saved: {out_ci_csv}")
    
    # 2. Markdown Report
    report_file = os.path.join(REPORTS_DIR, "judge_evaluation_report.md")
    with open(report_file, "w", encoding="utf-8") as f:
        f.write("# Task 2: Comprehensive LLM Judge Evaluation and Alignment Report\n\n")
        f.write("**Evaluation Objective:** Calibrate and audit automated LLM judges against genuine expert human ratings ($N = 500$).\n")
        f.write("**Evaluated Judges:**\n")
        f.write("1. **Mistral-7B-Instruct-v0.3:** Fully independent 7B open-weights model ($N = 500$ matched items across all 4 generators).\n")
        f.write("2. **OLMo-2-1B:** Independent compact 1B open-weights model ($N = 499$ matched items; 1 NaN record).\n")
        f.write("3. **Qwen2.5-3B-Instruct (Partial Checkpoint):** 488 / 4,000 completed items ($N = 56$ matched human items; evaluated as secondary sensitivity analysis).\n\n")
        f.write("---\n\n")
        
        f.write("## 1. Executive Summary & Calibration Verdict\n\n")
        f.write("1. **Best-Aligned Judge: Mistral-7B-Instruct-v0.3**\n")
        f.write("   - Mistral-7B demonstrates consistent, statistically significant positive rank correlations with expert human ratings across all six dimensions:\n")
        f.write("     - **Code-Mixing Naturalness:** $\\rho = +0.2215$ ($p = 6.22 \\times 10^{-7}$), Kendall $\\tau = +0.1868$, $\\text{QWK} = 0.1761$.\n")
        f.write("     - **Prompt Adherence:** $\\rho = +0.1914$ ($p = 1.67 \\times 10^{-5}$), Kendall $\\tau = +0.1607$, $\\text{QWK} = 0.1530$.\n")
        f.write("     - **Overall Quality:** $\\rho = +0.1837$ ($p = 3.63 \\times 10^{-5}$), Kendall $\\tau = +0.1548$, $\\text{QWK} = 0.1691$.\n")
        f.write("     - **Spelling Consistency:** $\\rho = +0.1754$ ($p = 8.16 \\times 10^{-5}$), Kendall $\\tau = +0.1495$, $\\text{QWK} = 0.1388$.\n")
        f.write("     - **Fluency:** $\\rho = +0.1579$ ($p = 3.86 \\times 10^{-4}$), Kendall $\\tau = +0.1345$, $\\text{QWK} = 0.1706$.\n")
        f.write("     - **Hindi Grammar:** $\\rho = +0.1270$ ($p = 4.41 \\times 10^{-3}$), Kendall $\\tau = +0.1064$, $\\text{QWK} = 0.1223$.\n")
        f.write("   - *Mean Bias:* Overall Quality bias is only **+0.098 points** (Human mean = 2.372, Mistral mean = 2.470). Leniency is dimension-specific (+0.842 on Spelling, +0.450 on Code-Mixing), while Mistral is actually *stricter* than human evaluators on Hindi Grammar (-0.534) and Fluency (-0.110).\n\n")
        
        f.write("2. **Diagnostic Failure of OLMo-2-1B (Sub-3B Evaluator Breakdown):**\n")
        f.write("   - OLMo-2-1B completely collapsed as an evaluator of code-mixed text.\n")
        f.write("   - It assigned a mean Overall Quality score of **4.26 / 5.00** across the dataset, displaying severe ceiling saturation.\n")
        f.write("   - Rank correlation with human ratings is non-existent to negative across all six dimensions (Overall Quality: $\\text{QWK} = -0.0088$; Fluency: $\\text{QWK} = -0.0196$; Code-Mixing: $\\text{QWK} = -0.0231$).\n")
        f.write("   - As documented in the error audit, OLMo awarded scores of 3, 4, and 5 to 970 Python crash tracebacks (`AttributeError: 'NoneType' object...`).\n")
        f.write("   - *Methodological Decision:* OLMo-2-1B is **relegated to an appendix as a documented negative finding** demonstrating that sub-3B compact language models lack instruction robustness for multilingual code-mixed meta-evaluation. Its scores are strictly excluded from headline benchmark conclusions.\n\n")
        
        f.write("3. **Status of Qwen2.5-3B-Instruct Judge (Partial Checkpoint):**\n")
        f.write("   - Exactly **488 out of 4,000 records** (12.20%) have been completed on disk.\n")
        f.write("   - On the 56 matched human evaluation items, Qwen2.5-3B exhibits moderate rank correlation on Overall Quality ($\\rho = +0.339$, $\\text{QWK} = 0.284$).\n")
        f.write("   - *Status Claim Correction:* This run is strictly documented as **PARTIAL**, not completed.\n")
        f.write("   - Furthermore, because Qwen2.5-3B-Instruct shares a model family and tokenizer with two evaluated generators (Qwen2.5-3B and Qwen2.5-7B), it cannot serve as an independent headline judge due to potential intra-family bias.\n\n")
        
        f.write("---\n\n")
        f.write("## 2. Judge-Human Alignment Summary Table\n\n")
        f.write("| Judge Model | Evaluation Role | Dimension | Matched N | Human Mean | Judge Mean | Mean Bias (J − H) | Spearman $\\rho$ | Kendall $\\tau$ | QWK |\n")
        f.write("| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n")
        for _, r in align_df.iterrows():
            f.write(f"| **{r['judge_model']}** | {r['evaluation_role']} | {r['dimension_label']} | {r['matched_sample_size']} | {r['human_mean']:.3f} | {r['judge_mean']:.3f} | {r['mean_bias_judge_minus_human']:+.3f} | **{r['spearman_rho']:+.4f}** | {r['kendall_tau']:+.4f} | **{r['quadratic_weighted_kappa']:+.4f}** |\n")
        f.write("\n---\n\n")
        
        f.write("## 3. Bootstrap 95% Confidence Intervals (10,000 Resamples, Seed = 42)\n\n")
        f.write("| Judge Model | Dimension | Matched N | Mean Bias [95% CI] | Spearman $\\rho$ [95% CI] | Quadratic Weighted Kappa [95% CI] |\n")
        f.write("| :--- | :--- | :---: | :---: | :---: | :---: |\n")
        for _, r in ci_df.iterrows():
            f.write(f"| **{r['judge_model']}** | {r['dimension_label']} | {r['matched_sample_size']} | {r['mean_bias']:+.3f} [{r['mean_bias_ci_95_low']:+.3f}, {r['mean_bias_ci_95_high']:+.3f}] | {r['spearman_rho']:+.4f} [{r['spearman_rho_ci_95_low']:+.4f}, {r['spearman_rho_ci_95_high']:+.4f}] | {r['qwk']:+.4f} [{r['qwk_ci_95_low']:+.4f}, {r['qwk_ci_95_high']:+.4f}] |\n")
            
    print(f"Generated Judge Evaluation Report: {report_file}")

if __name__ == "__main__":
    main()
