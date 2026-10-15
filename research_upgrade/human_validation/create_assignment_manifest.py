"""
create_assignment_manifest.py
Generates the balanced, stratified, non-overlapping assignment manifest for human evaluation
of exactly 1,000 benchmark responses in HinglishEval.

Design:
- Exactly 250 responses sampled per model:
  - HingGPT: 250
  - Phi-3.5-mini: 250
  - Qwen2.5-3B: 250
  - Qwen2.5-7B: 250
- Stratified across 8 prompt categories using largest-remainder method.
- Divided equally between two independent human annotators:
  - Annotator A (Lead / User): 500 responses (125 per model)
  - Annotator B (Partner): 500 responses (125 per model)
- Overlap: strictly 0 (disjoint partition)
- Fixed Random Seed: 42
"""

import os
import sys
import json
import random
import pandas as pd
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8")

INPUT_GENERATIONS = r"outputs\controlled_1000\benchmark_generations_.csv"
INPUT_BENCHMARK = r"data\benchmarks\hinglish_bench_.csv"

OUTPUT_MANIFEST_CSV = r"research_upgrade\human_validation\assignment_manifest.csv"
OUTPUT_MANIFEST_JSON = r"research_upgrade\human_validation\assignment_manifest.json"

RANDOM_SEED = 42

def classify_prompt(text: str) -> str:
    text_lower = str(text).lower()
    words = text_lower.split()
    if any(k in text_lower for k in ['retweet', 'rt ', 'bb ', 'hashtag', '#', '@', 'follow', 'tweet', 'viral', 'post ']):
        return 'Social Media Posts'
    if any(k in text_lower for k in ['order', 'delivery', 'refund', 'service', 'customer', 'support', 'complaint', 'account', 'issue', 'helpdesk']):
        return 'Customer Support Dialogues'
    if any(k in text_lower for k in ['review', 'flipkart', 'amazon', 'product', 'camera', 'battery', 'price', 'quality', 'purchase', 'worth']):
        return 'Product Reviews'
    if any(k in text_lower for k in ['news', 'govt', 'government', 'minister', 'police', 'election', 'covid', 'vaccine', 'corona', 'modi', 'bjp', 'congress', 'pakistan']):
        return 'News & Explainers'
    if any(k in text_lower for k in ['story', 'kahaani', 'ek baar', 'jab main', 'bachpan', 'incident', 'hua tha', 'tabhi']):
        return 'Storytelling'
    if len(words) <= 7 or any(k in text_lower for k in ['shayari', 'quote', 'caption', 'attitude', 'vibe']):
        return 'Captions & One-liners'
    if any(k in text_lower for k in ['advice', 'opinion', 'suggest', 'kya karu', 'kya kare', 'soch', 'lagta hai', 'socho', 'batao', 'recommend']):
        return 'Advice & Opinions'
    return 'Casual Conversation'

def generate_manifest():
    print("=" * 80)
    print("GENERATING STRATIFIED 1,000-RESPONSE HUMAN EVALUATION ASSIGNMENT MANIFEST")
    print(f"Random Seed: {RANDOM_SEED}")
    print("=" * 80)

    # 1. Load source generations
    if not os.path.exists(INPUT_GENERATIONS):
        raise FileNotFoundError(f"Missing generations file: {INPUT_GENERATIONS}")
    df_gen = pd.read_csv(INPUT_GENERATIONS)
    print(f"Loaded {len(df_gen)} responses from {INPUT_GENERATIONS}")

    # 2. Load benchmark prompts and classify categories
    source_texts = {}
    categories = {}
    if os.path.exists(INPUT_BENCHMARK):
        df_bench = pd.read_csv(INPUT_BENCHMARK)
        for i, r in df_bench.iterrows():
            source_text = str(r.get("source_text", ""))
            source_texts[i] = source_text
            categories[i] = classify_prompt(source_text)

    # Compute category quotas for 250 items per model using largest-remainder method
    cat_counts = pd.Series(categories).value_counts()
    print("\nBenchmark prompt category distribution across all 1,000 prompts:")
    for cat, count in cat_counts.items():
        print(f"  - {cat}: {count} ({count/10.0:.1f}%)")

    target_per_model = 250
    quotas = {}
    remainders = {}
    for cat, count in cat_counts.items():
        exact_q = count * target_per_model / 1000.0
        quotas[cat] = int(exact_q)
        remainders[cat] = exact_q - int(exact_q)

    shortage = target_per_model - sum(quotas.values())
    for cat, _ in sorted(remainders.items(), key=lambda x: x[1], reverse=True)[:shortage]:
        quotas[cat] += 1

    print(f"\nStratified sampling quota per model ({target_per_model} total):")
    for cat, q in quotas.items():
        print(f"  - {cat}: {q} samples")

    models = sorted(df_gen["model"].unique().tolist())
    print(f"\nModels to sample ({len(models)}): {models}")

    annotator_a_assignments = []
    annotator_b_assignments = []

    for m_idx, model in enumerate(models):
        sub_df = df_gen[df_gen["model"] == model].copy()
        sub_df["category"] = sub_df["row_index"].map(categories)

        # Stratified sample 250 items for this model
        rng = random.Random(RANDOM_SEED + m_idx * 31)
        model_sampled_indices = []

        cat_groups = defaultdict(list)
        for idx, r in sub_df.iterrows():
            cat_groups[r["category"]].append(idx)

        for cat, q in quotas.items():
            pool = cat_groups[cat]
            rng.shuffle(pool)
            chosen = pool[:q]
            model_sampled_indices.extend(chosen)

        assert len(model_sampled_indices) == 250, f"Expected 250 samples for {model}, got {len(model_sampled_indices)}"

        # Now partition the 250 items for this model equally between Annotator A (125) and Annotator B (125)
        # Stratify the split within categories to preserve category balance per annotator
        rng_split = random.Random(RANDOM_SEED + m_idx * 13 + 7)
        a_indices = []
        b_indices = []

        # Group sampled indices by category
        sampled_by_cat = defaultdict(list)
        for idx in model_sampled_indices:
            cat = sub_df.loc[idx, "category"]
            sampled_by_cat[cat].append(idx)

        # Distribute items between A and B
        turn = 0
        for cat in sorted(sampled_by_cat.keys()):
            cat_idxs = sampled_by_cat[cat]
            rng_split.shuffle(cat_idxs)
            for idx in cat_idxs:
                if turn % 2 == 0:
                    a_indices.append(idx)
                else:
                    b_indices.append(idx)
                turn += 1

        # Balancing check
        while len(a_indices) > 125:
            b_indices.append(a_indices.pop())
        while len(b_indices) > 125:
            a_indices.append(b_indices.pop())

        assert len(a_indices) == 125, f"Annotator A must have 125 items for {model}"
        assert len(b_indices) == 125, f"Annotator B must have 125 items for {model}"

        for idx in a_indices:
            row = sub_df.loc[idx]
            row_idx = int(row["row_index"])
            annotator_a_assignments.append({
                "annotator_id": "annotator_a",
                "response_id": f"RESP_{model}_{row_idx:04d}",
                "global_row_index": int(idx),
                "row_index": row_idx,
                "prompt_id": row_idx + 1,
                "model": model,
                "category": categories.get(row_idx, "Casual Conversation"),
                "prompt": str(row["prompt"]),
                "response": str(row["response"]),
                "source_text": source_texts.get(row_idx, "")
            })

        for idx in b_indices:
            row = sub_df.loc[idx]
            row_idx = int(row["row_index"])
            annotator_b_assignments.append({
                "annotator_id": "annotator_b",
                "response_id": f"RESP_{model}_{row_idx:04d}",
                "global_row_index": int(idx),
                "row_index": row_idx,
                "prompt_id": row_idx + 1,
                "model": model,
                "category": categories.get(row_idx, "Casual Conversation"),
                "prompt": str(row["prompt"]),
                "response": str(row["response"]),
                "source_text": source_texts.get(row_idx, "")
            })

    # Shuffle presentation order per annotator to prevent model/category clustering
    rng_a = random.Random(101)
    rng_a.shuffle(annotator_a_assignments)
    for i, item in enumerate(annotator_a_assignments, start=1):
        item["assignment_id"] = f"A_{i:04d}"
        item["item_index"] = i

    rng_b = random.Random(202)
    rng_b.shuffle(annotator_b_assignments)
    for i, item in enumerate(annotator_b_assignments, start=1):
        item["assignment_id"] = f"B_{i:04d}"
        item["item_index"] = i

    all_assignments = annotator_a_assignments + annotator_b_assignments
    manifest_df = pd.DataFrame(all_assignments)

    # 3. Verification & Checks
    set_a = {x["response_id"] for x in annotator_a_assignments}
    set_b = {x["response_id"] for x in annotator_b_assignments}
    overlap = set_a.intersection(set_b)
    union_set = set_a.union(set_b)

    print("\n--- ASSIGNMENT MANIFEST VERIFICATION ---")
    print(f"Total Sampled Responses: {len(all_assignments)} (Target: 1,000)")
    print(f"Annotator A Assignments: {len(annotator_a_assignments)} (Target: 500)")
    print(f"Annotator B Assignments: {len(annotator_b_assignments)} (Target: 500)")
    print(f"Assignment Overlap: {len(overlap)} (Target: 0)")
    print(f"Unique Source Responses: {len(union_set)} (Target: 1,000)")

    assert len(all_assignments) == 1000, "Manifest must contain exactly 1,000 responses"
    assert len(annotator_a_assignments) == 500, "Annotator A must have exactly 500 responses"
    assert len(annotator_b_assignments) == 500, "Annotator B must have exactly 500 responses"
    assert len(overlap) == 0, "Assignment overlap must be strictly 0"
    assert len(union_set) == 1000, "Union must cover all 1,000 unique responses"

    # Verify per-model balance
    a_df = pd.DataFrame(annotator_a_assignments)
    b_df = pd.DataFrame(annotator_b_assignments)

    print("\nModel counts for Annotator A (500 total):")
    print(a_df["model"].value_counts().to_dict())
    print("Model counts for Annotator B (500 total):")
    print(b_df["model"].value_counts().to_dict())

    for m in models:
        assert (a_df["model"] == m).sum() == 125, f"Annotator A must have 125 of {m}"
        assert (b_df["model"] == m).sum() == 125, f"Annotator B must have 125 of {m}"
        assert (manifest_df["model"] == m).sum() == 250, f"Combined manifest must have 250 of {m}"

    print("\nCategory distribution for Annotator A:")
    print(a_df["category"].value_counts().to_dict())
    print("Category distribution for Annotator B:")
    print(b_df["category"].value_counts().to_dict())

    # 4. Save manifest files
    os.makedirs(os.path.dirname(OUTPUT_MANIFEST_CSV), exist_ok=True)
    manifest_df.to_csv(OUTPUT_MANIFEST_CSV, index=False, encoding="utf-8")
    print(f"\nSaved CSV manifest: {OUTPUT_MANIFEST_CSV} ({len(manifest_df)} rows)")

    with open(OUTPUT_MANIFEST_JSON, "w", encoding="utf-8") as f:
        json.dump(all_assignments, f, indent=2, ensure_ascii=False)
    print(f"Saved JSON manifest: {OUTPUT_MANIFEST_JSON}")

    print("\n[SUCCESS] Stratified 1,000-response manifest generated and verified.")

if __name__ == "__main__":
    generate_manifest()
