"""
Inter-Annotator Agreement and Reliability Analysis for HinglishEval.
Computes:
- Klaus Krippendorff's Ordinal Alpha for all 6 dimensions
- Quadratic Weighted Kappa (QWK) for all 6 dimensions
- Exact and 1-off agreement percentages
- 95% Confidence Intervals via non-parametric bootstrapping
- Missing data coverage and sample size reports

Strictly adheres to empirical validity: Never fabricates annotations.
If study is incomplete or matched pairs are insufficient, reports progress status accurately.
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime
import numpy as np
import pandas as pd
from sklearn.metrics import cohen_kappa_score
from typing import Optional, Dict, Any, List, Tuple

# UTF-8 stdout configuration for Windows
sys.stdout.reconfigure(encoding="utf-8")

APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR.parent) not in sys.path:
    sys.path.insert(0, str(APP_DIR.parent))

from human_validation_app.config import RATING_DIMENSIONS, TOTAL_EXPECTED_RESPONSES
from human_validation_app.database import SessionLocal
from human_validation_app.models import Annotation


def krippendorff_alpha_ordinal(y1: np.ndarray, y2: np.ndarray) -> float:
    """
    Compute Klaus Krippendorff's alpha for ordinal data (1..5 scale) between two coders.
    Uses standard cumulative frequency difference metric for ordinal categories.
    """
    if len(y1) != len(y2) or len(y1) == 0:
        return float("nan")

    # If all ratings are identical across all units, agreement is 1.0
    if np.array_equal(y1, y2):
        return 1.0

    # Collect category counts across both coders
    all_values = np.concatenate([y1, y2])
    categories = np.arange(1, 6)  # Scale 1..5
    n_total = len(all_values)

    counts = {c: np.sum(all_values == c) for c in categories}

    # Ordinal metric distance matrix: delta(c, k)^2
    # delta(c, k) = sum_{g=c}^k n_g - (n_c + n_k)/2
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

    # Observed disagreement Do
    d_observed = np.sum([delta[int(a), int(b)] for a, b in zip(y1, y2)]) / len(y1)

    # Expected disagreement De
    d_expected = 0.0
    for c in range(1, 6):
        for k in range(1, 6):
            d_expected += counts[c] * counts[k] * delta[c, k]
    d_expected /= (n_total * (n_total - 1))

    if d_expected == 0:
        return 1.0 if d_observed == 0 else 0.0

    alpha = 1.0 - (d_observed / d_expected)
    return float(alpha)


def bootstrap_ci(y1: np.ndarray, y2: np.ndarray, metric_fn, n_boot: int = 500, ci: float = 0.95):
    """Compute empirical non-parametric bootstrap confidence interval."""
    if len(y1) < 10:
        return (float("nan"), float("nan"))

    rng = np.random.default_rng(seed=42)
    scores = []
    n = len(y1)
    for _ in range(n_boot):
        idx = rng.integers(0, n, size=n)
        val = metric_fn(y1[idx], y2[idx])
        if not np.isnan(val):
            scores.append(val)

    if len(scores) < 20:
        return (float("nan"), float("nan"))

    lower = np.percentile(scores, (1 - ci) / 2 * 100)
    upper = np.percentile(scores, (1 + ci) / 2 * 100)
    return (float(lower), float(upper))


def analyze_agreement(csv_path: Optional[str] = None) -> str:
    """Analyze agreement from database or exported CSV."""
    if csv_path and os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
    else:
        # Load directly from database
        session = SessionLocal()
        try:
            records = session.query(
                Annotation.response_id,
                Annotation.annotator_id,
                Annotation.fluency,
                Annotation.code_mixing_naturalness,
                Annotation.hindi_grammar,
                Annotation.prompt_adherence,
                Annotation.spelling_consistency,
                Annotation.overall,
                Annotation.is_completed
            ).all()
            df = pd.DataFrame([r._asdict() for r in records])
        finally:
            session.close()

    if df.empty:
        return "# HinglishEval Agreement Report\n\n**Status:** No annotations recorded yet in database."

    # Filter to completed records only
    df_comp = df[df["is_completed"] == True].copy()
    df_a = df_comp[df_comp["annotator_id"] == "annotator_a"].set_index("response_id")
    df_b = df_comp[df_comp["annotator_id"] == "annotator_b"].set_index("response_id")

    matched_ids = sorted(list(set(df_a.index).intersection(set(df_b.index))))
    matched_count = len(matched_ids)

    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    report = f"""# HinglishEval Inter-Annotator Agreement Report
**Analysis Timestamp:** {timestamp}  
**Total Target Responses:** {TOTAL_EXPECTED_RESPONSES}  
**Annotator A Completed:** {len(df_a)} / {TOTAL_EXPECTED_RESPONSES}  
**Annotator B Completed:** {len(df_b)} / {TOTAL_EXPECTED_RESPONSES}  
**Overlapping Matched Pairs (N):** {matched_count}  

---
"""

    if matched_count < 5:
        report += f"""## Study Completion Status: IN PROGRESS
> [!NOTE]
> Currently, {matched_count} matching responses have been fully evaluated by both independent annotators.
> In accordance with scientific integrity guidelines, no simulated, imputed, or fabricated scores are generated.
> Statistical agreement metrics (Ordinal Krippendorff's alpha and Quadratic Weighted Kappa) will be automatically computed once both evaluators advance the study.

### Pending Progress:
- Annotator A: {TOTAL_EXPECTED_RESPONSES - len(df_a)} responses pending
- Annotator B: {TOTAL_EXPECTED_RESPONSES - len(df_b)} responses pending
"""
        return report

    # If matched responses exist:
    report += """## Reliability & Agreement Statistics

| Evaluation Dimension | Matched N | Exact Agr. (%) | ±1 Agr. (%) | QWK (95% CI) | Ordinal α (95% CI) |
| :--- | :---: | :---: | :---: | :---: | :---: |
"""

    sub_a = df_a.loc[matched_ids]
    sub_b = df_b.loc[matched_ids]

    for dim in RATING_DIMENSIONS:
        y1 = sub_a[dim].to_numpy(dtype=int)
        y2 = sub_b[dim].to_numpy(dtype=int)

        exact_pct = float(np.mean(y1 == y2) * 100.0)
        close_pct = float(np.mean(np.abs(y1 - y2) <= 1) * 100.0)

        # QWK
        qwk = float(cohen_kappa_score(y1, y2, weights="quadratic"))
        qwk_lo, qwk_hi = bootstrap_ci(y1, y2, lambda a, b: cohen_kappa_score(a, b, weights="quadratic"))

        # Ordinal Alpha
        alpha = krippendorff_alpha_ordinal(y1, y2)
        alpha_lo, alpha_hi = bootstrap_ci(y1, y2, krippendorff_alpha_ordinal)

        qwk_str = f"{qwk:.3f} [{qwk_lo:.2f}, {qwk_hi:.2f}]" if not np.isnan(qwk_lo) else f"{qwk:.3f}"
        alpha_str = f"{alpha:.3f} [{alpha_lo:.2f}, {alpha_hi:.2f}]" if not np.isnan(alpha_lo) else f"{alpha:.3f}"

        pretty_dim = "Overall Quality" if dim == "overall" else dim.replace("_", " ").title()
        report += f"| **{pretty_dim}** | {matched_count} | {exact_pct:.1f}% | {close_pct:.1f}% | {qwk_str} | {alpha_str} |\n"

    report += f"""
### Interpretation Guidelines:
- **Krippendorff's α:** $\\ge 0.80$ demonstrates strong reliability; $\\ge 0.67$ permits tentative conclusions.
- **Quadratic Weighted Kappa:** Evaluates ordinal distance penalizing larger disagreements quadratically.
"""
    return report


def main():
    parser = argparse.ArgumentParser(description="Analyze Inter-Annotator Agreement for HinglishEval")
    parser.add_argument("--csv", type=str, default=None, help="Path to exported CSV (optional, defaults to database)")
    parser.add_argument("--out", type=str, default=None, help="Output markdown report path")
    args = parser.parse_args()

    report = analyze_agreement(args.csv)
    print(report)

    if args.out:
        out_p = Path(args.out).resolve()
        out_p.parent.mkdir(parents=True, exist_ok=True)
        with open(out_p, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"\nReport written to {out_p}")


if __name__ == "__main__":
    main()
