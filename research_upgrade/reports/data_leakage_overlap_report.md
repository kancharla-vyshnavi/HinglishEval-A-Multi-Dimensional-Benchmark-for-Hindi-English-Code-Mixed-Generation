# Benchmark vs Training Set Overlap Audit Report

**Audit Date:** 2026-10-13 20:14:03  
**Evaluated Training File:** `C:\Users\vyshu\Downloads\train.jsonl` (277,431 sequences)  
**Evaluated Benchmark File:** `data\benchmarks\hinglish_bench_.csv` (1,000 prompts)  
**Audit Wallclock Time:** 104.33 seconds  

---

## 1. Executive Summary

| Category | Overlap Count (Train Rows) | Unique Benchmark Prompts Affected | % of Benchmark |
| :--- | :--- | :--- | :--- |
| **Exact Matches (Identical String)** | **0** | **0** | **0.00%** |
| **Case-Insensitive Exact Matches (New)** | **0** | **0** | **0.00%** |
| **Normalized Text Matches (New)** | **0** | **0** | **0.00%** |
| **High Near-Duplicates (Token Jaccard $\ge 0.90$)** | **0** | **0** | **0.00%** |
| **Moderate Near-Duplicates ($0.80 \le \text{Jaccard} < 0.90$)** | **102** | **8** | **0.80%** |
| **Total Distinct Benchmark Prompts Affected** | **102** | **8** | **0.80%** |

---

## 2. Leakage and Contamination Analysis

1. **Validation & Benchmark Integrity:**
   - The original paper stated that the 1,000 benchmark prompts were sampled from `data/processed/cpt/validation.jsonl` (14,601 entries) under the assumption that the training corpus of 277,431 sequences was strictly disjoint.
   - The empirical audit demonstrates that **0** prompts (0.00%) have exact textual duplicates in the training set, and **0** prompts (0.00%) have normalized alphanumeric matches.
   - For publication quality, this exact overlap count must be reported in the paper and benchmark specification.
   - Original data files are strictly preserved without modification.

---

## 3. Representative Overlap Instances

### Example 1: near_duplicate_jaccard_>=0.8 (Benchmark Prompt ID: 354, Train Line: 2853)
- **Benchmark Utterance:** `shame on you salman khan 790 colors stop harassing umar`
- **Training Utterance:** `shame on you salman khan 298 colors stop harassing umar`
- **Similarity Score:** 0.8182

### Example 2: near_duplicate_jaccard_>=0.8 (Benchmark Prompt ID: 354, Train Line: 7800)
- **Benchmark Utterance:** `shame on you salman khan 790 colors stop harassing umar`
- **Training Utterance:** `shame on you salman khan 19 colors stop harassing umar`
- **Similarity Score:** 0.8182

### Example 3: near_duplicate_jaccard_>=0.8 (Benchmark Prompt ID: 354, Train Line: 8438)
- **Benchmark Utterance:** `shame on you salman khan 790 colors stop harassing umar`
- **Training Utterance:** `shame on you salman khan 47 colors stop harassing umar`
- **Similarity Score:** 0.8182

### Example 4: near_duplicate_jaccard_>=0.8 (Benchmark Prompt ID: 354, Train Line: 11694)
- **Benchmark Utterance:** `shame on you salman khan 790 colors stop harassing umar`
- **Training Utterance:** `shame on you salman khan 621 colors stop harassing umar`
- **Similarity Score:** 0.8182

### Example 5: near_duplicate_jaccard_>=0.8 (Benchmark Prompt ID: 354, Train Line: 13462)
- **Benchmark Utterance:** `shame on you salman khan 790 colors stop harassing umar`
- **Training Utterance:** `shame on you salman khan 222 colors stop harassing umar`
- **Similarity Score:** 0.8182

### Example 6: near_duplicate_jaccard_>=0.8 (Benchmark Prompt ID: 354, Train Line: 17728)
- **Benchmark Utterance:** `shame on you salman khan 790 colors stop harassing umar`
- **Training Utterance:** `shame on you salman khan 25 colors stop harassing umar`
- **Similarity Score:** 0.8182

### Example 7: near_duplicate_jaccard_>=0.8 (Benchmark Prompt ID: 425, Train Line: 18539)
- **Benchmark Utterance:** `my friend: i am 45 kg and you. me: ja bahan kuchh kha ho gaya hai😉🤪`
- **Training Utterance:** `my friend: i am 45 kg and you. me: ja behan kuchh kha ho gaya hai😉🤪`
- **Similarity Score:** 0.8824

### Example 8: near_duplicate_jaccard_>=0.8 (Benchmark Prompt ID: 354, Train Line: 18601)
- **Benchmark Utterance:** `shame on you salman khan 790 colors stop harassing umar`
- **Training Utterance:** `shame on you salman khan 777$ colors stop harassing umar`
- **Similarity Score:** 0.8182

### Example 9: near_duplicate_jaccard_>=0.8 (Benchmark Prompt ID: 354, Train Line: 18658)
- **Benchmark Utterance:** `shame on you salman khan 790 colors stop harassing umar`
- **Training Utterance:** `shame on you salman khan 458 colors stop harassing umar`
- **Similarity Score:** 0.8182

### Example 10: near_duplicate_jaccard_>=0.8 (Benchmark Prompt ID: 354, Train Line: 21370)
- **Benchmark Utterance:** `shame on you salman khan 790 colors stop harassing umar`
- **Training Utterance:** `shame on you salman khan 787 colors stop harassing umar`
- **Similarity Score:** 0.8182

### Example 11: near_duplicate_jaccard_>=0.8 (Benchmark Prompt ID: 354, Train Line: 25847)
- **Benchmark Utterance:** `shame on you salman khan 790 colors stop harassing umar`
- **Training Utterance:** `shame on you salman khan 183 colors stop harassing umar`
- **Similarity Score:** 0.8182

### Example 12: near_duplicate_jaccard_>=0.8 (Benchmark Prompt ID: 867, Train Line: 26306)
- **Benchmark Utterance:** `Salman Khan grooves to Jumme Ki Raat with Shilpa Shetty at Praful Patels sons wedding,watch`
- **Training Utterance:** `Salman Khan grooves to Jumme Ki Raat with Shilpa Shetty at Praful Patels sons wedding, watch`
- **Similarity Score:** 0.8235

### Example 13: near_duplicate_jaccard_>=0.8 (Benchmark Prompt ID: 354, Train Line: 33784)
- **Benchmark Utterance:** `shame on you salman khan 790 colors stop harassing umar`
- **Training Utterance:** `shame on you salman khan 112 colors stop harassing umar`
- **Similarity Score:** 0.8182

### Example 14: near_duplicate_jaccard_>=0.8 (Benchmark Prompt ID: 354, Train Line: 34179)
- **Benchmark Utterance:** `shame on you salman khan 790 colors stop harassing umar`
- **Training Utterance:** `shame on you salman khan 592 colors stop harassing umar`
- **Similarity Score:** 0.8182

### Example 15: near_duplicate_jaccard_>=0.8 (Benchmark Prompt ID: 354, Train Line: 34708)
- **Benchmark Utterance:** `shame on you salman khan 790 colors stop harassing umar`
- **Training Utterance:** `shame on you salman khan 4 colors stop harassing umar`
- **Similarity Score:** 0.8182

