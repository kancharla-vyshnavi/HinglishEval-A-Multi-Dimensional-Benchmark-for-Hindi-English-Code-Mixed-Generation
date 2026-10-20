HinglishEval

A multi-dimensional benchmark for Hindi–English (Hinglish) code-mixed text generation.

Show Image Show Image Show Image Show Image

HinglishEval compares four LLMs on 1,000 Hinglish prompts (4,000 generations) using human ratings from two annotators, automated LLM judges, linguistic diagnostics, error analysis, and statistical testing.

Key findings
Phi-3.5-mini rates significantly lowest on overall quality against every other model (Holm-adjusted p ≤ 0.006).
Qwen2.5-3B, Qwen2.5-7B and HingGPT are close. Qwen2.5-3B vs Qwen2.5-7B is not significant (p = 0.540), and Qwen2.5-3B vs HingGPT is not significant after correction (Holm p = 0.055).
Human agreement is low (QWK from −0.357 to +0.128 across dimensions), so results are reported per annotator as well as averaged.
Automated judges and humans disagree. Judges separate the models widely (Phi-3.5-mini overall 1.03 vs Qwen2.5-3B 3.56), while human ratings differ only slightly (2.11 vs 2.22).
Benchmark at a glance
Item	Count
Continued-pretraining sequences	277,431
Validation utterances	14,601
Benchmark prompts	1,000
Prompts quarantined by overlap audit (8-gram Jaccard)	8
Overlap-audited prompts	992
Generator models	4
Generations	4,000
Human ratings (2 annotators × 4,000)	8,000

Models: Qwen2.5-3B (QLoRA continued pretraining, rank 8, checkpoint-17340), Qwen2.5-7B, Phi-3.5-mini, HingGPT (L3Cube Pune).

Results: human evaluation

Mean of Annotators A and B, 1,000 responses per model, 1–5 scale, 95% bootstrap CI.

Model	Fluency	Code-Mixing	Hindi Grammar	Prompt Adherence	Spelling	Overall
Qwen2.5-7B	2.394 [2.370, 2.421]	2.613 [2.592, 2.635]	2.864 [2.839, 2.888]	2.659 [2.622, 2.685]	2.724 [2.684, 2.755]	2.227 [2.194, 2.262]
Qwen2.5-3B	2.399 [2.372, 2.424]	2.616 [2.592, 2.638]	2.884 [2.860, 2.910]	2.667 [2.633, 2.697]	2.752 [2.714, 2.782]	2.221 [2.189, 2.258]
HingGPT	2.361 [2.339, 2.388]	2.583 [2.559, 2.613]	2.845 [2.813, 2.872]	2.631 [2.601, 2.663]	2.694 [2.658, 2.723]	2.175 [2.142, 2.209]
Phi-3.5-mini	2.358 [2.335, 2.382]	2.558 [2.533, 2.584]	2.827 [2.798, 2.852]	2.615 [2.578, 2.643]	2.688 [2.646, 2.720]	2.114 [2.079, 2.142]
Pairwise comparisons (overall quality, Wilcoxon signed-rank, Holm-corrected, N = 1,000)
Comparison	Mean diff.	Raw p	Holm p	Significant (α = 0.05)
Qwen2.5-7B vs Phi-3.5-mini	+0.1125	4.89 × 10⁻⁹	2.94 × 10⁻⁸	Yes
Qwen2.5-3B vs Phi-3.5-mini	+0.1070	2.62 × 10⁻⁸	1.31 × 10⁻⁷	Yes
HingGPT vs Phi-3.5-mini	+0.0605	1.51 × 10⁻³	6.05 × 10⁻³	Yes
Qwen2.5-7B vs HingGPT	+0.0520	3.56 × 10⁻³	1.07 × 10⁻²	Yes
Qwen2.5-3B vs HingGPT	+0.0465	2.73 × 10⁻²	5.47 × 10⁻²	No
Qwen2.5-3B vs Qwen2.5-7B	−0.0055	5.40 × 10⁻¹	5.40 × 10⁻¹	No
Per-annotator overall quality (mean)
Model	Annotator A	Annotator B
Qwen2.5-3B	1.620	2.822
Qwen2.5-7B	1.616	2.837
HingGPT	1.519	2.830
Phi-3.5-mini	1.449	2.779

The two annotators use the scale at different levels (A ≈ 1.4–1.6, B ≈ 2.8 on overall quality). Phi-3.5-mini is last for both. The order of the other three differs between annotators.

Inter-annotator agreement (N = 4,000 pairs)
Dimension	Exact agr.	±1 agr.	QWK [95% CI]	Ordinal α [95% CI]	Spearman ρ
Prompt Adherence	35.8%	86.5%	+0.086 [0.06, 0.11]	−0.012 [−0.05, 0.02]	+0.118
Spelling Consistency	37.1%	84.0%	+0.128 [0.11, 0.15]	+0.063 [0.03, 0.08]	+0.183
Hindi Grammar	37.2%	86.1%	−0.119 [−0.15, −0.09]	−0.157 [−0.19, −0.13]	−0.154
Fluency	28.8%	90.4%	+0.000 [−0.03, 0.03]	−0.327 [−0.36, −0.30]	+0.047
Code-Mixing Naturalness	29.2%	80.1%	−0.357 [−0.38, −0.33]	−0.395 [−0.42, −0.37]	−0.408
Overall Quality	14.2%	57.8%	+0.087 [0.07, 0.10]	−0.323 [−0.35, −0.30]	+0.230
Results: automated judge

Mistral-7B-Instruct judge, mean ± SD, 1–5 scale.

Dimension	HingGPT	Phi-3.5-mini	Qwen2.5-3B	Qwen2.5-7B
Fluency	2.123 ± 1.003	1.028 ± 0.235	3.533 ± 0.921	3.251 ± 0.991
Code-Mixing	2.400 ± 1.279	1.041 ± 0.363	3.979 ± 1.211	3.682 ± 1.235
Hindi Grammar	1.644 ± 0.631	1.014 ± 0.167	2.943 ± 0.954	2.610 ± 0.942
Prompt Adherence	1.783 ± 1.057	1.032 ± 0.333	3.741 ± 1.399	3.072 ± 1.531
Spelling	2.868 ± 1.426	1.054 ± 0.411	4.648 ± 0.876	4.664 ± 0.837
Overall	1.990 ± 0.951	1.027 ± 0.242	3.563 ± 1.081	3.173 ± 1.139

Inter-judge agreement (Mistral-7B vs OLMo-2-1B, N = 3,989): QWK between −0.166 and +0.008 across dimensions.

Rubric sensitivity: a perturbed rubric shifts Mistral scores upward on every dimension (overall +0.420, 95% CI [0.380, 0.458]).

Error analysis (E1–E10, 4,000 generations)

A response can carry several flags (4,335 flags in total).

Code	Category	HingGPT	Phi-3.5-mini	Qwen2.5-3B	Qwen2.5-7B	Total
E1	English-dominant	6	6	19	30	61
E2	Hindi-dominant	53	264	180	151	648
E3	Unnatural code-switching	9	1	10	6	26
E4	Grammatical error	98	73	68	45	284
E5	Repetition	36	117	41	48	242
E6	Prompt misunderstanding	156	351	215	323	1,045
E7	Incomplete response	163	275	106	135	679
E8	Spelling / transliteration	2	678	114	71	865
E9	Hallucination detector flag	0	0	0	0	0
E10	Irrelevant response	135	236	91	23	485

E9 = 0 means the detector raised no flags, not that no hallucinations occurred.

Linguistic diagnostics
Metric	HingGPT	Phi-3.5-mini	Qwen2.5-3B	Qwen2.5-7B
CMI (%)	19.07	15.71	15.63	13.73
Both languages present (%)	77.3	51.3	67.0	68.3
Das–Gambäck CMI	15.146	22.238	16.776	12.927
Avg. language switches	8.709	4.677	4.308	4.202
Perplexity	171.23	50.79	74.02	55.13
Distinct-1	0.734	0.700	0.897	0.882
Distinct-2	0.858	0.751	0.960	0.970
Repetition rate	0.168	0.127	0.097	0.118
Quickstart
bash
git clone https://github.com/kancharla-vyshnavi/A-Multi-Dimensional-Benchmark-of-LLMs-for-Hindi-English-Code-Mixed-Generation.git
cd A-Multi-Dimensional-Benchmark-of-LLMs-for-Hindi-English-Code-Mixed-Generation
python -m venv .venv && source .venv/bin/activate   # Windows: .\.venv\Scripts\Activate.ps1
python -m pip install pandas numpy scipy matplotlib
python research_upgrade/v3/scripts/generate_publication_figures_and_tables.py

This rebuilds the summary tables and figures from the saved rating files. Training and generation need a CUDA GPU plus PyTorch, Transformers, PEFT and bitsandbytes.

Reproducibility
Bootstrap: 10,000 resamples, seed 42.
Continued pretraining (Qwen2.5-3B): QLoRA, LoRA rank 8, alpha 16, dropout 0.05, sequence length 128, effective batch size 16, paged_adamw_8bit, FP16, seed 42.
Statistics: Wilcoxon signed-rank with Holm correction (6 comparisons); QWK, ordinal Krippendorff's α and Spearman ρ for agreement.
Human ratings: human_ratings_4000_two_annotators.csv (8,000 rows, 0 missing, 0 duplicates).
Repository structure
text
research_upgrade/
├── figures/            # Figures
├── human_validation/   # FastAPI rating app and rating reports
├── leakage_audit/      # 8-gram overlap audit
├── paper/              # Manuscript
├── reports/            # Audit, methods and analysis reports
├── scripts/            # Evaluation, audit, reporting scripts
├── tables/             # Ratings, metrics, summary tables
└── v3/                 # Canonical configs, data, figures, scripts, tables
Human-rating app
bash
python -m uvicorn research_upgrade.human_validation.app:app --host 127.0.0.1 --port 8000
Limitations
Low inter-annotator agreement; the annotators use the scale at different levels.
Differences among Qwen2.5-3B, Qwen2.5-7B and HingGPT are small.
Models differ in size, tokenizer and training history, so this is not an architecture-only comparison.
8-gram overlap auditing does not rule out semantic contamination.
Offline benchmark scores do not measure chatbot latency, safety or user satisfaction.
Links
Resource	Link
Paper	research_upgrade/v3/paper/hinglisheval_paper.md
arXiv	TBA
QLoRA adapter (Hugging Face)	TBA
HingGPT checkpoint	TBA
Citation

See CITATION.cff.

bibtex
@misc{vyshnavi_hinglisheval,
  author = {Kancharla Vyshnavi},
  title  = {HinglishEval: A Multi-Dimensional Benchmark for Hindi-English Code-Mixed Generation},
  year   = {2026},
  url    = {https://github.com/kancharla-vyshnavi/A-Multi-Dimensional-Benchmark-of-LLMs-for-Hindi-English-Code-Mixed-Generation}
}
License

MIT for project code. Third-party datasets and model checkpoints keep their own licenses.

Author

Kancharla Vyshnavi
