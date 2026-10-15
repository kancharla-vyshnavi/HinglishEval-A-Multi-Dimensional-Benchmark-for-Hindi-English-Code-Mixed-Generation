import sys
import json
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

df_gen = pd.read_csv("outputs/controlled_1000/benchmark_generations_.csv")
df_bench = pd.read_csv("data/benchmarks/hinglish_bench_.csv")

# Select 5 diverse, genuine prompts across different lengths and styles
# Prompts:
# 1. Conversational question / chat (pid 10)
# 2. Emotional expression / reflection (pid 120)
# 3. Cultural / festival comment (pid 250)
# 4. Everyday query (pid 500)
# 5. Colloquial observation (pid 750)
selected_pids = [10, 120, 250, 500, 750]
examples = []

for pid in selected_pids:
    bench_idx = pid - 1
    brow = df_bench.iloc[bench_idx]
    ex = {
        "prompt_id": pid,
        "benchmark_index": bench_idx,
        "source_corpus_row": int(brow["row_index"]),
        "source_text": str(brow["source_text"]),
        "generations": {}
    }
    for m in ["HingGPT", "Phi-3.5-mini", "Qwen2.5-3B", "Qwen2.5-7B"]:
        grow = df_gen[(df_gen["row_index"] == bench_idx) & (df_gen["model"] == m)]
        resp = str(grow["response"].iloc[0]) if len(grow) else "N/A"
        ex["generations"][m] = resp
    examples.append(ex)

with open(r"research_upgrade\tables\five_genuine_examples.json", "w", encoding="utf-8") as f:
    json.dump(examples, f, indent=2, ensure_ascii=False)

print("Saved five genuine examples to research_upgrade/tables/five_genuine_examples.json")
for ex in examples:
    print(f"\n=======================================================")
    print(f"[Prompt ID {ex['prompt_id']} | Source Corpus Index {ex['source_corpus_row']}]:")
    print(f"Utterance: \"{ex['source_text']}\"")
    print("-------------------------------------------------------")
    for m, g in ex["generations"].items():
        print(f"[{m}]:\n  {g}\n")
