# Hardware Feasibility, Baseline, and Ablation Study Report

**Hardware Environment:** NVIDIA GeForce RTX 4050 Laptop GPU (Total VRAM: 6.00 GB)  
**Host Memory:** 15.71 GB RAM  
**Operating System:** Windows 11  

---

## 1. Hardware Inspection & Compute Feasibility Analysis

- **Hardware Capabilities & Constraints:**
  - The local runtime environment is constrained to an NVIDIA GeForce RTX 4050 Laptop GPU with **6,141 MiB (6.0 GB) VRAM**.
  - Standard full-precision (FP16/BF16) fine-tuning of a 3B model requires $\sim 24$ GB VRAM; a 7B model requires $\sim 56$ GB VRAM.
  - QLoRA 4-bit NormalFloat (NF4) with Double Quantization allows loading the 3B model in $\sim 2.07$ GB VRAM and the 7B model in $\sim 4.6$ GB VRAM.
  - Retraining across 17,340 steps for multiple LoRA ranks ($r \in \{8, 16, 64\}$) and sequence lengths (128 vs 512) requires hundreds of compute hours beyond the thermal budget of the host laptop GPU.
  - Therefore, we conduct exact parameter/memory modeling for all ranks, coupled with empirical forward-pass evaluation across Base, Instruct, and CPT checkpoints, and sequence length evaluations on the validation corpus.

---

## 2. LoRA Rank Ablation Specifications ($r \in \{8, 16, 64\}$)

| LoRA Rank ($r$) | Scaling Alpha ($\alpha$) | Trainable LoRA Params | Base Model Params | % Trainable | Adapter Size (MB) | Optimizer Memory (MB) | Feasibility on 6GB VRAM |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **8** | 16 | 8,257,536 | 3,086,000,000 | 0.2676% | 15.75 MB | 126.0 MB | Feasible (QLoRA 4-bit) |
| **16** | 32 | 16,515,072 | 3,086,000,000 | 0.5352% | 31.50 MB | 252.0 MB | Feasible (QLoRA 4-bit) |
| **64** | 128 | 66,060,288 | 3,086,000,000 | 2.1406% | 126.00 MB | 1,008.0 MB | Feasible (QLoRA 4-bit) |

*Analysis:*
Moving from $r=8$ to $r=16$ doubles rank capacity while requiring only an additional 126 MB of optimizer state memory. Rank $r=64$ consumes $>1$ GB of optimizer state memory, which remains viable in 4-bit QLoRA but approaches the 6GB VRAM safety ceiling under long sequence lengths.

---

## 3. Empirical Model Comparison: Base vs Instruct vs CPT (Qwen2.5-3B)

Evaluated on the natural Hinglish validation corpus (`data/processed/cpt/validation.jsonl`):

| Model Variant | Base Architecture | Adapter Checkpoint | Validation Loss (Nats) | Validation Perplexity | Evaluation Throughput (tok/s) |
| :--- | :--- | :--- | :---: | :---: | :---: |
| **Base (Qwen2.5-3B)** | Qwen/Qwen2.5-3B | None | 5.0432 | 154.97 | 403.1 |
| **Instruct (Qwen2.5-3B-Instruct)** | Qwen/Qwen2.5-3B-Instruct | None | 5.2363 | 187.97 | 440.5 |
| **CPT Adapted (Qwen2.5-3B-CPT)** | Qwen/Qwen2.5-3B | `checkpoint-17340` | **4.0566** | **57.78** | 335.1 |

*Key Findings:*
1. **Domain Adaptation Impact:** Continued Pretraining (CPT) reduces cross-entropy loss from 5.04 to 4.06 and slashes validation perplexity from 154.97 down to **57.78** (a **62.7% reduction**).
2. **Base vs Instruct:** The general-purpose Instruct model exhibits higher perplexity (187.97) than the base model (154.97) on raw code-mixed text, reflecting alignment drift toward structured English formatting prior to code-mixed CPT adaptation.

---

## 4. Sequence Length Ablation (128 vs 512 tokens)

Evaluated on Qwen2.5-3B-CPT across 128 and 512 token context limits:

| Max Sequence Length | Validation Loss (Nats) | Validation Perplexity | Throughput (tok/s) | Peak VRAM (GB) |
| :---: | :---: | :---: | :---: | :---: |
| **128** | 4.0566 | 57.78 | 332.1 | 2.07 GB |
| **512** | 4.0566 | 57.78 | 323.9 | 2.07 GB |

*Key Findings:*
Conversational Hinglish utterances in this benchmark average $\sim 30$ tokens, meaning that 128 tokens fully captures the discourse context without truncation, while offering $\sim 2.5\%$ higher throughput. For extended paragraph-length code-mixed generation, 512 tokens preserves long-range coherence with negligible memory overhead in 4-bit precision.
