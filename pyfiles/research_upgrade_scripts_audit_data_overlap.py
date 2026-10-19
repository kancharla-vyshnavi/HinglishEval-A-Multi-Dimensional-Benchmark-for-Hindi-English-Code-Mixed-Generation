import os
import sys
import json
import csv
import re
import time
from collections import defaultdict

TRAIN_PATH = r"C:\Users\vyshu\Downloads\train.jsonl"
VAL_PATH = r"data\processed\cpt\validation.jsonl"
BENCHMARK_PATH = r"data\benchmarks\hinglish_bench_.csv"

OUTPUT_REPORT = r"research_upgrade\reports\data_leakage_overlap_report.md"
OUTPUT_MATCHES_CSV = r"research_upgrade\tables\benchmark_train_overlap_matches.csv"

def normalize_text(text):
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def get_tokens(text):
    norm = normalize_text(text)
    return frozenset(norm.split())

def jaccard_similarity(set1, set2):
    if not set1 or not set2:
        return 0.0
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union if union > 0 else 0.0

def main():
    start_time = time.time()
    print("=" * 80, flush=True)
    print("AUDIT: BENCHMARK (1,000) VS TRAINING SAMPLES (277,431)", flush=True)
    print("=" * 80, flush=True)

    # 1. Load benchmark
    print(f"Loading benchmark from: {BENCHMARK_PATH}", flush=True)
    bench_rows = []
    with open(BENCHMARK_PATH, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for r in reader:
            bench_rows.append({
                "prompt_id": r["prompt_id"],
                "row_index": r["row_index"],
                "source_text": r["source_text"].strip(),
                "norm_text": normalize_text(r["source_text"]),
                "tokens": get_tokens(r["source_text"]),
                "n_tokens": len(get_tokens(r["source_text"]))
            })
    print(f"Loaded {len(bench_rows)} benchmark prompts.", flush=True)

    # Build lookup dicts
    exact_bench = {b["source_text"]: b for b in bench_rows}
    casefold_bench = {b["source_text"].lower(): b for b in bench_rows}
    norm_bench = {b["norm_text"]: b for b in bench_rows if b["norm_text"]}

    # Group benchmark prompts by token length for ultra-fast near-dup candidate filtering
    bench_by_len = defaultdict(list)
    for b in bench_rows:
        bench_by_len[b["n_tokens"]].append(b)

    # 2. Stream through train.jsonl
    print(f"\nStreaming through training dataset: {TRAIN_PATH}", flush=True)
    train_count = 0
    exact_matches = []
    casefold_matches = []
    norm_matches = []
    near_dup_matches_90 = []
    near_dup_matches_80 = []

    seen_near_pairs = set()

    with open(TRAIN_PATH, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            train_count += 1
            if train_count % 50000 == 0:
                print(f"Processed {train_count:,} / 277,431 training lines ({time.time() - start_time:.1f}s)...", flush=True)
            
            try:
                item = json.loads(line)
            except Exception:
                continue

            train_text = (item.get("text") or item.get("utterance") or item.get("source_text") or "").strip()
            if not train_text:
                continue

            # 1. Exact match
            if train_text in exact_bench:
                b = exact_bench[train_text]
                exact_matches.append({
                    "type": "exact_match",
                    "prompt_id": b["prompt_id"],
                    "bench_row_index": b["row_index"],
                    "train_index": idx,
                    "bench_text": b["source_text"],
                    "train_text": train_text,
                    "similarity": 1.0
                })

            # 2. Casefold match
            train_lower = train_text.lower()
            if train_lower in casefold_bench:
                b = casefold_bench[train_lower]
                if train_text not in exact_bench:
                    casefold_matches.append({
                        "type": "case_insensitive_match",
                        "prompt_id": b["prompt_id"],
                        "bench_row_index": b["row_index"],
                        "train_index": idx,
                        "bench_text": b["source_text"],
                        "train_text": train_text,
                        "similarity": 1.0
                    })

            # 3. Normalized match
            train_norm = normalize_text(train_text)
            if train_norm in norm_bench:
                b = norm_bench[train_norm]
                if train_lower not in casefold_bench:
                    norm_matches.append({
                        "type": "normalized_match",
                        "prompt_id": b["prompt_id"],
                        "bench_row_index": b["row_index"],
                        "train_index": idx,
                        "bench_text": b["source_text"],
                        "train_text": train_text,
                        "similarity": 1.0
                    })

            # 4. Near-duplicate matching with length-pruned candidates
            # For Jaccard >= 0.8, |A| and |B| must satisfy min(|A|,|B|) / max(|A|,|B|) >= 0.8
            train_tokens = get_tokens(train_text)
            n_t = len(train_tokens)
            if n_t >= 4:
                min_b_len = int(n_t * 0.8)
                max_b_len = int(n_t / 0.8) + 1
                for b_len in range(min_b_len, max_b_len + 1):
                    for b in bench_by_len.get(b_len, []):
                        if train_norm == b["norm_text"]:
                            continue  # already captured in exact/norm
                        jacc = jaccard_similarity(train_tokens, b["tokens"])
                        if jacc >= 0.80:
                            pair_key = (b["prompt_id"], idx)
                            if pair_key not in seen_near_pairs:
                                seen_near_pairs.add(pair_key)
                                entry = {
                                    "type": "near_duplicate_jaccard_>=0.8",
                                    "prompt_id": b["prompt_id"],
                                    "bench_row_index": b["row_index"],
                                    "train_index": idx,
                                    "bench_text": b["source_text"],
                                    "train_text": train_text,
                                    "similarity": round(jacc, 4)
                                }
                                if jacc >= 0.90:
                                    near_dup_matches_90.append(entry)
                                else:
                                    near_dup_matches_80.append(entry)

    elapsed = time.time() - start_time
    print(f"\nCompleted audit in {elapsed:.2f} seconds.", flush=True)
    print(f"Total training samples scanned: {train_count:,}", flush=True)
    print(f"Exact string matches: {len(exact_matches)}", flush=True)
    print(f"Case-insensitive matches (additional): {len(casefold_matches)}", flush=True)
    print(f"Normalized alphanumeric matches (additional): {len(norm_matches)}", flush=True)
    print(f"Near-duplicates (Jaccard >= 0.90): {len(near_dup_matches_90)}", flush=True)
    print(f"Near-duplicates (0.80 <= Jaccard < 0.90): {len(near_dup_matches_80)}", flush=True)

    all_matches = exact_matches + casefold_matches + norm_matches + near_dup_matches_90 + near_dup_matches_80

    affected_exact = set(m["prompt_id"] for m in exact_matches)
    affected_casefold = set(m["prompt_id"] for m in exact_matches + casefold_matches)
    affected_norm = set(m["prompt_id"] for m in exact_matches + casefold_matches + norm_matches)
    affected_all = set(m["prompt_id"] for m in all_matches)

    print(f"\nUnique benchmark prompts with exact match: {len(affected_exact)} / 1,000 ({len(affected_exact)/10:.1f}%)", flush=True)
    print(f"Unique benchmark prompts with case-insensitive match: {len(affected_casefold)} / 1,000 ({len(affected_casefold)/10:.1f}%)", flush=True)
    print(f"Unique benchmark prompts with normalized match: {len(affected_norm)} / 1,000 ({len(affected_norm)/10:.1f}%)", flush=True)
    print(f"Unique benchmark prompts with near-duplicate (>=0.8 Jaccard): {len(affected_all)} / 1,000 ({len(affected_all)/10:.1f}%)", flush=True)

    # Save to CSV
    os.makedirs(os.path.dirname(OUTPUT_MATCHES_CSV), exist_ok=True)
    with open(OUTPUT_MATCHES_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "type", "prompt_id", "bench_row_index", "train_index", "similarity", "bench_text", "train_text"
        ])
        writer.writeheader()
        for m in all_matches:
            writer.writerow(m)
    print(f"Saved match details to: {OUTPUT_MATCHES_CSV}", flush=True)

    # Generate Markdown Report
    os.makedirs(os.path.dirname(OUTPUT_REPORT), exist_ok=True)
    report = f"""# Benchmark vs Training Set Overlap Audit Report

**Audit Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}  
**Evaluated Training File:** `{TRAIN_PATH}` ({train_count:,} sequences)  
**Evaluated Benchmark File:** `{BENCHMARK_PATH}` (1,000 prompts)  
**Audit Wallclock Time:** {elapsed:.2f} seconds  

---

## 1. Executive Summary

| Category | Overlap Count (Train Rows) | Unique Benchmark Prompts Affected | % of Benchmark |
| :--- | :--- | :--- | :--- |
| **Exact Matches (Identical String)** | **{len(exact_matches)}** | **{len(affected_exact)}** | **{len(affected_exact)/10:.2f}%** |
| **Case-Insensitive Exact Matches (New)** | **{len(casefold_matches)}** | **{len(affected_casefold) - len(affected_exact)}** | **{(len(affected_casefold)-len(affected_exact))/10:.2f}%** |
| **Normalized Text Matches (New)** | **{len(norm_matches)}** | **{len(affected_norm) - len(affected_casefold)}** | **{(len(affected_norm)-len(affected_casefold))/10:.2f}%** |
| **High Near-Duplicates (Token Jaccard $\\ge 0.90$)** | **{len(near_dup_matches_90)}** | **{len(set(m['prompt_id'] for m in near_dup_matches_90) - affected_norm)}** | **{len(set(m['prompt_id'] for m in near_dup_matches_90) - affected_norm)/10:.2f}%** |
| **Moderate Near-Duplicates ($0.80 \\le \\text{{Jaccard}} < 0.90$)** | **{len(near_dup_matches_80)}** | **{len(set(m['prompt_id'] for m in near_dup_matches_80) - affected_norm)}** | **{len(set(m['prompt_id'] for m in near_dup_matches_80) - affected_norm)/10:.2f}%** |
| **Total Distinct Benchmark Prompts Affected** | **{len(all_matches)}** | **{len(affected_all)}** | **{len(affected_all)/10:.2f}%** |

---

## 2. Leakage and Contamination Analysis

1. **Validation & Benchmark Integrity:**
   - The original paper stated that the 1,000 benchmark prompts were sampled from `data/processed/cpt/validation.jsonl` (14,601 entries) under the assumption that the training corpus of 277,431 sequences was strictly disjoint.
   - The empirical audit demonstrates that **{len(affected_exact)}** prompts ({len(affected_exact)/10:.2f}%) have exact textual duplicates in the training set, and **{len(affected_norm)}** prompts ({len(affected_norm)/10:.2f}%) have normalized alphanumeric matches.
   - For publication quality, this exact overlap count must be reported in the paper and benchmark specification.
   - Original data files are strictly preserved without modification.

---

## 3. Representative Overlap Instances

"""
    for i, m in enumerate(all_matches[:15], 1):
        report += f"### Example {i}: {m['type']} (Benchmark Prompt ID: {m['prompt_id']}, Train Line: {m['train_index']})\n"
        report += f"- **Benchmark Utterance:** `{m['bench_text']}`\n"
        report += f"- **Training Utterance:** `{m['train_text']}`\n"
        report += f"- **Similarity Score:** {m['similarity']}\n\n"

    with open(OUTPUT_REPORT, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"Saved markdown report to: {OUTPUT_REPORT}", flush=True)

if __name__ == "__main__":
    main()
