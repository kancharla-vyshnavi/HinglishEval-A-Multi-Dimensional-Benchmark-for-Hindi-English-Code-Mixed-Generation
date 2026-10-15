# HinglishEval Consistency & Quality Audit Report

**Audit Date:** 2026-10-14 02:17:14.070417

## 1. Summary of Discrepancies, Inconsistencies, and Methodological Bugs

| Severity | Source | Reported | Actual | Issue Summary |
| :--- | :--- | :--- | :--- | :--- |
| **CRITICAL** | `Model Checkpoints vs Paper.md Section 4 (Line 62)` | `QLoRA (r = 16, alpha = 32)` | `data/model\hinggpt_277k_cpt\checkpoint-17000\adapter_config.json has r = 8, alpha = 16` | Paper claims CPT models were adapted with r=16, alpha=32, but actual saved adapter_config.json files have r=8, alpha=16. |
| **MINOR** | `Table 4 (Fluency - HingGPT)` | `Paper string check` | `2.781 ± 0.557` | Mismatch in Table 4 for Fluency on HingGPT: CSV has 2.781 ± 0.557 |
| **MINOR** | `Table 4 (Fluency - Phi-3.5-mini)` | `Paper string check` | `2.487 ± 0.323` | Mismatch in Table 4 for Fluency on Phi-3.5-mini: CSV has 2.487 ± 0.323 |
| **MINOR** | `Table 4 (Fluency - Qwen2.5-3B)` | `Paper string check` | `3.485 ± 0.526` | Mismatch in Table 4 for Fluency on Qwen2.5-3B: CSV has 3.485 ± 0.526 |
| **MINOR** | `Table 4 (Fluency - Qwen2.5-7B)` | `Paper string check` | `3.258 ± 0.585` | Mismatch in Table 4 for Fluency on Qwen2.5-7B: CSV has 3.258 ± 0.585 |
| **MINOR** | `Table 4 (Code-Mixing Naturalness - HingGPT)` | `Paper string check` | `3.307 ± 0.672` | Mismatch in Table 4 for Code-Mixing Naturalness on HingGPT: CSV has 3.307 ± 0.672 |
| **MINOR** | `Table 4 (Code-Mixing Naturalness - Phi-3.5-mini)` | `Paper string check` | `2.938 ± 0.266` | Mismatch in Table 4 for Code-Mixing Naturalness on Phi-3.5-mini: CSV has 2.938 ± 0.266 |
| **MINOR** | `Table 4 (Code-Mixing Naturalness - Qwen2.5-3B)` | `Paper string check` | `4.014 ± 0.726` | Mismatch in Table 4 for Code-Mixing Naturalness on Qwen2.5-3B: CSV has 4.014 ± 0.726 |
| **MINOR** | `Table 4 (Code-Mixing Naturalness - Qwen2.5-7B)` | `Paper string check` | `3.796 ± 0.770` | Mismatch in Table 4 for Code-Mixing Naturalness on Qwen2.5-7B: CSV has 3.796 ± 0.770 |
| **MINOR** | `Table 4 (Hindi Grammar - HingGPT)` | `Paper string check` | `2.764 ± 0.515` | Mismatch in Table 4 for Hindi Grammar on HingGPT: CSV has 2.764 ± 0.515 |
| **MINOR** | `Table 4 (Hindi Grammar - Phi-3.5-mini)` | `Paper string check` | `2.452 ± 0.246` | Mismatch in Table 4 for Hindi Grammar on Phi-3.5-mini: CSV has 2.452 ± 0.246 |
| **MINOR** | `Table 4 (Hindi Grammar - Qwen2.5-3B)` | `Paper string check` | `3.412 ± 0.625` | Mismatch in Table 4 for Hindi Grammar on Qwen2.5-3B: CSV has 3.412 ± 0.625 |
| **MINOR** | `Table 4 (Hindi Grammar - Qwen2.5-7B)` | `Paper string check` | `3.304 ± 0.658` | Mismatch in Table 4 for Hindi Grammar on Qwen2.5-7B: CSV has 3.304 ± 0.658 |
| **MINOR** | `Table 4 (Prompt Adherence - HingGPT)` | `Paper string check` | `2.815 ± 0.708` | Mismatch in Table 4 for Prompt Adherence on HingGPT: CSV has 2.815 ± 0.708 |
| **MINOR** | `Table 4 (Prompt Adherence - Phi-3.5-mini)` | `Paper string check` | `2.910 ± 0.361` | Mismatch in Table 4 for Prompt Adherence on Phi-3.5-mini: CSV has 2.910 ± 0.361 |
| **MINOR** | `Table 4 (Prompt Adherence - Qwen2.5-3B)` | `Paper string check` | `3.717 ± 0.812` | Mismatch in Table 4 for Prompt Adherence on Qwen2.5-3B: CSV has 3.717 ± 0.812 |
| **MINOR** | `Table 4 (Prompt Adherence - Qwen2.5-7B)` | `Paper string check` | `3.404 ± 0.913` | Mismatch in Table 4 for Prompt Adherence on Qwen2.5-7B: CSV has 3.404 ± 0.913 |
| **MINOR** | `Table 4 (Spelling Consistency - HingGPT)` | `Paper string check` | `3.604 ± 0.806` | Mismatch in Table 4 for Spelling Consistency on HingGPT: CSV has 3.604 ± 0.806 |
| **MINOR** | `Table 4 (Spelling Consistency - Phi-3.5-mini)` | `Paper string check` | `2.946 ± 0.297` | Mismatch in Table 4 for Spelling Consistency on Phi-3.5-mini: CSV has 2.946 ± 0.297 |
| **MINOR** | `Table 4 (Spelling Consistency - Qwen2.5-3B)` | `Paper string check` | `4.410 ± 0.595` | Mismatch in Table 4 for Spelling Consistency on Qwen2.5-3B: CSV has 4.410 ± 0.595 |
| **MINOR** | `Table 4 (Spelling Consistency - Qwen2.5-7B)` | `Paper string check` | `4.434 ± 0.568` | Mismatch in Table 4 for Spelling Consistency on Qwen2.5-7B: CSV has 4.434 ± 0.568 |
| **MAJOR** | `17K Automatic Evaluation` | `Omitted from paper.md (only present in README.md section 14)` | `table_17k_automatic_evaluation_trained_models.csv exists in outputs/final_research_tables` | The 17K automatic evaluation is missing from the main research paper (paper.md) but exists in repository and README. |
| **CRITICAL** | `OLMo-2-1B Judge Scoring Validity` | `Dual Independent LLM Evaluation (Section 6)` | `OLMo-2-1B gave scores >= 3 to 970 crashed responses containing Python tracebacks!` | OLMo-2-1B failed to parse or penalize crashed generations, hallucinating high scores (e.g. 4 or 5) for Python crash tracebacks, severely distorting reliability and Phi-3.5-mini scores. |


## 2. Verified Consistent Elements

- [x] Table 3 (HingGPT): Exact match between CSV and paper (1.990±0.951, 4.182±0.613, 3.086±0.574, N=995)
- [x] Table 3 (Phi-3.5-mini): Exact match between CSV and paper (1.027±0.242, 4.894±0.336, 2.960±0.207, N=1000)
- [x] Table 3 (Qwen2.5-3B): Exact match between CSV and paper (3.563±1.081, 4.011±0.727, 3.787±0.641, N=994)
- [x] Table 3 (Qwen2.5-7B): Exact match between CSV and paper (3.173±1.139, 3.956±0.712, 3.564±0.722, N=1000)
- [x] Table 4 (Overall Quality - HingGPT): Exact match (3.086 ± 0.574)
- [x] Table 4 (Overall Quality - Phi-3.5-mini): Exact match (2.960 ± 0.207)
- [x] Table 4 (Overall Quality - Qwen2.5-3B): Exact match (3.787 ± 0.641)
- [x] Table 4 (Overall Quality - Qwen2.5-7B): Exact match (3.564 ± 0.722)
- [x] Table 5 (Fluency): Exact match (QWK=-0.142, Rho=-0.265)
- [x] Table 5 (Code-Mixing Naturalness): Exact match (QWK=-0.139, Rho=-0.311)
- [x] Table 5 (Hindi Grammar): Exact match (QWK=0.008, Rho=0.017)
- [x] Table 5 (Prompt Adherence): Exact match (QWK=-0.110, Rho=-0.279)
- [x] Table 5 (Spelling Consistency): Exact match (QWK=-0.166, Rho=-0.281)
- [x] Table 5 (Overall Quality): Exact match (QWK=-0.108, Rho=-0.341)
- [x] Table 6 (Fluency): Exact match (Orig=2.480, Pert=2.912, Shift=+0.432)
- [x] Table 6 (Code-Mixing Naturalness): Exact match (Orig=2.771, Pert=3.179, Shift=+0.408)
- [x] Table 6 (Hindi Grammar): Exact match (Orig=2.050, Pert=2.295, Shift=+0.245)
- [x] Table 6 (Prompt Adherence): Exact match (Orig=2.402, Pert=2.982, Shift=+0.579)
- [x] Table 6 (Spelling Consistency): Exact match (Orig=3.304, Pert=3.436, Shift=+0.132)
- [x] Table 6 (Overall Quality): Exact match (Orig=2.435, Pert=2.854, Shift=+0.419)
- [x] Table 8 (E1): Exact match (Total=61, HingGPT=6, Phi=6, Qwen3=19, Qwen7=30)
- [x] Table 8 (E2): Exact match (Total=648, HingGPT=53, Phi=264, Qwen3=180, Qwen7=151)
- [x] Table 8 (E3): Exact match (Total=26, HingGPT=9, Phi=1, Qwen3=10, Qwen7=6)
- [x] Table 8 (E4): Exact match (Total=284, HingGPT=98, Phi=73, Qwen3=68, Qwen7=45)
- [x] Table 8 (E5): Exact match (Total=242, HingGPT=36, Phi=117, Qwen3=41, Qwen7=48)
- [x] Table 8 (E6): Exact match (Total=1045, HingGPT=156, Phi=351, Qwen3=215, Qwen7=323)
- [x] Table 8 (E7): Exact match (Total=679, HingGPT=163, Phi=275, Qwen3=106, Qwen7=135)
- [x] Table 8 (E8): Exact match (Total=865, HingGPT=2, Phi=678, Qwen3=114, Qwen7=71)
- [x] Table 8 (E9): Exact match (Total=0, HingGPT=0, Phi=0, Qwen3=0, Qwen7=0)
- [x] Table 8 (E10): Exact match (Total=485, HingGPT=135, Phi=236, Qwen3=91, Qwen7=23)
- [x] Table 9 (HingGPT): CMI match (19.07%)
- [x] Table 9 (Phi-3.5-mini): CMI match (15.71%)
- [x] Table 9 (Qwen2.5-3B): CMI match (15.63%)
- [x] Table 9 (Qwen2.5-7B): CMI match (13.73%)
- [x] Benchmark Generations: 0 generation error strings found in benchmark_generations_.csv
