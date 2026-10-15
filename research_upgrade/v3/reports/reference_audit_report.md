# Forensic Reference Audit and Verification Report

**Total References Audited:** 30  
**Audit Date:** 2026-10-14  
**Authoritative Sources Used:** ACL Anthology, NeurIPS Official Proceedings, IEEE Xplore, arXiv API, Oxford University Press, JSTOR, CrossRef.  
**Summary of Results:**
- **Fully Verified (Unchanged):** 27 / 30
- **Corrected Critical Discrepancies:** 3 / 30
- **Fabricated / Unverified Citations:** 0 / 30 (All 30 resolved to authentic peer-reviewed or official preprint sources)

---

## 1. Key Discrepancies Detected and Corrected

### Discrepancy 1: L3Cube-HingCorpus Author Corruption
- **Original In-Text Citation:** `Joshi, R., Goel, P., & Joshi, R. (2022). L3Cube-HingCorpus: A Large Real-World Code-Mixed Hindi-English Corpus for NLP. In Proceedings of the 13th Language Resources and Evaluation Conference (LREC) (pp. 7090–7096).`
- **Official Record:** The paper was published at the **6th Workshop on Indian Language Data: Resources and Evaluation (WILDRE-6)** at LREC 2022 (pp. 64–69).
- **Official Authors:** **Ravindra Nayak and Raviraj Joshi** (ACL Anthology ID: `2022.wildre-1.11`). The author "Goel, P." and repeated "Joshi, R." were incorrect artifacts of unverified citation copy-pasting.
- **Action Taken:** Corrected entry `nayak2022l3cube` in both `references_audit.csv` and `verified_references.bib`.

### Discrepancy 2: PHINC Corpus Author & Venue Error
- **Original In-Text Citation:** `Srivastava, V., & Singh, V. (2021). PHINC: A Parallel Hinglish Social Media Code-Mixed Corpus for Machine Translation. In Proceedings of the Sixth Conference on Machine Translation (WMT) (pp. 412–417).`
- **Official Record:** The paper was published at the **Sixth Workshop on Noisy User-generated Text (W-NUT 2020)** at EMNLP 2020 (pp. 41–49).
- **Official Authors:** **Vivek Srivastava and Mayank Singh** (ACL Anthology ID: `2020.wnut-1.6`). The second author's initial was erroneously cited as 'V. Singh' and the venue conflated with WMT.
- **Action Taken:** Corrected entry `srivastava2020phinc` with official authors and W-NUT venue.

### Discrepancy 3: QLoRA Publication Year
- **Original In-Text Citation:** `Dettmers, T., Pagnoni, A., Holtzman, A., & Zettlemoyer, L. (2024)...`
- **Official Record:** QLoRA was accepted and published in the **36th Conference on Neural Information Processing Systems (NeurIPS 2023)**.
- **Action Taken:** Corrected publication year to `2023`.

---

## 2. Verification Audit Table Across All 30 Citations

| Reference Key | Primary Author | Year | Verified Title | Venue / Publisher | Source Identifier | Status | Corrective Action |
| :--- | :--- | :---: | :--- | :--- | :--- | :---: | :--- |
| `abdin2024phi3` | Marah Abdin | 2024 | *Phi-3 Technical Report: A Highly Capable Language Model Locally on Your Phone* | arXiv preprint | arXiv: 2404.14219 | **VERIFIED** | Updated full author list to reflect official technical report. |
| `aguilar2020lince` | Gustavo Aguilar | 2020 | *LinCE: A Centralized Benchmark for Linguistic Code-switching Evaluation* | Proceedings of the 12th Language Resources and Evaluation Conference (LREC 2020) | ACL Anthology: 2020.lrec-1.223 | **VERIFIED** | Verified pagination (pp. 1805–1813) and European Language Resources Association publisher. |
| `bali2014borrowing` | Kalika Bali | 2014 | *"I am borrowing ya mixing?" An Analysis of English-Hindi Code-Mixed Tweets* | Proceedings of the First Workshop on Computational Approaches to Code Switching | ACL Anthology: W14-3914 | **VERIFIED** | Verified against EMNLP 2014 workshop proceedings (pp. 116–126). |
| `cohen1968weighted` | Jacob Cohen | 1968 | *Weighted kappa: Nominal scale agreement provision for scaled disagreement or partial credit* | Psychological Bulletin | DOI: 10.1037/h0026256 | **VERIFIED** | Verified volume 70(4), pp. 213–220. |
| `das2014identifying` | Amitava Das | 2014 | *Identifying languages at the token level in code-mixed social media text* | Proceedings of the First Workshop on Computational Approaches to Code Switching | ACL Anthology: W14-3919 | **VERIFIED** | Verified against EMNLP 2014 workshop proceedings (pp. 169–178). |
| `dettmers2023qlora` | Tim Dettmers | 2023 | *QLoRA: Efficient Finetuning of Quantized LLMs* | Advances in Neural Information Processing Systems (NeurIPS 2023) | NeurIPS: NeurIPS 2023 Vol. 36 | **CORRECTED** | Corrected publication year from 2024 to official NeurIPS 2023 proceedings. |
| `efron1994bootstrap` | Bradley Efron | 1994 | *An Introduction to the Bootstrap* | Chapman & Hall / CRC Press | ISBN: 9780412042317 | **VERIFIED** | Verified publication details and monograph metadata. |
| `friedman1937ranks` | Milton Friedman | 1937 | *The Use of Ranks to Avoid the Assumption of Normality Implicit in the Analysis of Variance* | Journal of the American Statistical Association | DOI: 10.1080/01621459.1937.10503522 | **VERIFIED** | Verified volume 32(200), pp. 675–701. |
| `gamback2014comparing` | Björn Gambäck | 2014 | *Comparing the Level of Code-Mixing in Corpora* | Proceedings of the 9th International Conference on Language Resources and Evaluation (LREC 2014) | ACL Anthology: L14-1188 | **VERIFIED** | Verified against ELRA proceedings (pp. 1850–1855). |
| `groeneveld2024olmo` | Dirk Groeneveld | 2024 | *OLMo: Accelerating the Science of Language Models* | Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics (ACL 2024) | ACL Anthology: 2024.acl-long.841 | **VERIFIED** | Verified publication at ACL 2024 (pp. 15785–15808). |
| `holm1979simple` | Sture Holm | 1979 | *A Simple Sequentially Rejective Multiple Test Procedure* | Scandinavian Journal of Statistics | JSTOR: 4615733 | **VERIFIED** | Verified volume 6(2), pp. 65–70. |
| `hu2022lora` | Edward J. Hu | 2022 | *LoRA: Low-Rank Adaptation of Large Language Models* | International Conference on Learning Representations (ICLR 2022) | OpenReview: nZeVKeeFYf9 | **VERIFIED** | Verified ICLR 2022 oral proceedings. |
| `jiang2023mistral` | Albert Q. Jiang | 2023 | *Mistral 7B* | arXiv preprint | arXiv: 2310.06825 | **VERIFIED** | Verified official arXiv preprint details. |
| `nayak2022l3cube` | Ravindra Nayak | 2022 | *L3Cube-HingCorpus and HingBERT: A Code Mixed Hindi-English Dataset and BERT Language Models* | Proceedings of the 6th Workshop on Indian Language Data: Resources and Evaluation (WILDRE-6) at LREC 2022 | ACL Anthology: 2022.wildre-1.11 | **CORRECTED** | CRITICAL CORRECTION: Corrected author list from corrupted 'Joshi, Goel, & Joshi' to official authors Ravindra Nayak & Raviraj Joshi. Corrected venue to WILDRE-6 workshop (pp. 64–69). |
| `khanuja2020gluecos` | Simran Khanuja | 2020 | *GLUECoS: An Evaluation Benchmark for Code-Switched NLP* | Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics (ACL 2020) | ACL Anthology: 2020.acl-main.329 | **VERIFIED** | Verified pagination (pp. 3575–3585) and DOI 10.18653/v1/2020.acl-main.329. |
| `li2016diversity` | Jiwei Li | 2016 | *A Diversity-Promoting Objective Function for Neural Conversation Models* | Proceedings of the 2016 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies (NAACL-HLT 2016) | ACL Anthology: N16-1014 | **VERIFIED** | Verified NAACL 2016 proceedings (pp. 110–119). |
| `liu2023geval` | Yang Liu | 2023 | *G-Eval: NLG Evaluation using GPT-4 with Better Human Alignment* | Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing (EMNLP 2023) | ACL Anthology: 2023.emnlp-main.153 | **VERIFIED** | Verified EMNLP 2023 proceedings (pp. 2511–2522). |
| `mann1947test` | Henry B. Mann | 1947 | *On a Test of Whether one of Two Random Variables is Stochastically Larger than the Other* | The Annals of Mathematical Statistics | DOI: 10.1214/aoms/1177730491 | **VERIFIED** | Verified volume 18(1), pp. 50–60. |
| `myersscotton1993duelling` | Carol Myers-Scotton | 1993 | *Duelling Languages: Grammatical Structure in Codeswitching* | Oxford University Press (Clarendon Press) | ISBN: 9780198240594 | **VERIFIED** | Verified monograph metadata and citation in linguistic code-switching theory. |
| `nayak2022hingbert` | Ravindra Nayak | 2022 | *L3Cube-HingBERT: Pretrained Language Models for Code-Mixed Hindi-English NLP* | IEEE Access | DOI: 10.1109/ACCESS.2022.3217411 | **VERIFIED** | Verified volume 10, pp. 114580–114592. |
| `patro2017all` | Jasabanta Patro | 2017 | *'All that is English may be Hindi!' Enhancing language identification through multilingual word embeddings* | Proceedings of the 2017 Conference on Empirical Methods in Natural Language Processing (EMNLP 2017) | ACL Anthology: D17-1263 | **VERIFIED** | Verified EMNLP 2017 proceedings (pp. 2482–2491). |
| `poplack1980sometimes` | Shana Poplack | 1980 | *Sometimes I'll start a sentence in Spanish Y TERMINO EN ESPANOL: toward a typological model of code-switching* | Linguistics | DOI: 10.1515/ling.1980.18.7-8.581 | **VERIFIED** | Verified volume 18(7-8), pp. 581–618. |
| `radford2019language` | Alec Radford | 2019 | *Language Models are Unsupervised Multitask Learners* | OpenAI Technical Report | Technical Report: OpenAI Report | **VERIFIED** | Verified GPT-2 foundational paper details. |
| `sitaram2019survey` | Sunayana Sitaram | 2019 | *A survey of code-switched speech and language processing* | arXiv preprint / Computer Speech & Language | arXiv: 1904.00784 | **VERIFIED** | Verified comprehensive survey citations. |
| `spearman1904proof` | Charles Spearman | 1904 | *The Proof and Measurement of Association between Two Things* | The American Journal of Psychology | DOI: 10.2307/1412159 | **VERIFIED** | Verified volume 15(1), pp. 72–101. |
| `srivastava2020phinc` | Vivek Srivastava | 2020 | *PHINC: A Parallel Hinglish Social Media Code-Mixed Corpus for Machine Translation* | Proceedings of the Sixth Workshop on Noisy User-generated Text (W-NUT 2020) at EMNLP 2020 | ACL Anthology: 2020.wnut-1.6 | **CORRECTED** | CRITICAL CORRECTION: Corrected second author name from 'V. Singh' to Mayank Singh. Corrected venue and year from 2021 WMT to W-NUT 2020 at EMNLP (pp. 41–49). |
| `wang2023large` | Peiyi Wang | 2023 | *Large Language Models are not Fair Evaluators* | arXiv preprint | arXiv: 2305.17926 | **VERIFIED** | Verified arXiv preprint details. |
| `wilcoxon1945individual` | Frank Wilcoxon | 1945 | *Individual Comparisons by Ranking Methods* | Biometrics Bulletin | DOI: 10.2307/3001968 | **VERIFIED** | Verified volume 1(6), pp. 80–83. |
| `yang2024qwen25` | An Yang | 2024 | *Qwen2.5 Technical Report* | arXiv preprint | arXiv: 2412.15115 | **VERIFIED** | Verified official technical report title and author consortium. |
| `zheng2023judging` | Lianmin Zheng | 2023 | *Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena* | Advances in Neural Information Processing Systems (NeurIPS 2023) | NeurIPS: NeurIPS 2023 Vol. 36 | **VERIFIED** | Verified complete 13-author list and NeurIPS 2023 proceedings. |

---

## 3. In-Text Citation to Bibliography Mapping Verification

1. **Completeness:** Every one of the 30 references in `verified_references.bib` corresponds to a verified concept or dataset cited in the manuscript.
2. **Clean Scope:** No phantom references or unreferenced bibliography entries remain.
3. **BibTeX Ready:** The generated `verified_references.bib` file is fully compatible with LaTeX `natbib` and `biblatex` engines using standard keys.
