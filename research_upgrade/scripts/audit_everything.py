import os
import sys
import sqlite3
import json
import pandas as pd
import numpy as np
from scipy.stats import spearmanr, wilcoxon, mannwhitneyu, friedmanchisquare
from sklearn.metrics import cohen_kappa_score

sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

print("=" * 80)
print("AUDIT SCRIPT: VERIFYING BENCHMARKS, JUDGES, STATISTICAL TESTS, AND HUMAN RATINGS")
print("=" * 80)

# 1. Benchmark prompts
bench_csv = os.path.join(ROOT, "outputs", "controlled_1000", "benchmark_generations_.csv")
df_bench = pd.read_csv(bench_csv)
print(f"Benchmark generations file: {bench_csv}")
print(f"Total rows: {len(df_bench)}")
print(f"Unique prompts in generations: {df_bench['row_index'].nunique()}")
print(f"Models in generations: {df_bench['model'].value_counts().to_dict()}")

orig_bench_csv = os.path.join(ROOT, "data", "benchmarks", "hinglish_bench_.csv")
if os.path.exists(orig_bench_csv):
    df_orig = pd.read_csv(orig_bench_csv)
    print(f"Original hinglish_bench_.csv rows: {len(df_orig)}")

leakage_csv = os.path.join(ROOT, "research_upgrade", "tables", "proposed_leakage_free_benchmark_992.csv")
if os.path.exists(leakage_csv):
    df_leak = pd.read_csv(leakage_csv)
    print(f"Leakage-free subset rows: {len(df_leak)}")

overlap_csv = os.path.join(ROOT, "research_upgrade", "tables", "benchmark_train_overlap_matches.csv")
if os.path.exists(overlap_csv):
    df_over = pd.read_csv(overlap_csv)
    print(f"Quarantined overlap rows: {len(df_over)}")

# 2. Judges
print("\n--- JUDGES AUDIT ---")
mistral_csv = os.path.join(ROOT, "outputs", "independent_judge_1000", "independent_mistral_judge__FINAL.csv")
df_mistral = pd.read_csv(mistral_csv)
print(f"Mistral CSV rows: {len(df_mistral)}")
print(f"Mistral nulls in overall: {df_mistral['overall'].isna().sum()}")
# Check if any text/traceback in scores
for d in ["fluency", "code_mixing_naturalness", "hindi_grammar", "prompt_adherence", "spelling_consistency", "overall"]:
    vals = pd.to_numeric(df_mistral[d], errors="coerce")
    print(f"  Mistral {d}: valid numeric = {vals.notna().sum()}, range = [{vals.min()}, {vals.max()}]")

qwen_jsonl = os.path.join(ROOT, "research_upgrade", "tables", "judge_qwen25_3b_4000_results.jsonl")
qwen_records = []
with open(qwen_jsonl, "r", encoding="utf-8") as f:
    for line in f:
        if line.strip():
            qwen_records.append(json.loads(line.strip()))
df_qwen = pd.DataFrame(qwen_records)
print(f"\nQwen JSONL total records: {len(df_qwen)}")
print(f"Qwen unique keys (row_index, model): {len(df_qwen.drop_duplicates(subset=['row_index', 'model']))}")
print(f"Qwen valid count (is_valid==True): {(df_qwen['is_valid'] == True).sum()}")
print(f"Qwen invalid count (is_valid==False): {(df_qwen['is_valid'] == False).sum()}")

# Check exact intersection between Mistral and Qwen
df_mistral["row_index"] = df_mistral["row_index"].astype(int)
df_mistral["model"] = df_mistral["model"].astype(str)
df_qwen["row_index"] = df_qwen["row_index"].astype(int)
df_qwen["model"] = df_qwen["model"].astype(str)

# Filter for valid records
valid_mistral = df_mistral.dropna(subset=["overall", "fluency", "code_mixing_naturalness", "hindi_grammar", "prompt_adherence", "spelling_consistency"]).copy()
valid_qwen = df_qwen[df_qwen["is_valid"] == True].dropna(subset=["overall", "fluency", "code_mixing_naturalness", "hindi_grammar", "prompt_adherence", "spelling_consistency"]).copy()

print(f"Valid Mistral rows: {len(valid_mistral)}")
print(f"Valid Qwen rows: {len(valid_qwen)}")

merged_mq = pd.merge(valid_mistral, valid_qwen, on=["row_index", "model"], suffixes=("_mistral", "_qwen"))
print(f"Exact intersection of valid records between Mistral and Qwen: N = {len(merged_mq)}")

# Inter-judge metrics on exact intersection
dims = ["fluency", "code_mixing_naturalness", "hindi_grammar", "prompt_adherence", "spelling_consistency", "overall"]
print("\nExact Inter-Judge Alignment (Mistral vs Qwen) on N =", len(merged_mq))
for d in dims:
    m_v = merged_mq[f"{d}_mistral"].astype(float)
    q_v = merged_mq[f"{d}_qwen"].astype(float)
    qwk = cohen_kappa_score(m_v.round().astype(int), q_v.round().astype(int), weights="quadratic")
    rho, p_val = spearmanr(m_v, q_v)
    print(f"  {d:<25}: QWK = {qwk:.4f}, Spearman rho = {rho:+.4f}, p = {p_val:.2e}")

# 3. Statistical Testing: Paired vs Independent
print("\n--- STATISTICAL METHODOLOGY AUDIT ---")
# Check prompt overlap between models in human 500
human_500_csv = os.path.join(ROOT, "research_upgrade", "tables", "human_ratings_annotator_a_500.csv")
df_h500 = pd.read_csv(human_500_csv)
print(f"Human 500 rows: {len(df_h500)}")
print(f"Human 500 models: {df_h500['model'].value_counts().to_dict()}")
prompt_overlap_h = {}
for m in df_h500['model'].unique():
    prompt_overlap_h[m] = set(df_h500[df_h500['model'] == m]['row_index'])

# Check overlap of prompts across models in human 500
m_list = list(prompt_overlap_h.keys())
print("Human 500 prompt overlap between pairs:")
for i in range(len(m_list)):
    for j in range(i+1, len(m_list)):
        inter = prompt_overlap_h[m_list[i]].intersection(prompt_overlap_h[m_list[j]])
        print(f"  {m_list[i]} vs {m_list[j]}: {len(inter)} overlapping row_indices")

# Now check benchmark 1,000 prompt overlap across models
prompt_overlap_b = {}
for m in df_mistral['model'].unique():
    prompt_overlap_b[m] = set(df_mistral[df_mistral['model'] == m]['row_index'])
print("\nBenchmark 4,000 prompt overlap between pairs:")
for i in range(len(m_list)):
    for j in range(i+1, len(m_list)):
        inter = prompt_overlap_b[m_list[i]].intersection(prompt_overlap_b[m_list[j]])
        print(f"  {m_list[i]} vs {m_list[j]}: {len(inter)} overlapping row_indices")

# 4. Human Agreement in ratings_4000.db
print("\n--- HUMAN AGREEMENT IN ratings_4000.db ---")
db_path = os.path.join(ROOT, "human_validation_app", "ratings_4000.db")
conn = sqlite3.connect(db_path)
df_ratings = pd.read_sql_query("SELECT * FROM annotations", conn)
conn.close()
print(f"Total annotations in DB: {len(df_ratings)}")
print(f"Annotators: {df_ratings['annotator_id'].value_counts().to_dict()}")

df_a = df_ratings[df_ratings["annotator_id"] == "annotator_a"].set_index("response_id")
df_b = df_ratings[df_ratings["annotator_id"] == "annotator_b"].set_index("response_id")
matched_ids = sorted(list(set(df_a.index).intersection(set(df_b.index))))
print(f"Matched response_ids in DB: {len(matched_ids)}")

sub_a = df_a.loc[matched_ids]
sub_b = df_b.loc[matched_ids]

for d in dims:
    y1 = sub_a[d].to_numpy(dtype=int)
    y2 = sub_b[d].to_numpy(dtype=int)
    exact = np.mean(y1 == y2) * 100
    close = np.mean(np.abs(y1 - y2) <= 1) * 100
    qwk = cohen_kappa_score(y1, y2, weights="quadratic")
    rho, p_val = spearmanr(y1, y2)
    
    # Ordinal Krippendorff alpha
    all_vals = np.concatenate([y1, y2])
    counts = {c: np.sum(all_vals == c) for c in range(1, 6)}
    n_tot = len(all_vals)
    delta = np.zeros((6, 6))
    for c in range(1, 6):
        for k in range(c, 6):
            if c == k:
                delta[c, k] = 0.0
            else:
                s = sum(counts[g] for g in range(c, k + 1))
                delta[c, k] = (s - (counts[c] + counts[k]) / 2.0) ** 2
            delta[k, c] = delta[c, k]
    D_o = np.mean([delta[r1, r2] for r1, r2 in zip(y1, y2)])
    D_e = 0.0
    for c in range(1, 6):
        for k in range(1, 6):
            D_e += counts[c] * counts[k] * delta[c, k]
    D_e /= (n_tot * (n_tot - 1))
    alpha = 1.0 - (D_o / D_e) if D_e > 0 else 0.0
    
    print(f"  {d:<25}: Exact = {exact:.1f}%, +/-1 = {close:.1f}%, QWK = {qwk:+.4f}, rho = {rho:+.4f}, alpha = {alpha:+.4f}")

# 5. Paired Model Comparisons on Benchmark Prompts
print("\n--- PAIRED MODEL COMPARISONS ON BENCHMARK PROMPTS (MISTRAL OVERALL) ---")
piv_m = df_mistral.pivot(index="row_index", columns="model", values="overall").dropna()
print(f"Complete prompt blocks with all 4 models: N = {len(piv_m)}")

# Friedman test
f_stat, f_p = friedmanchisquare(piv_m["HingGPT"], piv_m["Phi-3.5-mini"], piv_m["Qwen2.5-3B"], piv_m["Qwen2.5-7B"])
print(f"Friedman omnibus test: Chi2 = {f_stat:.2f}, df = 3, p = {f_p:.2e}")

pairs = [
    ("Qwen2.5-3B", "Qwen2.5-7B"),
    ("Qwen2.5-3B", "HingGPT"),
    ("Qwen2.5-3B", "Phi-3.5-mini"),
    ("Qwen2.5-7B", "HingGPT"),
    ("Qwen2.5-7B", "Phi-3.5-mini"),
    ("HingGPT", "Phi-3.5-mini")
]

raw_results = []
for m1, m2 in pairs:
    diff = piv_m[m1] - piv_m[m2]
    # Paired Wilcoxon signed-rank test
    w_stat, w_p = wilcoxon(piv_m[m1], piv_m[m2])
    # Matched rank-biserial effect size: W / (n * (n + 1) / 2)
    # or mean difference
    m_diff = diff.mean()
    sd_diff = diff.std()
    cohens_d = m_diff / sd_diff if sd_diff > 0 else 0
    raw_results.append({
        "m1": m1, "m2": m2, "mean_diff": m_diff, "wilcoxon_stat": w_stat, "raw_p": w_p, "cohens_d": cohens_d
    })

# Holm correction
raw_results.sort(key=lambda x: x["raw_p"])
m_total = len(raw_results)
print("\nPairwise Paired Wilcoxon Signed-Rank Tests (Holm Corrected):")
for idx, r in enumerate(raw_results):
    holm_multiplier = m_total - idx
    holm_p = min(1.0, r["raw_p"] * holm_multiplier)
    r["holm_p"] = holm_p
    r["significant"] = holm_p < 0.05
    print(f"  {r['m1']} vs {r['m2']}: Mean Diff = {r['mean_diff']:+.3f}, W = {r['wilcoxon_stat']:.1f}, raw p = {r['raw_p']:.2e}, Holm p = {holm_p:.2e}, Sig = {r['significant']}")

