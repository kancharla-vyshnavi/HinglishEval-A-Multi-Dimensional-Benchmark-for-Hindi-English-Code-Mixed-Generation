# HinglishEval: Human Evaluation Validation Report

**Audit Timestamp:** `2026-10-13 18:00:30 UTC`
**Database Source:** [`ratings.db`](file:///C:/Users/vyshu/OneDrive/Desktop/HinglishLLM/research_upgrade/human_validation/ratings.db)
**Assignment Manifest:** [`assignment_manifest.csv`](file:///C:/Users/vyshu/OneDrive/Desktop/HinglishLLM/research_upgrade/human_validation/assignment_manifest.csv)

---

## 1. Assignment Manifest Integrity Audit

| Verification Check | Target / Expected | Actual Verified | Status |
| :--- | :---: | :---: | :---: |
| **Total Unique Source Responses** | 4,000 | 4,000 | ✓ PASS |
| **Annotator A Assigned Responses** | 2,000 | 2,000 | ✓ PASS |
| **Annotator B Assigned Responses** | 2,000 | 2,000 | ✓ PASS |
| **Assignment Overlap Between A & B** | 0 | 0 | ✓ PASS (Disjoint Partition) |
| **Model Balance (Per Annotator)** | 500 per model | 500 (all 4 models) | ✓ PASS |
| **Duplicate Response IDs** | 0 | 0 | ✓ PASS |
| **Original Source Files Preserved** | 100% untouched | 100% untouched | ✓ PASS |

---

## 2. Evaluation Progress & Status Summary

| Partition | Total Assigned | Completed | Pending (Unrated) | Invalid Scores | Completion % |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Annotator A (Lead Researcher)** | 2,000 | 0 | 2,000 | 0 | 0.00% |
| **Annotator B (Independent Evaluator)** | 2,000 | 0 | 2,000 | 0 | 0.00% |
| **Total Benchmark Pool** | 4,000 | 0 | 4,000 | 0 | 0.00% |

> [!IMPORTANT]
> **Zero-Fabrication & Integrity Notice:** Unsubmitted responses are explicitly classified as `pending` and are **NEVER** filled with synthetic or AI-judge numbers. Human evaluation validity requires genuine human completion.

---

## 3. Methodological Note on Inter-Annotator Agreement

> [!NOTE]
> **Non-Overlapping Assignment Disclosure:** Because Annotator A and Annotator B evaluate non-overlapping partitions of 2,000 responses each (targeting maximum benchmark coverage across all 4,000 outputs within feasible annotator effort), **inter-annotator reliability metrics (Cohen's Kappa, Quadratic Weighted Kappa $\kappa_w$, and Spearman's $\rho$) cannot be computed across their disjoint primary assignments.**
>
> If reviewer requirements necessitate formal inter-rater agreement computation, a calibrated **overlapping calibration subset** of 100 or 200 responses (e.g. 25–50 per model) can be scored independently by both annotators in a supplementary session.

---

## 4. Descriptive Score Statistics (Completed Responses)

_No completed human ratings have been submitted yet. Both annotator partitions currently stand in `pending` state._

Once human annotators submit ratings via the live web interface, re-running this script will populate full descriptive statistics, score distributions, and model comparisons automatically.

---

## 5. Generated Dataset Files

- Combined Ratings: [`combined_human_ratings.csv`](file:///C:/Users/vyshu/OneDrive/Desktop/HinglishLLM/research_upgrade/human_validation/combined_human_ratings.csv)
- Annotator A Ratings: [`annotator_A_ratings.csv`](file:///C:/Users/vyshu/OneDrive/Desktop/HinglishLLM/research_upgrade/human_validation/annotator_A_ratings.csv)
- Annotator B Ratings: [`annotator_B_ratings.csv`](file:///C:/Users/vyshu/OneDrive/Desktop/HinglishLLM/research_upgrade/human_validation/annotator_B_ratings.csv)
- Validation Report: [`human_evaluation_validation_report.md`](file:///C:/Users/vyshu/OneDrive/Desktop/HinglishLLM/research_upgrade/human_validation/human_evaluation_validation_report.md)
