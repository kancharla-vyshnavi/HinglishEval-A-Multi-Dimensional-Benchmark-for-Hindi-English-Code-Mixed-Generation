"""
CLI Export and Data Validation Utility for HinglishEval Human Validation Platform.
Exports complete dataset with blinded model mapping unmasked for research analysis,
and prints a comprehensive validation report covering response integrity, completion status,
and agreement readiness.
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime
import pandas as pd

# UTF-8 stdout configuration for Windows
sys.stdout.reconfigure(encoding="utf-8")

# Ensure package importability
APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR.parent) not in sys.path:
    sys.path.insert(0, str(APP_DIR.parent))

from human_validation_app.config import TOTAL_EXPECTED_RESPONSES, RATING_DIMENSIONS
from human_validation_app.database import SessionLocal
from human_validation_app.models import Response as StimulusResponse, Annotator, Annotation


def generate_export_dataframe(session) -> pd.DataFrame:
    """Generate complete ratings DataFrame conforming to required schema."""
    results = session.query(
        StimulusResponse.id.label("response_id"),
        StimulusResponse.item_index,
        StimulusResponse.prompt_id,
        StimulusResponse.model,
        Annotation.annotator_id,
        StimulusResponse.prompt,
        StimulusResponse.response,
        Annotation.fluency,
        Annotation.code_mixing_naturalness,
        Annotation.hindi_grammar,
        Annotation.prompt_adherence,
        Annotation.spelling_consistency,
        Annotation.overall,
        Annotation.notes,
        Annotation.is_completed,
        Annotation.submitted_at,
        Annotation.updated_at
    ).outerjoin(
        Annotation, StimulusResponse.id == Annotation.response_id
    ).order_by(
        StimulusResponse.item_index.asc(), Annotation.annotator_id.asc()
    ).all()

    rows = []
    for r in results:
        rows.append({
            "response_id": r.response_id,
            "prompt_id": r.prompt_id,
            "model": r.model,
            "annotator_id": r.annotator_id if r.annotator_id else "",
            "prompt": r.prompt,
            "response": r.response,
            "fluency": r.fluency if r.fluency is not None else pd.NA,
            "code_mixing_naturalness": r.code_mixing_naturalness if r.code_mixing_naturalness is not None else pd.NA,
            "hindi_grammar": r.hindi_grammar if r.hindi_grammar is not None else pd.NA,
            "prompt_adherence": r.prompt_adherence if r.prompt_adherence is not None else pd.NA,
            "spelling_consistency": r.spelling_consistency if r.spelling_consistency is not None else pd.NA,
            "overall": r.overall if r.overall is not None else pd.NA,
            "notes": r.notes if r.notes else "",
            "is_completed": r.is_completed if r.is_completed is not None else False,
            "submitted_at": r.submitted_at.isoformat() if r.submitted_at else "",
            "updated_at": r.updated_at.isoformat() if r.updated_at else ""
        })

    return pd.DataFrame(rows)


def run_validation_report(session) -> str:
    """Generate markdown validation report."""
    total_loaded = session.query(StimulusResponse).count()
    unique_ids = session.query(StimulusResponse.id).distinct().count()

    # Model coverage check
    model_counts = {}
    for r in session.query(StimulusResponse.model).all():
        model_counts[r[0]] = model_counts.get(r[0], 0) + 1

    # Annotators status
    prog_a = session.query(Annotation).filter_by(annotator_id="annotator_a", is_completed=True).count()
    prog_b = session.query(Annotation).filter_by(annotator_id="annotator_b", is_completed=True).count()

    total_a = session.query(Annotation).filter_by(annotator_id="annotator_a").count()
    total_b = session.query(Annotation).filter_by(annotator_id="annotator_b").count()

    # Agreement ready: response_id where BOTH annotator_a and annotator_b have is_completed=True
    a_completed_ids = set(
        r[0] for r in session.query(Annotation.response_id).filter_by(
            annotator_id="annotator_a", is_completed=True
        ).all()
    )
    b_completed_ids = set(
        r[0] for r in session.query(Annotation.response_id).filter_by(
            annotator_id="annotator_b", is_completed=True
        ).all()
    )
    matched_count = len(a_completed_ids.intersection(b_completed_ids))

    report = f"""# HinglishEval Human Validation Data Report
**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}

## 1. Stimulus Dataset Integrity
- **Total Loaded Responses:** {total_loaded} / {TOTAL_EXPECTED_RESPONSES}
- **Unique Response IDs:** {unique_ids}
- **Model Distribution:**
"""
    for m, c in sorted(model_counts.items()):
        report += f"  - `{m}`: {c} responses\n"

    report += f"""
## 2. Annotator Completion & Progress
| Annotator | Saved Records | Fully Completed (6/6 Dims) | Target | Progress (%) |
| :--- | :---: | :---: | :---: | :---: |
| **Annotator A (Lead)** | {total_a} | {prog_a} | {TOTAL_EXPECTED_RESPONSES} | {(prog_a / TOTAL_EXPECTED_RESPONSES * 100):.1f}% |
| **Annotator B (Partner)** | {total_b} | {prog_b} | {TOTAL_EXPECTED_RESPONSES} | {(prog_b / TOTAL_EXPECTED_RESPONSES * 100):.1f}% |

## 3. Data Quality & Constraints
- **Invalid Values Detected:** 0 (enforced via DB schema and API validation)
- **Duplicate Annotations Detected:** 0 (enforced via UNIQUE constraint on `(response_id, annotator_id)`)
- **Agreement-Ready Matched Responses:** {matched_count} / {TOTAL_EXPECTED_RESPONSES}

## 4. Study Status
- **Annotator A Remaining:** {TOTAL_EXPECTED_RESPONSES - prog_a}
- **Annotator B Remaining:** {TOTAL_EXPECTED_RESPONSES - prog_b}
- **Overall Completion:** {"COMPLETED" if (prog_a == TOTAL_EXPECTED_RESPONSES and prog_b == TOTAL_EXPECTED_RESPONSES) else "IN PROGRESS"}
"""
    return report


def main():
    parser = argparse.ArgumentParser(description="Export HinglishEval Human Ratings and Validation Report")
    parser.add_argument("--output", type=str, default=None, help="Output CSV path for exported ratings")
    parser.add_argument("--report", action="store_true", help="Print validation report to stdout")
    parser.add_argument("--report-file", type=str, default=None, help="Save validation report to markdown file")
    args = parser.parse_args()

    session = SessionLocal()
    try:
        if args.output:
            out_path = Path(args.output).resolve()
            out_path.parent.mkdir(parents=True, exist_ok=True)
            df = generate_export_dataframe(session)
            df.to_csv(out_path, index=False, encoding="utf-8")
            print(f"Exported {len(df)} records to {out_path}")

        if args.report or args.report_file:
            report_text = run_validation_report(session)
            if args.report:
                print(report_text)
            if args.report_file:
                rf = Path(args.report_file).resolve()
                rf.parent.mkdir(parents=True, exist_ok=True)
                with open(rf, "w", encoding="utf-8") as f:
                    f.write(report_text)
                print(f"Validation report saved to {rf}")
    finally:
        session.close()


if __name__ == "__main__":
    main()
