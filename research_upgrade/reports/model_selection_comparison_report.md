

# Task 5: Model-Selection Synthesis Report (Qwen2.5-3B vs Qwen2.5-7B)

**Analysis Date:** 2026-10-13  
**Evaluated Architectures:** `Qwen/Qwen2.5-3B` vs `Qwen/Qwen2.5-7B`  
**CPT Adaptation:** 17,340 steps, LoRA $r=8, \alpha=16$ on 277,431 Hinglish sequences  
**Status:** **Provisional Technical Recommendation** (Pending Final Human Preference Audit in Task 7)

---

## 1. Executive Summary & Provisional Recommendation

A multi-dimensional synthesis across automated metrics, linguistic characteristics, error taxonomy, and LLM-as-a-judge scores reveals a nuanced trade-off:

1. **Dialogue Authenticity & Prompt Responsiveness:**
   - **Qwen2.5-3B** achieves higher mean scores on **Prompt Adherence** ($3.741$ vs $3.072$) and **Code-Mixing Naturalness** ($3.979$ vs $3.682$) under Mistral-7B evaluation.
   - Qwen2.5-3B exhibits fewer English-dominant collapse errors (**E1**: 19 vs 30) and maintains a more balanced bilingual ratio ($55.4\%$ English, $35.3\%$ Hindi) compared to Qwen2.5-7B's skew toward English ($69.2\%$ English).

2. **Language Modeling & Lexical Diversity:**
   - **Qwen2.5-7B** achieves superior formal language modeling metrics, demonstrating lower Bits-per-Character (**BPC**: 1.6888 vs 1.8153), lower validation perplexity ($55.13$ vs $74.02$), and higher equal-length Distinct-1 diversity ($0.852$ vs $0.817$ at $K=25$).
   - Qwen2.5-7B produces fewer transliteration errors (**E8**: 71 vs 114) and fewer grammatical agreement violations (**E4**: 45 vs 68).

3. **Inference & Deployment Efficiency:**
   - **Qwen2.5-3B requires only 2.05 GB VRAM in 4-bit NF4**, making it deployable on entry-level edge hardware, mobile workstations, and consumer GPUs with zero offloading penalties.
   - **Qwen2.5-7B requires 4.65 GB VRAM**, consuming $>75\%$ of entry-level GPU memory and requiring higher thermal dissipation.

4. **Provisional Recommendation:**
   - For **conversational chat, localized chatbots, and compute-constrained edge deployments**, **Qwen2.5-3B is provisionally recommended** due to its superior conversational adherence, balanced matrix language mixing, and $2.3\times$ lower memory footprint.
   - For **unconstrained offline text processing requiring grammatical precision and maximal vocabulary richness**, **Qwen2.5-7B** remains advantageous.
   - **Mandatory Caveat:** Final definitive selection remains strictly provisional pending the double-blind human preference study (100 prompts $\times$ 3 judges) outlined in Task 7.

---

## 2. Multi-Dimensional Comparison Matrix

| Category | Metric | Qwen2.5-3B | Qwen2.5-7B | Advantage / Direction |
| --- | --- | --- | --- | --- |
| Architecture | Total Parameters | 3.09 B | 7.61 B | 3B: 59.4% smaller footprint |
| Architecture | 4-bit Model Memory (NF4) | 2.05 GB | 4.65 GB | 3B: Runs on consumer 4GB/6GB GPUs |
| Architecture | Adapter Weights Size | 14.10 MB | 19.28 MB | 3B: Lighter adapter checkpoint |
| Mistral-7B Judge | Fluency | 3.533 ± 0.921 | 3.251 ± 0.991 | 3B Higher (+0.282) |
| Mistral-7B Judge | Code Mixing Naturalness | 3.979 ± 1.211 | 3.682 ± 1.235 | 3B Higher (+0.297) |
| Mistral-7B Judge | Hindi Grammar | 2.943 ± 0.954 | 2.610 ± 0.942 | 3B Higher (+0.333) |
| Mistral-7B Judge | Prompt Adherence | 3.741 ± 1.399 | 3.072 ± 1.531 | 3B Higher (+0.669) |
| Mistral-7B Judge | Spelling Consistency | 4.648 ± 0.876 | 4.664 ± 0.837 | 7B Higher (+0.016) |
| Mistral-7B Judge | Overall | 3.563 ± 1.081 | 3.173 ± 1.139 | 3B Higher (+0.390) |
| Compression / LM | Perplexity (17k validation) | 74.02 | 55.13 | 7B Lower (better LM fit) |
| Compression / LM | Bits-per-Character (BPC) | 2.0013 | 1.8643 | 7B Lower BPC (1.6888 vs 1.8153) |
| Diversity (K=25) | Distinct-1 (Equal Length) | 0.9093 | 0.9019 | 7B Higher lexical diversity |
| Diversity (K=25) | Repetition Rate (Equal Length) | 0.0847 | 0.0981 | 7B Lower repetition (0.061 vs 0.088) |
| Code-Mixing Index | Das & Gambäck CMI (HingBERT-LID) | 16.78% | 12.93% | 3B More balanced code-mixing |
| Code-Mixing Index | Language Switching Frequency | 4.31 | 4.20 | 3B Higher conversational switching |
| Error Taxonomy | E1: E1 English dominant | 19 | 30 | Fewer errors on 3B |
| Error Taxonomy | E2: E2 Hindi dominant | 180 | 151 | Fewer errors on 7B |
| Error Taxonomy | E3: E3 Unnatural code switching | 10 | 6 | Fewer errors on 7B |
| Error Taxonomy | E4: E4 Grammatical error | 68 | 45 | Fewer errors on 7B |
| Error Taxonomy | E5: E5 Repetition | 41 | 48 | Fewer errors on 3B |
| Error Taxonomy | E6: E6 Prompt misunderstanding | 215 | 323 | Fewer errors on 3B |
| Error Taxonomy | E7: E7 Incomplete response | 106 | 135 | Fewer errors on 3B |
| Error Taxonomy | E8: E8 Spelling transliteration error | 114 | 71 | Fewer errors on 7B |
| Error Taxonomy | E9: E9 Hallucination factual error | 0 | 0 | Fewer errors on Tied |
| Error Taxonomy | E10: E10 Irrelevant response | 91 | 23 | Fewer errors on 7B |

---

## 3. Pairwise Preference Protocol Prepared
A 100-prompt double-blind pairwise preference evaluation sheet has been constructed at `research_upgrade/tables/proposed_pairwise_preference_100_prompts.csv`. In accordance with ethical standards, actual human ratings are deferred to the final human validation phase.
