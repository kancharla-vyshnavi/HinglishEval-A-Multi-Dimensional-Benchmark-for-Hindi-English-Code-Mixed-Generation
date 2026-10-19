import sys
import os
import re
import json
import torch
import pandas as pd
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

sys.stdout.reconfigure(encoding="utf-8")

JUDGE_MODEL_ID = "Qwen/Qwen2.5-3B-Instruct"

FEW_SHOT_PROMPT = """You are an expert bilingual linguistic judge evaluating Hindi-English code-mixed (Hinglish) conversational text generation.

Rate the MODEL RESPONSE to the USER PROMPT on a 1 to 5 scale across six dimensions:
1. fluency (1 = completely disjointed/broken, 5 = smooth, highly articulate flow)
2. code_mixing_naturalness (1 = awkward word-for-word substitution, 5 = authentic, native conversational code-switching)
3. hindi_grammar (1 = broken inflections/gender-number mismatch, 5 = flawless Hindi morphosyntax)
4. prompt_adherence (1 = off-topic, refusal, or crash traceback, 5 = perfectly addresses the utterance)
5. spelling_consistency (1 = erratic phonetic chaos, 5 = standard, readable Romanized Hindi transliteration)
6. overall (1 = very poor, 5 = exceptional)

--- FEW-SHOT CALIBRATION ANCHORS ---
Anchor 1 (Severe Degradation / Crash / Disjointed):
USER PROMPT: "bhai kal shaam ko milte hain cafe pe"
MODEL RESPONSE: "[GENERATION_ERROR] AttributeError: 'NoneType' object has no attribute 'shape' or ...."
OUTPUT: {"fluency": 1, "code_mixing_naturalness": 1, "hindi_grammar": 1, "prompt_adherence": 1, "spelling_consistency": 1, "overall": 1}

Anchor 2 (High Quality / Natural Hinglish):
USER PROMPT: "bhai kal shaam ko milte hain cafe pe"
MODEL RESPONSE: "Haan bilkul bhai! Shaam ko 6 baje done karte hain, wahi milte hain coffee pe."
OUTPUT: {"fluency": 5, "code_mixing_naturalness": 5, "hindi_grammar": 5, "prompt_adherence": 5, "spelling_consistency": 5, "overall": 5}

Anchor 3 (Grammar & Boundary Glitch):
USER PROMPT: "kya tum meri help kar sakte ho assignment me?"
MODEL RESPONSE: "main help the you in assignment karegi kal morning."
OUTPUT: {"fluency": 2, "code_mixing_naturalness": 1, "hindi_grammar": 2, "prompt_adherence": 3, "spelling_consistency": 4, "overall": 2}

Anchor 4 (Good Fluency but Weak Code-Mixing / Pure English):
USER PROMPT: "movie kaisi lagi tujhe kal raat?"
MODEL RESPONSE: "It was an amazing movie with great direction and stunning acting."
OUTPUT: {"fluency": 5, "code_mixing_naturalness": 1, "hindi_grammar": 1, "prompt_adherence": 4, "spelling_consistency": 5, "overall": 3}
-------------------------------------

Respond ONLY with a valid JSON object matching this schema:
{"fluency": <1-5>, "code_mixing_naturalness": <1-5>, "hindi_grammar": <1-5>, "prompt_adherence": <1-5>, "spelling_consistency": <1-5>, "overall": <1-5>}
"""

def extract_json(raw_text):
    match = re.search(r"\{[^{}]*\}", raw_text)
    if not match:
        return None
    try:
        data = json.loads(match.group(0))
        scores = {}
        for dim in ["fluency", "code_mixing_naturalness", "hindi_grammar", "prompt_adherence", "spelling_consistency", "overall"]:
            val = int(data[dim])
            if val < 1 or val > 5:
                return None
            scores[dim] = val
        return scores
    except Exception:
        return None

def main():
    print("Loading test batch from benchmark...")
    df = pd.read_csv(r"outputs\controlled_1000\benchmark_generations_.csv").head(5)
    
    bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.float16)
    tok = AutoTokenizer.from_pretrained(JUDGE_MODEL_ID, padding_side="left")
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    
    model = AutoModelForCausalLM.from_pretrained(JUDGE_MODEL_ID, quantization_config=bnb, device_map="cuda:0")

    print("\nRunning inference on 5 test samples...")
    for idx, row in df.iterrows():
        user_prompt = row["prompt"]
        model_resp = row["response"]
        
        messages = [
            {"role": "system", "content": FEW_SHOT_PROMPT},
            {"role": "user", "content": f"USER PROMPT:\n{user_prompt}\n\nMODEL RESPONSE:\n{model_resp}\n\nJSON EVALUATION:"}
        ]
        
        prompt_text = tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = tok(prompt_text, return_tensors="pt").to("cuda:0")
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=64,
                do_sample=False,
                pad_token_id=tok.pad_token_id
            )
        
        gen_text = tok.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
        scores = extract_json(gen_text)
        print(f"\nSample {idx} ({row['model']}):")
        print("Raw output:", gen_text.strip())
        print("Parsed scores:", scores)

if __name__ == "__main__":
    main()
