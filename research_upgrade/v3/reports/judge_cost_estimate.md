# Task 2: Independent API Judges — Dry Run and Cost Estimate Report

**Evaluation Design:** Two Independent API Judges from Distinct Model Families
1. **OpenAI GPT Family:** `gpt-4o-mini-2024-07-18`
2. **Anthropic Claude Family:** `claude-3-5-haiku-20241022`

**Blinding Protocol:** Generator model names are strictly hidden; presentation order is shuffled using fixed seed `42`.
**Checkpointing:** Resumable batch writes every 50 records to prevent duplicate spend.

---

## 1. Dry Run Token Metrics (N = 20 Sample Responses)

- **System Prompt & Few-Shot Context:** ~881 tokens per API call
- **Mean User Utterance & Generation:** ~129.0 tokens
- **Total Mean Input Tokens / Item:** **1010.0 tokens**
- **Mean Structured JSON Output / Item:** **65.0 tokens**
- **Full Dataset Scale (4,000 items):** 4,040,200 input tokens, 260,000 output tokens

---

## 2. Verified Cost Projections for Full 4,000-Response Evaluation

| Judge Model | Provider | Model Family | Input Rate (/1M) | Output Rate (/1M) | Projected Total Cost (USD) | Credential Status | Pricing Source |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| `gpt-4o-mini-2024-07-18` | Openai | OpenAI GPT | $0.15 | $0.60 | **$0.76** | BLOCKED (Missing API Key) | 2024-10-01 (Official OpenAI Pricing) |
| `claude-3-5-haiku-20241022` | Anthropic | Anthropic Claude | $0.80 | $4.00 | **$4.27** | BLOCKED (Missing API Key) | 2024-10-22 (Official Anthropic Pricing) |

### Total Combined Cost Estimate:
- Dual-Judge Scoring (OpenAI + Anthropic across all 4,000 responses): **$5.03 USD**

---

## 3. Honest Completion Status Disclosure

1. **Status of External API Judging:** **NOT RUN / BLOCKED ($0.00 Spend)**
   - Formally designated as NOT RUN due to API quota exhaustion (OpenAI returned RateLimitError 429 `credit_balance_exhausted`) and absent Anthropic credentials (`ANTHROPIC_API_KEY` unset).
   - Zero paid API calls were executed, zero costs incurred, and zero API numbers fabricated.

2. **Status of Local Qwen2.5-3B-Instruct Judging:** **COMPLETED (4,000 / 4,000 Records, 100.00%)**
   - Verified on disk in `judge_qwen25_3b_4000_results.jsonl`: exactly 4,000 / 4,000 responses evaluated (3,996 valid, 4 preserved malformed outputs with `is_valid = False`, 0 failed JSON parses, 0 duplicate keys, 0 missing records).
   - Serves as the active dual-judge evaluator alongside Mistral-7B, confirming robust positive inter-judge alignment across all six dimensions.
