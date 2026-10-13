# HinglishEval: Offline Human Evaluation Guide

## 1. Study Overview
- **Total Dataset:** 1,000 distinct benchmark responses across 4 models (`HingGPT`, `Phi-3.5-mini`, `Qwen2.5-3B`, `Qwen2.5-7B`).
- **Blinding Protocol:** All model names, parameter counts, and automated judge scores are strictly hidden to ensure objective, unbiased evaluation.
- **Annotator Assignments (Disjoint Partition):**
  - **Annotator A (Lead Evaluator):** 500 responses | **429 Completed** | **71 Pending**
  - **Annotator B (Independent Evaluator):** 500 responses | **15 Completed** | **485 Pending**

---

## 2. CSV Files Available For Evaluation

| File Name | Purpose | Rows |
| :--- | :--- | :---: |
| [`annotator_A_pending_ratings.csv`](file:///research_upgrade/human_validation/annotator_A_pending_ratings.csv) | **Recommended for Annotator A.** Contains only the 71 pending responses. | 71 |
| [`annotator_B_pending_ratings.csv`](file:///research_upgrade/human_validation/annotator_B_pending_ratings.csv) | **Recommended for Annotator B.** Contains only the 485 pending responses. | 485 |
| [`annotator_A_rating_sheet.csv`](file:///research_upgrade/human_validation/annotator_A_rating_sheet.csv) | Full 500-item sheet for Annotator A (pre-populated with 429 finished ratings). | 500 |
| [`annotator_B_rating_sheet.csv`](file:///research_upgrade/human_validation/annotator_B_rating_sheet.csv) | Full 500-item sheet for Annotator B (pre-populated with 15 finished ratings). | 500 |

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
.\.venv311\Scripts\python.exe research_upgrade\human_validation\merge_and_validate_offline.py --file research_upgrade\human_validation\annotator_A_pending_ratings.csv --annotator annotator_a
```
5. To validate without saving changes (dry-run):
```powershell
.\.venv311\Scripts\python.exe research_upgrade\human_validation\merge_and_validate_offline.py --file research_upgrade\human_validation\annotator_A_pending_ratings.csv --annotator annotator_a --dry-run
```
6. The script automatically updates `ratings.db`, re-computes all summary statistics, verifies data integrity, and updates `human_validation_report.md` with zero API dependencies.
