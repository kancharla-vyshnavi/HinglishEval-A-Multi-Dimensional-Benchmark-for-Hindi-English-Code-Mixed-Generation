# Specification: Pairwise Human Preference Protocol (Qwen2.5-3B vs Qwen2.5-7B)

## 1. Study Objective
To resolve whether the compact, highly localized **Qwen2.5-3B** architecture or the higher-capacity **Qwen2.5-7B** foundation model yields qualitatively superior Hindi-English code-mixed conversational text when judged by bilingual human evaluators.

---

## 2. Methodology & Blinding Safeguards
1. **Sampling Frame:** Exactly 100 benchmark prompts deterministically sampled with fixed seed `2026` from the 1,000 benchmark pool.
2. **Double-Blind Presentation:** 
   - Model identities are masked. Candidate A and Candidate B are randomly assigned with 50/50 probability per pair to prevent position bias.
   - Ground truth mapping is decoupled and stored only in the audit key.
3. **Annotator Pool:** 3 native, fluent Hindi-English bilingual speakers residing in India.
4. **Evaluation Criteria:**
   - **Preference Choice:** Annotators choose strictly between:
     - `A_Much_Better`
     - `A_Slightly_Better`
     - `Tie / Both_Equal`
     - `B_Slightly_Better`
     - `B_Much_Better`
   - **Guiding Dimensions:** Sociolinguistic naturalness, conversational engagement, absence of degenerate loops, and authentic matrix language insertion.
5. **Statistical Aggregation:**
   - Inter-annotator agreement: Fleiss' Kappa ($\kappa$) and majority win rates.
   - Two-sided binomial sign test with $lpha = 0.05$ to determine if preference diverges significantly from parity (50%).

---

## 3. Current Execution Status
- **Protocol & Material Status:** **Completed & Formatted** (`research_upgrade/tables/proposed_pairwise_preference_100_prompts.csv`).
- **Human Annotation Execution:** **Deferred to Final Phase (Task 7)** in compliance with research ethics rules. No synthetic or simulated human ratings are generated.
