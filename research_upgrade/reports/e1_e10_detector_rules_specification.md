# Formal Specification: Automated Fine-Grained Error Taxonomy (E1–E10)

## Overview and Methodological Principles
To complement subjective Likert-scale evaluations with objective, reproducible diagnostic signals, we establish a deterministic rule-based error taxonomy spanning ten distinct failure modes (**E1–E10**). 

The detector operates without human annotator variance and without prompting an LLM evaluator, guaranteeing 100% determinism across benchmark iterations.

---

## Formal Definitions and Mathematical Detector Rules

### E1: English-Dominant Output
- **Definition:** The model collapses into monolingual English, violating the code-mixing instruction.
- **Rule Formulation:**
  $$\text{Detect}(E1) = \mathbb{I}\left( R_{\text{en}} \ge 0.45 \;\wedge\; R_{\text{hi}} < 0.10 \;\wedge\; R_{\text{roman-hi}} < 0.10 \right)$$
  where $R_{\text{en}} = \frac{N_{\text{English}}}{N_{\text{words}}}$ and $R_{\text{hi}} = \frac{N_{\text{Hindi}}}{N_{\text{words}}}$.

### E2: Hindi-Dominant Output (Excessive Hindi / Script Drift)
- **Definition:** The model generates predominantly Hindi text with negligible English participation.
- **Rule Formulation:**
  $$\text{Detect}(E2) = \mathbb{I}\left( (R_{\text{hi}} + R_{\text{roman-hi}}) \ge 0.45 \;\wedge\; R_{\text{en}} < 0.10 \right)$$

### E3: Unnatural Code-Switching Boundary
- **Definition:** Fragmented, hyper-frequent language alternating within clauses or mid-phrase stuttering across punctuation.
- **Rule Formulation:**
  Let $S$ be the number of language transitions between consecutive tokens in a sequence of $L$ classified tokens ($L \ge 8$).
  $$\text{SwitchRate} = \frac{S}{L}$$
  $$\text{Detect}(E3) = \mathbb{I}\left( \text{SwitchRate} \ge 0.65 \;\vee\; \left(\text{PunctuationFragmentRatio} \ge 0.65 \right) \right)$$

### E4: Grammatical Agreement Error
- **Definition:** Subject-verb agreement violations, tense mismatch, or corrupted verbal postposition structures (e.g., *"he don't"*, *"i has"*, *"they is"*, or ungrammatical repetitive punctuation `[.,!?]{3,}`).
- **Rule Formulation:**
  $$\text{Detect}(E4) = \mathbb{I}\left( \text{RegexMatch}(\text{SyntacticAgreementViolations}) \;\vee\; \text{RegexMatch}([,.!?]{3,}) \right)$$

### E5: Token / Emoji Repetition Loop
- **Definition:** Degenerative decoding loops characterized by consecutive identical tokens, n-gram cyclic stuttering, or emoji spam.
- **Rule Formulation:**
  Let $A$ be the count of adjacent identical tokens ($w_i = w_{i+1}$) and $T_{\text{rep}}$ be repeated 3-grams:
  $$\text{RepScore} = \frac{2A + T_{\text{rep}}}{\max(N_{\text{words}}, 1)}$$
  $$\text{Detect}(E5) = \mathbb{I}\left( \text{RepScore} \ge 0.18 \right)$$

### E6: Prompt Misunderstanding
- **Definition:** The model issues an explicit refusal (*"I cannot help"*, *"as an AI"*), produces code when conversational text was requested, or fails minimal semantic instruction criteria.
- **Rule Formulation:**
  $$\text{Detect}(E6) = \mathbb{I}\left( \text{RegexMatch}(\text{RefusalPatterns}) \;\vee\; \left( \text{PromptRequiresCode} \wedge \neg\text{ContainsCode} \wedge N_{\text{words}} \le 8 \right) \right)$$

### E7: Incomplete / Truncated Response
- **Definition:** The generation abruptly terminates mid-sentence, ends with an unresolved syntactic connector (*"and"*, *"because"*, *"with"*, *"toh"*), or contains an unfinished trailing ellipsis.
- **Rule Formulation:**
  $$\text{Detect}(E7) = \mathbb{I}\left( N_{\text{words}} \le 3 \;\vee\; \text{EndsWithConnector} \;\vee\; \text{RegexMatch}(\text{TrailingCutoff}) \right)$$

### E8: Spelling / Transliteration Error
- **Definition:** Phonetically implausible Romanized transliteration, excessive vowel omission (consonant clustering $\ge 8$ characters without vowels), or character elongation (*"kaaaaaaaaam"*).
- **Rule Formulation:**
  $$\text{Detect}(E8) = \mathbb{I}\left( \text{RegexMatch}((.)\1{4,}) \;\vee\; \left( \sum_{w \in W} \mathbb{I}(|w| \ge 8 \wedge \text{Vowels}(w) = 0) \ge 2 \right) \right)$$

### E9: Hallucination / Factual Contradiction
- **Definition:** Blatant factual or arithmetic contradictions within the generated text.
- **Methodological Note:** Currently restricted to arithmetic contradictions ($2+2=5$, etc.) in heuristic mode. Without entity-level knowledge graph linking, general factual hallucinations in conversational domains cannot be resolved by regex heuristics; this boundary condition is explicitly documented.

### E10: Irrelevant Response / Topical Drift
- **Definition:** Completely off-topic boilerplate responses, unprompted apologies, or canned disclaimers (*"I am an AI assistant and cannot feel emotions"*).
- **Rule Formulation:**
  $$\text{Detect}(E10) = \mathbb{I}\left( \text{RegexMatch}(\text{GenericAIEvasionPhrases}) \right)$$

---

## Validation Summary
The detector scripts have been validated across all 4,000 controlled generations.
