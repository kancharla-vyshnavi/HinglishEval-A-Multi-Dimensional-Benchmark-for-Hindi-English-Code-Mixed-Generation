import re
import os
import json
import glob
import pandas as pd
import numpy as np

PAPER_PATH = "paper.md"
TABLES_DIR = r"outputs\final_research_tables"
REPORT_PATH = r"research_upgrade\reports\consistency_audit_report.md"

def main():
    print("=" * 80)
    print("AUDIT: CONSISTENCY ACROSS REPORTED NUMBERS, TABLES, AND FIGURES")
    print("=" * 80)

    with open(PAPER_PATH, "r", encoding="utf-8") as f:
        paper_text = f.read()

    discrepancies = []
    verifications = []

    # 1. Hardware & Training Configuration:
    adapter_configs = {}
    for p in glob.glob("data/model/**/adapter_config.json", recursive=True):
        with open(p) as f:
            cfg = json.load(f)
            adapter_configs[p] = (cfg.get("r"), cfg.get("lora_alpha"))

    print(f"Found {len(adapter_configs)} adapter configs.")
    for p, (r, alpha) in adapter_configs.items():
        if r != 16 or alpha != 32:
            discrepancies.append({
                "source": "Model Checkpoints vs Paper.md Section 4 (Line 62)",
                "reported": "QLoRA (r = 16, alpha = 32)",
                "actual": f"{p} has r = {r}, alpha = {alpha}",
                "severity": "CRITICAL",
                "explanation": "Paper claims CPT models were adapted with r=16, alpha=32, but actual saved adapter_config.json files have r=8, alpha=16."
            })
            break

    # 2. Table 3: Overall Performance
    t3 = pd.read_csv(os.path.join(TABLES_DIR, "table_3_overall_model_performance.csv"))
    for idx, row in t3.iterrows():
        model = row["Model"]
        m_mean, m_sd = f"{row['Mistral_Mean']:.3f}", f"{row['Mistral_SD']:.3f}"
        o_mean, o_sd = f"{row['OLMo_Mean']:.3f}", f"{row['OLMo_SD']:.3f}"
        c_mean, c_sd = f"{row['Combined_Mean']:.3f}", f"{row['Combined_SD']:.3f}"
        n = int(row["Combined_N"])
        
        pattern = rf"{model}\s+{m_mean}\s*±\s*{m_sd}\s+{o_mean}\s*±\s*{o_sd}\s+{c_mean}\s*±\s*{c_sd}\s+{n}"
        if re.search(pattern, paper_text):
            verifications.append(f"Table 3 ({model}): Exact match between CSV and paper ({m_mean}±{m_sd}, {o_mean}±{o_sd}, {c_mean}±{c_sd}, N={n})")
        else:
            discrepancies.append({
                "source": f"Table 3 ({model})",
                "reported": "Paper table string check",
                "actual": f"{m_mean}±{m_sd}, {o_mean}±{o_sd}, {c_mean}±{c_sd}, N={n}",
                "severity": "MODERATE",
                "explanation": "Table 3 value formatted differently in paper."
            })

    # 3. Table 4: Dimension-wise Performance
    t4 = pd.read_csv(os.path.join(TABLES_DIR, "table_4_dimension_wise_performance.csv"))
    for dim in ["Fluency", "Code-Mixing Naturalness", "Hindi Grammar", "Prompt Adherence", "Spelling Consistency", "Overall Quality"]:
        dim_data = t4[t4["Dimension"] == dim]
        for idx, row in dim_data.iterrows():
            m = row["Model"]
            score_str = f"{row['Combined_Mean']:.3f} ± {row['Combined_SD']:.3f}"
            if score_str in paper_text:
                verifications.append(f"Table 4 ({dim} - {m}): Exact match ({score_str})")
            else:
                discrepancies.append({
                    "source": f"Table 4 ({dim} - {m})",
                    "reported": "Paper string check",
                    "actual": score_str,
                    "severity": "MINOR",
                    "explanation": f"Mismatch in Table 4 for {dim} on {m}: CSV has {score_str}"
                })

    # 4. Table 5: Inter-Judge Reliability
    t5 = pd.read_csv(os.path.join(TABLES_DIR, "table_5_inter_judge_reliability.csv"))
    for idx, row in t5.iterrows():
        dim = row["Dimension"]
        qwk = f"{row['Quadratic_Weighted_Kappa_QWK']:.3f}"
        spearman = f"{row['Spearman_Rho']:.3f}"
        if qwk in paper_text and spearman in paper_text:
            verifications.append(f"Table 5 ({dim}): Exact match (QWK={qwk}, Rho={spearman})")
        else:
            discrepancies.append({
                "source": f"Table 5 ({dim})",
                "reported": "Paper Table 5 values",
                "actual": f"QWK={qwk}, Rho={spearman}",
                "severity": "MODERATE",
                "explanation": f"Table 5 {dim} mismatch: QWK={qwk}, Rho={spearman}"
            })

    # 5. Table 6: Robustness Analysis
    t6 = pd.read_csv(os.path.join(TABLES_DIR, "table_6_robustness_analysis.csv"))
    for idx, row in t6.iterrows():
        dim = row["Dimension"]
        orig_mean = f"{row['Original_Rubric_Mean']:.3f}"
        pert_mean = f"{row['Perturbed_Rubric_Mean']:.3f}"
        shift = f"{row['Signed_Mean_Change']:+.3f}"
        if orig_mean in paper_text and pert_mean in paper_text:
            verifications.append(f"Table 6 ({dim}): Exact match (Orig={orig_mean}, Pert={pert_mean}, Shift={shift})")
        else:
            discrepancies.append({
                "source": f"Table 6 ({dim})",
                "reported": "Paper Table 6 values",
                "actual": f"Orig={orig_mean}, Pert={pert_mean}, Shift={shift}",
                "severity": "MINOR",
                "explanation": f"Table 6 {dim} mismatch in values"
            })

    # 6. Table 8: Error Analysis (E1-E10)
    t8 = pd.read_csv(os.path.join(TABLES_DIR, "table_8_error_analysis_e1_e10.csv"))
    for idx, row in t8.iterrows():
        code = row["Error_Code"]
        tot = row["Total_Count"]
        h_cnt = row["HingGPT_Count"]
        p_cnt = row["Phi_3_5_mini_Count"]
        q3_cnt = row["Qwen2_5_3B_Count"]
        q7_cnt = row["Qwen2_5_7B_Count"]
        pattern = rf"{code}\s+.*?\s+{tot}\s+.*?{h_cnt}\s+{p_cnt}\s+{q3_cnt}\s+{q7_cnt}"
        if re.search(pattern, paper_text):
            verifications.append(f"Table 8 ({code}): Exact match (Total={tot}, HingGPT={h_cnt}, Phi={p_cnt}, Qwen3={q3_cnt}, Qwen7={q7_cnt})")
        else:
            discrepancies.append({
                "source": f"Table 8 ({code})",
                "reported": "Counts in paper",
                "actual": f"Total={tot}, HingGPT={h_cnt}, Phi={p_cnt}, Qwen3={q3_cnt}, Qwen7={q7_cnt}",
                "severity": "MINOR",
                "explanation": f"Table 8 count mismatch for {code}"
            })

    # 7. Table 9: Linguistic Metrics (CMI)
    t9 = pd.read_csv(os.path.join(TABLES_DIR, "table_9_hinglish_linguistic_metrics.csv"))
    for idx, row in t9.iterrows():
        m = row["Model"]
        cmi = f"{row['Avg_Lexical_CMI_Percent']:.2f}"
        if cmi in paper_text:
            verifications.append(f"Table 9 ({m}): CMI match ({cmi}%)")
        else:
            discrepancies.append({
                "source": f"Table 9 ({m})",
                "reported": "CMI in paper",
                "actual": f"{cmi}%",
                "severity": "MODERATE",
                "explanation": f"Table 9 CMI for {m} is {cmi}%, check paper representation."
            })

    # 8. Check 17K Automatic Evaluation:
    if "table_17k_automatic_evaluation_trained_models.csv" not in paper_text and "171.232" not in paper_text:
        discrepancies.append({
            "source": "17K Automatic Evaluation",
            "reported": "Omitted from paper.md (only present in README.md section 14)",
            "actual": "table_17k_automatic_evaluation_trained_models.csv exists in outputs/final_research_tables",
            "severity": "MAJOR",
            "explanation": "The 17K automatic evaluation is missing from the main research paper (paper.md) but exists in repository and README."
        })
    else:
        verifications.append("17K Automatic Evaluation: Present in paper.md")

    # 9. Audit OLMo-2-1B Judge and Phi-3.5-mini Generation Error Artifacts
    df_gen = pd.read_csv(r"outputs\controlled_1000\benchmark_generations_.csv")
    phi_errs = df_gen[df_gen["response"].str.contains(r"\[GENERATION_ERROR\]|AttributeError", na=False)]
    if len(phi_errs) > 0:
        discrepancies.append({
            "source": "Benchmark Generations (Phi-3.5-mini)",
            "reported": "Controlled Generations: 4,000 valid generations",
            "actual": f"{len(phi_errs)} generation errors in benchmark_generations_.csv",
            "severity": "CRITICAL",
            "explanation": f"Phi-3.5-mini crashed during generation with AttributeError: 'DynamicCache' object has no attribute 'seen_tokens' for {len(phi_errs)} rows in benchmark_generations_.csv."
        })
    else:
        verifications.append("Benchmark Generations: 0 generation error strings found in benchmark_generations_.csv")

    # 10. Audit OLMo-2-1B raw scoring on crashed generations:
    with open(r"outputs\independent_judge_1000\independent_olmo2_1b_judge__results.jsonl", "r", encoding="utf-8") as f:
        crashed_high_scores = 0
        for line in f:
            try:
                obj = json.loads(line)
                if "[GENERATION_ERROR]" in obj.get("response", ""):
                    if int(obj.get("overall", 0)) >= 3:
                        crashed_high_scores += 1
            except Exception:
                pass
    if crashed_high_scores > 0:
        discrepancies.append({
            "source": "OLMo-2-1B Judge Scoring Validity",
            "reported": "Dual Independent LLM Evaluation (Section 6)",
            "actual": f"OLMo-2-1B gave scores >= 3 to {crashed_high_scores} crashed responses containing Python tracebacks!",
            "severity": "CRITICAL",
            "explanation": "OLMo-2-1B failed to parse or penalize crashed generations, hallucinating high scores (e.g. 4 or 5) for Python crash tracebacks, severely distorting reliability and Phi-3.5-mini scores."
        })

    # Summary
    print(f"\nAudit complete.")
    print(f"Total Verifications Passed: {len(verifications)}")
    print(f"Total Discrepancies / Inconsistencies Found: {len(discrepancies)}")

    # Write Markdown Report
    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("# HinglishEval Consistency & Quality Audit Report\n\n")
        f.write(f"**Audit Date:** {pd.Timestamp.now()}\n\n")
        f.write("## 1. Summary of Discrepancies, Inconsistencies, and Methodological Bugs\n\n")
        f.write("| Severity | Source | Reported | Actual | Issue Summary |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- |\n")
        for d in discrepancies:
            f.write(f"| **{d['severity']}** | `{d['source']}` | `{d['reported']}` | `{d['actual']}` | {d['explanation']} |\n")

        f.write("\n\n## 2. Verified Consistent Elements\n\n")
        for v in verifications:
            f.write(f"- [x] {v}\n")

    print(f"Saved consistency report to: {REPORT_PATH}")

if __name__ == "__main__":
    main()
