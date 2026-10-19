"""
Task 6: Prepare Blinded Second-Rater & Author Test-Retest Annotation Sheets
Creates:
- research_upgrade/v3/data/second_rater_annotation_sheet_100.csv
- research_upgrade/v3/data/author_test_retest_sheet_100.csv
- research_upgrade/v3/data/annotation_id_mapping.csv
"""

import os
import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = BASE_DIR.parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

INPUT_CSV = REPO_ROOT / "research_upgrade" / "tables" / "human_ratings_annotator_a_500.csv"

RUBRIC_HEADER = """# ==============================================================================
# HINGLISHEVAL: INDEPENDENT HUMAN EVALUATION ANNOTATION PROTOCOL
# ==============================================================================
# INSTRUCTIONS FOR ANNOTATOR:
# Please evaluate each model response against the source utterance on a 1-5 scale:
#
# 1. Fluency (1-5):
#    1 = Completely broken / ungrammatical / severe repetitive loops
#    3 = Moderately fluent; minor syntactic awkwardness
#    5 = Perfectly fluent; highly natural conversational phrasing
#
# 2. Code-Mixing Naturalness (1-5):
#    1 = Completely unnatural (unnatural word insertion / Spanish / pure English / pure Hindi)
#    3 = Acceptable mixing; somewhat forced or rigid boundaries
#    5 = Highly natural, authentic urban Hinglish matrix language mixing
#
# 3. Hindi Grammar (1-5):
#    1 = Severe Hindi case, gender, tense, or postposition errors
#    3 = Understandable Hindi syntax with noticeable grammatical flaws
#    5 = Native Hindi grammatical precision and natural inflection
#
# 4. Prompt Adherence (1-5):
#    1 = Ignores utterance completely / safety refusal / pure gibberish
#    3 = Addresses source utterance partially; drifts off-topic
#    5 = Perfectly responds to and follows the source utterance intent
#
# 5. Spelling Consistency (1-5):
#    1 = Chaotic, unreadable, highly distorted Roman transliteration
#    3 = Readable Roman spelling with frequent idiosyncratic variations
#    5 = Standard, consistent Roman-script Hindi phonetic conventions
#
# 6. Overall Quality (1-5):
#    1 = Catastrophic failure / unusable
#    2 = Poor / barely acceptable
#    3 = Moderate / passable
#    4 = Good / high quality
#    5 = Outstanding / native Hinglish benchmark quality
#
# NOTE: All model identifiers and internal IDs have been completely blinded.
# Do NOT consult external annotators or prior ratings. Leave unrated if in doubt.
# ==============================================================================
"""

def prepare_sheets():
    print("=" * 80)
    print("TASK 6: PREPARING BLINDED ANNOTATION SHEETS")
    print("=" * 80)

    if not INPUT_CSV.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT_CSV}")

    df = pd.read_csv(INPUT_CSV)
    print(f"Loaded {len(df)} validated human ratings from {INPUT_CSV.name}")
    print(f"Model breakdown: {df['model'].value_counts().to_dict()}")

    mapping_records = []

    # --------------------------------------------------------------------------
    # 1. Second-Rater Sheet (100 items, stratified 25 per model, seed=42)
    # --------------------------------------------------------------------------
    second_rater_samples = []
    models = sorted(df["model"].unique())

    for m in models:
        m_subset = df[df["model"] == m]
        # Stratify by category if possible
        sampled = m_subset.sample(n=25, random_state=42)
        second_rater_samples.append(sampled)

    second_df = pd.concat(second_rater_samples).sample(frac=1.0, random_state=42).reset_index(drop=True)
    second_df["blind_id"] = [f"BLIND_ITEM_{i+1:03d}" for i in range(len(second_df))]

    # Build blinded sheet
    second_sheet = pd.DataFrame({
        "blind_id": second_df["blind_id"],
        "category": second_df["category"],
        "source_utterance": second_df["source_text"],
        "model_response": second_df["response"],
        "fluency": "",
        "code_mixing_naturalness": "",
        "hindi_grammar": "",
        "prompt_adherence": "",
        "spelling_consistency": "",
        "overall_quality": "",
        "rater_notes": ""
    })

    second_out_path = DATA_DIR / "second_rater_annotation_sheet_100.csv"
    with open(second_out_path, "w", encoding="utf-8-sig") as f:
        f.write(RUBRIC_HEADER)
        second_sheet.to_csv(f, index=False)
    print(f"Created Second-Rater Sheet: {second_out_path} ({len(second_sheet)} rows, 25 per model)")

    for _, r in second_df.iterrows():
        mapping_records.append({
            "sheet_type": "second_rater",
            "blind_id": r["blind_id"],
            "assignment_id": r["assignment_id"],
            "response_id": r["response_id"],
            "model": r["model"],
            "category": r["category"],
            "row_index": r["row_index"],
            "prompt_id": r["prompt_id"],
            "original_annotator_overall": r["overall"]
        })

    # --------------------------------------------------------------------------
    # 2. Author Test-Retest Sheet (100 items, stratified 25 per model, seed=101)
    # --------------------------------------------------------------------------
    retest_samples = []
    for m in models:
        m_subset = df[df["model"] == m]
        sampled = m_subset.sample(n=25, random_state=101)
        retest_samples.append(sampled)

    retest_df = pd.concat(retest_samples).sample(frac=1.0, random_state=101).reset_index(drop=True)
    retest_df["retest_id"] = [f"RETEST_ITEM_{i+1:03d}" for i in range(len(retest_df))]

    retest_sheet = pd.DataFrame({
        "retest_id": retest_df["retest_id"],
        "category": retest_df["category"],
        "source_utterance": retest_df["source_text"],
        "model_response": retest_df["response"],
        "fluency": "",
        "code_mixing_naturalness": "",
        "hindi_grammar": "",
        "prompt_adherence": "",
        "spelling_consistency": "",
        "overall_quality": "",
        "retest_notes": ""
    })

    retest_out_path = DATA_DIR / "author_test_retest_sheet_100.csv"
    with open(retest_out_path, "w", encoding="utf-8-sig") as f:
        f.write(RUBRIC_HEADER)
        retest_sheet.to_csv(f, index=False)
    print(f"Created Author Test-Retest Sheet: {retest_out_path} ({len(retest_sheet)} rows, 25 per model)")

    for _, r in retest_df.iterrows():
        mapping_records.append({
            "sheet_type": "author_retest",
            "blind_id": r["retest_id"],
            "assignment_id": r["assignment_id"],
            "response_id": r["response_id"],
            "model": r["model"],
            "category": r["category"],
            "row_index": r["row_index"],
            "prompt_id": r["prompt_id"],
            "original_annotator_overall": r["overall"]
        })

    # --------------------------------------------------------------------------
    # 3. Secure Mapping Key
    # --------------------------------------------------------------------------
    mapping_df = pd.DataFrame(mapping_records)
    mapping_path = DATA_DIR / "annotation_id_mapping.csv"
    mapping_df.to_csv(mapping_path, index=False, encoding="utf-8-sig")
    print(f"Created Secure Annotation Mapping: {mapping_path} ({len(mapping_df)} records)")

if __name__ == "__main__":
    prepare_sheets()
