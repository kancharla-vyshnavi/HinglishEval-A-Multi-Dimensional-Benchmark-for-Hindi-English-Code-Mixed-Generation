# Author Independence, Annotation Transparency, and AI Assistance Disclosure

## 1. Single-Annotator Status & Provenance of Existing Human Ratings

1. **Sole Primary Evaluator:**
   - All 500 completed human evaluation records (`research_upgrade/tables/human_ratings_annotator_a_500.csv`) were evaluated solely by the primary author (Annotator A).
   - No second human annotator contributed to the completed 500-item dataset.
   - Any prior references to an "Annotator B" or "inter-annotator consensus" in draft files were preliminary protocol scaffolding or unverified placeholders.
   - In accordance with research integrity standards, single-annotator judgments **do not establish inter-annotator reliability**.

2. **Dual Role & Potential Confirmation Bias:**
   - The primary author both performed the human evaluations and participated in model-selection decisions (e.g., selecting Qwen2.5-3B as the primary candidate).
   - Although the evaluation interface presented randomized, unlabelled outputs to mitigate immediate bias, the potential for unconscious cognitive confirmation bias remains an acknowledged scientific limitation.

---

## 2. Status of Second-Rater Validation & Author Test-Retest Protocols

1. **Independent Second-Rater Validation (PENDING):**
   - A dedicated 100-item evaluation sheet (`research_upgrade/v3/data/second_rater_annotation_sheet_100.csv`) has been prepared.
   - The sheet is stratified across all four models (exactly 25 items each for Qwen2.5-3B, Qwen2.5-7B, Phi-3.5-mini, and HingGPT) and diverse conversational categories.
   - All model identifiers, system internal keys, and previous ratings have been stripped.
   - **Current Status:** `PENDING`. Zero ratings have been entered or fabricated. The sheet is staged and awaiting completion by an independent native Hindi-English bilingual rater.
   - Inter-annotator agreement metrics (Krippendorff's $\alpha_{\text{ordinal}}$, Quadratic Weighted Kappa, and rank correlation) will be reported strictly after genuine ratings are received.

2. **Author Test-Retest Reliability Protocol (PENDING):**
   - A separate 100-item blinded re-rating list (`research_upgrade/v3/data/author_test_retest_sheet_100.csv`) has been generated using a distinct random seed (`seed = 101`).
   - Prior scores are concealed to ensure that re-evaluation after a 1-to-2 week washout interval provides an unbiased estimate of intra-annotator stability.
   - **Current Status:** `PENDING`. Intra-annotator test-retest reliability will be calculated upon completion.

3. **Secure Unblinding Key:**
   - Ground truth correspondences are preserved in `research_upgrade/v3/data/annotation_id_mapping.csv`. Access to this key is strictly quarantined from annotators until all ratings are logged.

---

## 3. Scope and Nature of AI Assistance Disclosure

In compliance with ACL, NeurIPS, and IEEE policies on generative AI and automated tools in scientific research:

1. **Role of AI Assistant:**
   - An AI coding assistant (DeepMind Antigravity) was utilized to execute software engineering tasks under the explicit instruction and technical oversight of the human author.
   - Permitted AI assistant duties included:
     - Automating reproducible data processing and statistical calculation scripts.
     - Extracting metadata and formatting LaTeX/Markdown tables from canonical CSV records.
     - Recomputing bootstrap confidence intervals, hypothesis tests, and effect sizes.
     - Auditing bibliographies against authoritative academic databases (ACL Anthology, arXiv, NeurIPS).

2. **Explicit Clarification of Non-Independence:**
   - The AI assistant **is not an independent external scientific auditor**.
   - Automated scripts executed by an AI assistant cannot confer external peer verification or "independent auditing" status upon the manuscript.
   - All descriptive labels referring to the assistant as an "Independent Auditor" or claiming results are "100% verified by AI auditor" have been retracted and removed from the v3 manuscript and reports.

3. **Human Responsibility:**
   - The human author takes full, unreserved intellectual responsibility for the experimental design, code verification, data interpretation, factual claims, and conclusions presented in this work.
