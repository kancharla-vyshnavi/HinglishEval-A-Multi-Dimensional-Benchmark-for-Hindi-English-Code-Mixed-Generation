import os
import sys
import json
import csv
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

BENCHMARK_PATH = r"outputs\controlled_1000\benchmark_generations_.csv"
JSONL_PATH = r"research_upgrade\tables\judge_qwen25_3b_4000_results.jsonl"
CSV_PATH = r"research_upgrade\tables\judge_qwen25_3b_4000_results.csv"

def main():
    print("=" * 80)
    print("VERIFICATION SCRIPT: QWEN JUDGE EXECUTION STATUS & DATA INTEGRITY AUDIT")
    print("=" * 80)

    # 1. Benchmark check
    bench_df = pd.read_csv(BENCHMARK_PATH)
    total_expected = len(bench_df)
    print(f"Expected Total Benchmark Records: {total_expected}")
    expected_keys = set((int(r["row_index"]), str(r["model"])) for _, r in bench_df.iterrows())

    # 2. JSONL Check
    jsonl_records = []
    jsonl_keys = []
    jsonl_duplicates = 0
    seen_keys = set()
    invalid_judgments = 0
    valid_judgments = 0
    failed_parses = 0

    if os.path.exists(JSONL_PATH):
        with open(JSONL_PATH, "r", encoding="utf-8") as f:
            for line_no, line in enumerate(f):
                line = line.strip()
                if not line:
                    continue
                try:
                    item = json.loads(line)
                    key = (int(item["row_index"]), str(item["model"]))
                    if key in seen_keys:
                        jsonl_duplicates += 1
                    else:
                        seen_keys.add(key)
                        jsonl_keys.append(key)
                        jsonl_records.append(item)
                    
                    is_valid = item.get("is_valid", False)
                    scores = [item.get(d) for d in ["fluency", "code_mixing_naturalness", "hindi_grammar", "prompt_adherence", "spelling_consistency", "overall"]]
                    
                    if is_valid and all(s is not None and 1 <= int(s) <= 5 for s in scores):
                        valid_judgments += 1
                    else:
                        invalid_judgments += 1
                except Exception as e:
                    failed_parses += 1
    
    total_completed = len(jsonl_records)
    initial_checkpoint_records = 256
    records_completed_in_this_run = max(0, total_completed - initial_checkpoint_records)
    remaining_records = total_expected - total_completed

    print(f"\n--- RECORD COUNTS ---")
    print(f"Total Expected Records          : {total_expected}")
    print(f"Initial Checkpoint Records      : {initial_checkpoint_records}")
    print(f"Records Completed in This Run   : {records_completed_in_this_run}")
    print(f"Total Completed Records So Far  : {total_completed} / {total_expected} ({total_completed/total_expected*100:.2f}%)")
    print(f"Total Valid Records Across Runs : {valid_judgments}")
    print(f"Invalid / Malformed Judgments   : {invalid_judgments}")
    print(f"Failed JSON Parses in Log       : {failed_parses}")
    print(f"Duplicate Record Keys in JSONL  : {jsonl_duplicates}")
    print(f"Missing Records (Remaining)     : {remaining_records}")

    # 3. Model breakdown
    model_counts = {}
    for it in jsonl_records:
        m = it.get("model", "unknown")
        model_counts[m] = model_counts.get(m, 0) + 1
    print(f"\n--- MODEL BREAKDOWN OF COMPLETED RECORDS ---")
    for m in ["HingGPT", "Phi-3.5-mini", "Qwen2.5-3B", "Qwen2.5-7B"]:
        print(f"  {m:<15}: {model_counts.get(m, 0):>5} / 1,000")

    # 4. Check CSV Checkpoint synchronization
    csv_records = 0
    if os.path.exists(CSV_PATH):
        try:
            csv_df = pd.read_csv(CSV_PATH)
            csv_records = len(csv_df)
        except Exception:
            csv_records = 0
    print(f"\n--- CHECKPOINT SYNCHRONIZATION ---")
    print(f"JSONL Records On Disk           : {total_completed}")
    print(f"CSV Records On Disk             : {csv_records}")

    # Synchronize CSV with full JSONL if CSV has fewer
    if total_completed > csv_records and jsonl_records:
        pd.DataFrame(jsonl_records).to_csv(CSV_PATH, index=False)
        print(f"Synchronized CSV Checkpoint     : Updated {CSV_PATH} to {total_completed} rows.")

    # 5. Check integrity against benchmark
    missing_keys = expected_keys - seen_keys
    print(f"\n--- BENCHMARK JOIN INTEGRITY ---")
    print(f"Matched Benchmark Prompts       : {len(seen_keys.intersection(expected_keys))}")
    print(f"Orphan / Unexpected Keys        : {len(seen_keys - expected_keys)}")
    print(f"Remaining Missing Benchmark Keys: {len(missing_keys)}")

    # 6. Overall Status
    is_complete = (remaining_records == 0)
    print(f"\n--- STATUS VERDICT ---")
    print(f"Execution State                 : {'COMPLETE' if is_complete else 'INCOMPLETE / IN PROGRESS'}")
    if not is_complete:
        print(f"Exact Remaining Count           : {remaining_records} records")
        print(f"Safe Resume Command             : .\\.venv311\\Scripts\\python.exe research_upgrade\\scripts\\run_qwen_judge_evaluation.py")

if __name__ == "__main__":
    main()
