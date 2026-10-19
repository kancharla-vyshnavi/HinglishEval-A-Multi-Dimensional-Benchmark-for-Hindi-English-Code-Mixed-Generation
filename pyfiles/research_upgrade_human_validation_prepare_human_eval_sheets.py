"""
prepare_human_eval_sheets.py
Generates user-friendly, blinded offline human evaluation CSV sheets:
1. annotator_A_pending_ratings.csv (71 pending items for Annotator A)
2. annotator_B_pending_ratings.csv (485 pending items for Annotator B)
3. annotator_A_rating_sheet.csv (all 500 items, with 429 completed ratings pre-filled)
4. annotator_B_rating_sheet.csv (all 500 items, with 15 completed ratings pre-filled)
5. HUMAN_EVALUATION_OFFLINE_GUIDE.md (comprehensive scoring guide and offline workflow)

All rating sheets are blinded (no model architecture names or AI scores revealed).
Requires zero external APIs or model calls.
"""

import os
import sys
import sqlite3
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MANIFEST_PATH = os.path.join(BASE_DIR, "assignment_manifest.csv")
DB_PATH = os.path.join(BASE_DIR, "ratings.db")

GUIDE_PATH = os.path.join(BASE_DIR, "HUMAN_EVALUATION_OFFLINE_GUIDE.md")

COLUMNS = [
    "assignment_id",
    "item_index",
    "category",
    "prompt",
    "response",
    "source_text",
    "fluency_1_to_5",
    "code_mixing_naturalness_1_to_5",
    "hindi_grammar_1_to_5",
    "prompt_adherence_1_to_5",
    "spelling_consistency_1_to_5",
    "overall_1_to_5",
    "notes"
]

def main():
    print("=" * 80)
    print("PREPARING OFFLINE HUMAN EVALUATION SHEETS")
    print("=" * 80)

    if not os.path.exists(MANIFEST_PATH):
        raise FileNotFoundError(f"Manifest not found: {MANIFEST_PATH}")
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database not found: {DB_PATH}")

    df_manifest = pd.read_csv(MANIFEST_PATH)
    print(f"Loaded {len(df_manifest)} assignments from manifest.")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT response_id, annotator_id, fluency, code_mixing_naturalness, "
        "hindi_grammar, prompt_adherence, spelling_consistency, overall, notes FROM ratings"
    )
    db_ratings = {r[0]: r for r in cur.fetchall()}
    conn.close()
    print(f"Loaded {len(db_ratings)} existing ratings from ratings.db.")

    stats = {}

    for ann_id, prefix in [("annotator_a", "A"), ("annotator_b", "B")]:
        sub = df_manifest[df_manifest["annotator_id"] == ann_id]
        full_rows = []
        pending_rows = []
        completed_rows = []

        for _, row in sub.iterrows():
            resp_id = str(row["response_id"])
            r_entry = db_ratings.get(resp_id)
            is_completed = (r_entry is not None and r_entry[2] is not None)

            item = {
                "assignment_id": row["assignment_id"],
                "item_index": row["item_index"],
                "category": row.get("category", "Casual Conversation"),
                "prompt": row["prompt"],
                "response": row["response"],
                "source_text": row.get("source_text", ""),
                "fluency_1_to_5": int(r_entry[2]) if is_completed else "",
                "code_mixing_naturalness_1_to_5": int(r_entry[3]) if is_completed else "",
                "hindi_grammar_1_to_5": int(r_entry[4]) if is_completed else "",
                "prompt_adherence_1_to_5": int(r_entry[5]) if is_completed else "",
                "spelling_consistency_1_to_5": int(r_entry[6]) if is_completed else "",
                "overall_1_to_5": int(r_entry[7]) if is_completed else "",
                "notes": str(r_entry[8]) if (is_completed and r_entry[8]) else ""
            }

            full_rows.append(item)
            if is_completed:
                completed_rows.append(item)
            else:
                pending_rows.append(item)

        stats[ann_id] = {
            "total": len(full_rows),
            "completed": len(completed_rows),
            "pending": len(pending_rows)
        }

        # Save full sheet (pre-populated with existing scores, pending left blank)
        full_csv = os.path.join(BASE_DIR, f"annotator_{prefix}_rating_sheet.csv")
        pd.DataFrame(full_rows)[COLUMNS].to_csv(full_csv, index=False, encoding="utf-8")
        print(f"Saved: {full_csv} ({len(full_rows)} total rows: {len(completed_rows)} filled, {len(pending_rows)} blank)")

        # Save pending-only sheet (quick sheet containing ONLY the items remaining to be scored)
        pending_csv = os.path.join(BASE_DIR, f"annotator_{prefix}_pending_ratings.csv")
        pd.DataFrame(pending_rows)[COLUMNS].to_csv(pending_csv, index=False, encoding="utf-8")
        print(f"Saved: {pending_csv} ({len(pending_rows)} pending rows)")

    # Write the offline guide
    guide_content = f"""# HinglishEval: Offline Human Evaluation Guide

## 1. Study Overview
- **Total Dataset:** 1,000 distinct benchmark responses across 4 models (`HingGPT`, `Phi-3.5-mini`, `Qwen2.5-3B`, `Qwen2.5-7B`).
- **Blinding Protocol:** All model names, parameter counts, and automated judge scores are strictly hidden to ensure objective, unbiased evaluation.
- **Annotator Assignments (Disjoint Partition):**
  - **Annotator A (Lead Evaluator):** 500 responses | **{stats['annotator_a']['completed']} Completed** | **{stats['annotator_a']['pending']} Pending**
  - **Annotator B (Independent Evaluator):** 500 responses | **{stats['annotator_b']['completed']} Completed** | **{stats['annotator_b']['pending']} Pending**

---

## 2. CSV Files Available For Evaluation

| File Name | Purpose | Rows |
| :--- | :--- | :---: |
| [`annotator_A_pending_ratings.csv`](file:///research_upgrade/human_validation/annotator_A_pending_ratings.csv) | **Recommended for Annotator A.** Contains only the {stats['annotator_a']['pending']} pending responses. | {stats['annotator_a']['pending']} |
| [`annotator_B_pending_ratings.csv`](file:///research_upgrade/human_validation/annotator_B_pending_ratings.csv) | **Recommended for Annotator B.** Contains only the {stats['annotator_b']['pending']} pending responses. | {stats['annotator_b']['pending']} |
| [`annotator_A_rating_sheet.csv`](file:///research_upgrade/human_validation/annotator_A_rating_sheet.csv) | Full 500-item sheet for Annotator A (pre-populated with {stats['annotator_a']['completed']} finished ratings). | 500 |
| [`annotator_B_rating_sheet.csv`](file:///research_upgrade/human_validation/annotator_B_rating_sheet.csv) | Full 500-item sheet for Annotator B (pre-populated with {stats['annotator_b']['completed']} finished ratings). | 500 |

---

## 3. Evaluation Dimensions & Likert Scoring Scale (1 to 5)

Each response must be assigned an integer score from **1 (worst)** to **5 (best)** across all six dimensions:

### 1. `fluency_1_to_5`
- **1 (Broken):** Incoherent, disjointed fragments, repetitive loops, or syntax breakdowns.
- **2 (Poor):** Awkward phrasing, heavy stumbling, or partial sentence fragments.
- **3 (Acceptable):** Understandable with noticeable phrasing awkwardness.
- **4 (Good):** Natural, flowing bilingual sentences with minor stylistic blemishes.
- **5 (Flawless):** Highly articulate, smooth, native-sounding conversational flow.

### 2. `code_mixing_naturalness_1_to_5`
- **1 (Unnatural):** Unnatural monolingual rewrite, or jarring word-by-word dictionary substitution.
- **2 (Rigid):** Forced code-mixing that does not follow Hindi matrix syntax.
- **3 (Moderate):** Understandable code-switching with some artificial phrasing.
- **4 (Natural):** Smooth intra-sentential switching matching authentic urban Hindi-English.
- **5 (Authentic):** Masterful bilingual code-switching; completely native vernacular feel.

### 3. `hindi_grammar_1_to_5`
- **1 (Severe Errors):** Corrupted postpositions, gender/number disagreement, incorrect auxiliary verbs.
- **2 (Frequent Errors):** Notable grammatical clashes disrupting meaning.
- **3 (Noticeable Flaws):** Understandable but with minor agreement slips (e.g. *karta* vs *karti*).
- **4 (Sound):** Grammatically correct with standard postpositional structures.
- **5 (Impeccable):** Flawless Hindi morphosyntax and verb-complement alignment.

### 4. `prompt_adherence_1_to_5`
- **1 (Irrelevant/Crash):** Empty generation, crash traceback, complete refusal, or totally unrelated topic.
- **2 (Weak):** Barely touches user query; largely veers off into generic statements.
- **3 (Partial):** Answers the question partially but misses core nuances or instructions.
- **4 (Strong):** Directly and coherently addresses the user's prompt.
- **5 (Exemplary):** Thoroughly, accurately, and contextually addresses the prompt.

### 5. `spelling_consistency_1_to_5`
- **1 (Chaos):** Chaotic transliteration, extreme vowel dropping, unreadable Romanized Hindi.
- **2 (Erratic):** Inconsistent spelling of common words within the same utterance.
- **3 (Readable):** Mostly readable with non-standard phonetic choices.
- **4 (Standard):** Consistent, readable Romanized Hindi transliteration.
- **5 (Exemplary):** Standard, clean, and unambiguous Romanized Hindi orthography.

### 6. `overall_1_to_5`
- **1 (Unusable):** Fails to provide meaningful communication.
- **2 (Below Average):** Significant flaws across multiple dimensions.
- **3 (Adequate):** Acceptable everyday conversational response.
- **4 (High Quality):** Strong, pleasant, and fluent code-mixed response.
- **5 (Publication Quality):** Outstanding, benchmark-setting Hinglish generation.

---

## 4. Offline Workflow & Merging

1. Open either the pending sheet (e.g., `annotator_A_pending_ratings.csv`) or the full sheet in Microsoft Excel, LibreOffice, or any text editor.
2. Fill in integer scores (1 to 5) for the 6 score columns.
3. Save the CSV file with standard UTF-8 encoding.
4. Run the validation and merge command:
```powershell
.\\.venv311\\Scripts\\python.exe research_upgrade\\human_validation\\merge_and_validate_offline.py --file research_upgrade\\human_validation\\annotator_A_pending_ratings.csv --annotator annotator_a
```
5. To validate without saving changes (dry-run):
```powershell
.\\.venv311\\Scripts\\python.exe research_upgrade\\human_validation\\merge_and_validate_offline.py --file research_upgrade\\human_validation\\annotator_A_pending_ratings.csv --annotator annotator_a --dry-run
```
6. The script automatically updates `ratings.db`, re-computes all summary statistics, verifies data integrity, and updates `human_validation_report.md` with zero API dependencies.
"""

    with open(GUIDE_PATH, "w", encoding="utf-8") as f:
        f.write(guide_content)
    print(f"Saved: {GUIDE_PATH}")

    print("\n" + "=" * 80)
    print("ALL OFFLINE HUMAN EVALUATION SHEETS PREPARED SUCCESSFULLY")
    print(f"Annotator A: {stats['annotator_a']['completed']} / 500 completed, {stats['annotator_a']['pending']} pending")
    print(f"Annotator B: {stats['annotator_b']['completed']} / 500 completed, {stats['annotator_b']['pending']} pending")
    print("=" * 80)

if __name__ == "__main__":
    main()
