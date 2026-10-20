"""
Generate 4K Human Evaluation Tables for HinglishEval
Dual-Annotator Complete Evaluation (Annotator A: 4,000 responses, Annotator B: 4,000 responses)
Total Ratings: 8,000 (4,000 matched response pairs across 4 models, 1,000 prompts each).
Computes:
1. Canonical 4K Human Evaluation Summary Table (Mean, Std, Median, 95% Bootstrap CI per model and dimension).
2. Inter-Annotator Agreement Table (Exact %, +-1 %, QWK [95% CI], Krippendorff's Alpha [95% CI], Spearman rho).
3. Pairwise Statistical Significance Table (Wilcoxon Signed-Rank tests with Holm-Bonferroni correction).
4. Exports all CSV tables to research_upgrade/tables/ and Tables csv/.
"""

import os
import sys
import sqlite3
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.metrics import cohen_kappa_score

sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DB_PATH = REPO_ROOT / "human_validation_app" / "ratings_4000.db"
OUTPUT_TABLES_DIR = REPO_ROOT / "research_upgrade" / "tables"
TABLES_CSV_DIR = REPO_ROOT / "Tables csv"
OUTPUT_TABLES_DIR.mkdir(parents=True, exist_ok=True)
TABLES_CSV_DIR.mkdir(parents=True, exist_ok=True)

DIMENSIONS = [
    ("fluency", "Fluency"),
    ("code_mixing_naturalness", "Code-Mixing Naturalness"),
    ("hindi_grammar", "Hindi Grammar"),
    ("prompt_adherence", "Prompt Adherence"),
    ("spelling_consistency", "Spelling Consistency"),
    ("overall", "Overall Quality")
]

DIM_KEYS = [d[0] for d in DIMENSIONS]

def krippendorff_alpha_ordinal(y1: np.ndarray, y2: np.ndarray) -> float:
    if len(y1) != len(y2) or len(y1) == 0:
        return float("nan")
    if np.array_equal(y1, y2):
        return 1.0

    all_values = np.concatenate([y1, y2])
    categories = np.arange(1, 6)
    n_total = len(all_values)
    counts = {c: np.sum(all_values == c) for c in categories}

    delta = np.zeros((6, 6))
    for c in range(1, 6):
        for k in range(c, 6):
            if c == k:
                d = 0.0
            else:
                intermediate = sum(counts[g] for g in range(c, k + 1))
                d = intermediate - (counts[c] + counts[k]) / 2.0
            delta[c, k] = d ** 2
            delta[k, c] = d ** 2

    d_observed = np.sum([delta[int(a), int(b)] for a, b in zip(y1, y2)]) / len(y1)
    d_expected = 0.0
    for c in range(1, 6):
        for k in range(1, 6):
            d_expected += counts[c] * counts[k] * delta[c, k]
    d_expected /= (n_total * (n_total - 1))

    if d_expected == 0:
        return 1.0 if d_observed == 0 else 0.0
    return float(1.0 - (d_observed / d_expected))

def bootstrap_ci(arr, stat_fn=np.mean, n_boot=200, ci=0.95):
    rng = np.random.default_rng(42)
    n = len(arr)
    boot_stats = []
    for _ in range(n_boot):
        sample = rng.choice(arr, size=n, replace=True)
        boot_stats.append(stat_fn(sample))
    lower = np.percentile(boot_stats, (1 - ci) / 2 * 100)
    upper = np.percentile(boot_stats, (1 + ci) / 2 * 100)
    return lower, upper

def bootstrap_agreement_ci(y1, y2, metric_fn, n_boot=100, ci=0.95):
    rng = np.random.default_rng(42)
    n = len(y1)
    scores = []
    for _ in range(n_boot):
        idx = rng.choice(n, size=n, replace=True)
        val = metric_fn(y1[idx], y2[idx])
        if not np.isnan(val):
            scores.append(val)
    if len(scores) < 10:
        return float("nan"), float("nan")
    lower = np.percentile(scores, (1 - ci) / 2 * 100)
    upper = np.percentile(scores, (1 + ci) / 2 * 100)
    return lower, upper

def main():
    print(f"Loading SQLite ratings from: {DB_PATH}")
    con = sqlite3.connect(DB_PATH)
    
    # Query complete joined ratings
    query = """
    SELECT 
        r.id as response_id,
        r.item_index,
        r.model,
        r.prompt_id,
        r.prompt,
        r.response,
        a.annotator_id,
        a.fluency,
        a.code_mixing_naturalness,
        a.hindi_grammar,
        a.prompt_adherence,
        a.spelling_consistency,
        a.overall,
        a.notes,
        a.is_completed
    FROM responses r
    JOIN annotations a ON r.id = a.response_id
    WHERE a.is_completed = 1
    ORDER BY r.item_index, a.annotator_id
    """
    df = pd.read_sql(query, con)
    print(f"Total completed rating rows: {len(df)}")
    
    # Export full dataset CSV
    full_export_path1 = OUTPUT_TABLES_DIR / "human_ratings_4000_two_annotators.csv"
    full_export_path2 = TABLES_CSV_DIR / "human_ratings_4000_two_annotators.csv"
    df.to_csv(full_export_path1, index=False)
    df.to_csv(full_export_path2, index=False)
    print(f"Exported full dataset to {full_export_path1}")

    # Separate Annotator A and Annotator B
    df_a = df[df["annotator_id"] == "annotator_a"].set_index("response_id")
    df_b = df[df["annotator_id"] == "annotator_b"].set_index("response_id")

    # -------------------------------------------------------------
    # 1. Table: Canonical 4K Human Evaluation Summary Table
    # -------------------------------------------------------------
    # For each response, compute mean score across Annotators A and B
    df_mean = df.groupby(["model", "response_id", "prompt_id"])[DIM_KEYS].mean().reset_index()

    models = ["Qwen2.5-7B", "Qwen2.5-3B", "HingGPT", "Phi-3.5-mini"]
    summary_rows = []

    for m in models:
        m_df = df_mean[df_mean["model"] == m]
        m_ratings = df[df["model"] == m]
        row = {"model": m, "sample_prompts": len(m_df), "total_ratings": len(m_ratings)}
        
        for key, name in DIMENSIONS:
            vals = m_df[key].values
            mean_val = np.mean(vals)
            std_val = np.std(vals, ddof=1)
            med_val = np.median(vals)
            ci_lo, ci_hi = bootstrap_ci(vals)
            
            row[f"{key}_mean"] = round(mean_val, 4)
            row[f"{key}_std"] = round(std_val, 4)
            row[f"{key}_median"] = round(med_val, 4)
            row[f"{key}_ci95_low"] = round(ci_lo, 4)
            row[f"{key}_ci95_high"] = round(ci_hi, 4)
            row[f"{key}_formatted"] = f"{mean_val:.3f} [{ci_lo:.3f}, {ci_hi:.3f}]"

        summary_rows.append(row)

    # Benchmark Overall row
    overall_row = {"model": "BENCHMARK_OVERALL", "sample_prompts": len(df_mean), "total_ratings": len(df)}
    for key, name in DIMENSIONS:
        vals = df_mean[key].values
        mean_val = np.mean(vals)
        std_val = np.std(vals, ddof=1)
        med_val = np.median(vals)
        ci_lo, ci_hi = bootstrap_ci(vals)
        overall_row[f"{key}_mean"] = round(mean_val, 4)
        overall_row[f"{key}_std"] = round(std_val, 4)
        overall_row[f"{key}_median"] = round(med_val, 4)
        overall_row[f"{key}_ci95_low"] = round(ci_lo, 4)
        overall_row[f"{key}_ci95_high"] = round(ci_hi, 4)
        overall_row[f"{key}_formatted"] = f"{mean_val:.3f} [{ci_lo:.3f}, {ci_hi:.3f}]"
    summary_rows.append(overall_row)

    df_summary = pd.DataFrame(summary_rows)
    sum_csv1 = OUTPUT_TABLES_DIR / "table_human_evaluation_4000_summary.csv"
    sum_csv2 = TABLES_CSV_DIR / "table_human_evaluation_4000_summary.csv"
    df_summary.to_csv(sum_csv1, index=False)
    df_summary.to_csv(sum_csv2, index=False)
    print(f"Saved summary table to {sum_csv1}")

    # -------------------------------------------------------------
    # 2. Table: Inter-Annotator Agreement across 4,000 Matched Pairs
    # -------------------------------------------------------------
    matched_ids = sorted(list(set(df_a.index).intersection(set(df_b.index))))
    sub_a = df_a.loc[matched_ids]
    sub_b = df_b.loc[matched_ids]

    agr_rows = []
    for key, name in DIMENSIONS:
        y1 = sub_a[key].to_numpy(dtype=int)
        y2 = sub_b[key].to_numpy(dtype=int)

        exact_pct = float(np.mean(y1 == y2) * 100.0)
        close_pct = float(np.mean(np.abs(y1 - y2) <= 1) * 100.0)

        # QWK
        qwk = float(cohen_kappa_score(y1, y2, weights="quadratic"))
        qwk_lo, qwk_hi = bootstrap_agreement_ci(y1, y2, lambda a, b: cohen_kappa_score(a, b, weights="quadratic"))

        # Alpha
        alpha = krippendorff_alpha_ordinal(y1, y2)
        alpha_lo, alpha_hi = bootstrap_agreement_ci(y1, y2, krippendorff_alpha_ordinal)

        # Spearman
        spearman_rho, spearman_p = stats.spearmanr(y1, y2)

        # Mean Annotator A vs Mean Annotator B
        mean_a = float(np.mean(y1))
        mean_b = float(np.mean(y2))

        agr_rows.append({
            "dimension_key": key,
            "dimension": name,
            "matched_n": len(matched_ids),
            "annotator_a_mean": round(mean_a, 3),
            "annotator_b_mean": round(mean_b, 3),
            "exact_agreement_pct": round(exact_pct, 2),
            "close_agreement_plusminus1_pct": round(close_pct, 2),
            "qwk": round(qwk, 3),
            "qwk_ci95_low": round(qwk_lo, 3),
            "qwk_ci95_high": round(qwk_hi, 3),
            "qwk_formatted": f"{qwk:.3f} [{qwk_lo:.2f}, {qwk_hi:.2f}]",
            "krippendorff_alpha": round(alpha, 3),
            "alpha_ci95_low": round(alpha_lo, 3),
            "alpha_ci95_high": round(alpha_hi, 3),
            "alpha_formatted": f"{alpha:.3f} [{alpha_lo:.2f}, {alpha_hi:.2f}]",
            "spearman_rho": round(spearman_rho, 3),
            "spearman_p": f"{spearman_p:.4e}"
        })

    df_agr = pd.DataFrame(agr_rows)
    agr_csv1 = OUTPUT_TABLES_DIR / "table_human_evaluation_4000_inter_annotator_agreement.csv"
    agr_csv2 = TABLES_CSV_DIR / "table_human_evaluation_4000_inter_annotator_agreement.csv"
    df_agr.to_csv(agr_csv1, index=False)
    df_agr.to_csv(agr_csv2, index=False)
    print(f"Saved agreement table to {agr_csv1}")

    # -------------------------------------------------------------
    # 3. Table: Pairwise Statistical Significance Testing (N=1000 prompts)
    # -------------------------------------------------------------
    # Paired comparisons across all 6 model pairs for each dimension
    model_pairs = [
        ("Qwen2.5-3B", "Qwen2.5-7B"),
        ("Qwen2.5-3B", "Phi-3.5-mini"),
        ("Qwen2.5-3B", "HingGPT"),
        ("Qwen2.5-7B", "Phi-3.5-mini"),
        ("Qwen2.5-7B", "HingGPT"),
        ("HingGPT", "Phi-3.5-mini")
    ]

    sig_rows = []
    for key, name in DIMENSIONS:
        # Collect raw p-values for Holm-Bonferroni correction within this dimension
        dim_tests = []
        for m1, m2 in model_pairs:
            s1 = df_mean[df_mean["model"] == m1].sort_values("prompt_id")[key].values
            s2 = df_mean[df_mean["model"] == m2].sort_values("prompt_id")[key].values
            diff = s1 - s2
            
            # Paired Wilcoxon signed-rank test
            try:
                w_res = stats.wilcoxon(s1, s2, zero_method="wilcox")
                w_stat = float(w_res.statistic)
                p_val = float(w_res.pvalue)
            except Exception:
                w_stat = 0.0
                p_val = 1.0

            # Rank-Biserial Correlation r_rb = 4 * |W - E(W)| / (N*(N+1))
            n_nonzero = np.sum(diff != 0)
            if n_nonzero > 0:
                e_w = n_nonzero * (n_nonzero + 1) / 4.0
                r_rb = (np.mean(diff > 0) - np.mean(diff < 0))
            else:
                r_rb = 0.0

            # Paired t-test
            t_res = stats.ttest_rel(s1, s2)
            
            dim_tests.append({
                "dimension": name,
                "dimension_key": key,
                "comparison": f"{m1} vs {m2}",
                "mean_diff": round(float(np.mean(diff)), 4),
                "wilcoxon_stat": w_stat,
                "p_value_raw": p_val,
                "effect_size_r_rb": round(float(r_rb), 4),
                "paired_t_stat": round(float(t_res.statistic), 4),
                "paired_t_p": float(t_res.pvalue)
            })

        # Holm-Bonferroni step-down correction
        dim_tests.sort(key=lambda x: x["p_value_raw"])
        m_tests = len(dim_tests)
        running_max = 0.0
        for rank, test in enumerate(dim_tests):
            multiplier = m_tests - rank
            p_adj = min(1.0, test["p_value_raw"] * multiplier)
            # Ensure monotonicity
            p_adj = max(running_max, p_adj)
            running_max = p_adj
            test["p_value_holm_adjusted"] = p_adj
            test["significant_alpha_0_05"] = (p_adj < 0.05)

        sig_rows.extend(dim_tests)

    df_sig = pd.DataFrame(sig_rows)
    sig_csv1 = OUTPUT_TABLES_DIR / "table_human_evaluation_4000_pairwise_significance.csv"
    sig_csv2 = TABLES_CSV_DIR / "table_human_evaluation_4000_pairwise_significance.csv"
    df_sig.to_csv(sig_csv1, index=False)
    df_sig.to_csv(sig_csv2, index=False)
    print(f"Saved significance table to {sig_csv1}")

    # -------------------------------------------------------------
    # 4. Table: Annotator-Specific Means Comparison Table
    # -------------------------------------------------------------
    breakdown_rows = []
    for m in models:
        for ann_id, ann_label in [("annotator_a", "Annotator A (Lead)"), ("annotator_b", "Annotator B (Partner)")]:
            ann_sub = df[(df["model"] == m) & (df["annotator_id"] == ann_id)]
            b_row = {"model": m, "annotator": ann_label, "n_responses": len(ann_sub)}
            for key, name in DIMENSIONS:
                b_row[f"{key}_mean"] = round(ann_sub[key].mean(), 3)
                b_row[f"{key}_std"] = round(ann_sub[key].std(), 3)
            breakdown_rows.append(b_row)

    df_breakdown = pd.DataFrame(breakdown_rows)
    bk_csv1 = OUTPUT_TABLES_DIR / "table_human_evaluation_4000_annotator_breakdown.csv"
    bk_csv2 = TABLES_CSV_DIR / "table_human_evaluation_4000_annotator_breakdown.csv"
    df_breakdown.to_csv(bk_csv1, index=False)
    df_breakdown.to_csv(bk_csv2, index=False)
    print(f"Saved annotator breakdown table to {bk_csv1}")

    print("\nALL 4K HUMAN EVALUATION TABLES GENERATED SUCCESSFULLY!")

if __name__ == "__main__":
    main()
