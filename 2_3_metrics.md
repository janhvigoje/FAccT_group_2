# 2.3 Metrics


Following the corrected dual-mode evaluation methodology established by our team in Section 2.2, we report the multidimensional metrics breakdown for the OpenAI Privacy Filter (OPF). As detailed in 2.2, the raw dataset labels were collapsed into **21 canonical categories** to eliminate taxonomy fragmentation. 

To isolate technical capability from deployment risks, we present the results in two modalities:
* **In-Scope Evaluation**: Assesses the model strictly on the 9 observed PII categories it successfully detects, plus one broken mapping (`ACCOUNTNUMBER`).
* **Full Evaluation**: Scores the model against all 21 observed canonical categories, penalizing the **12 unsupported labels** (marked with `*`) as False Negatives (FN) to reflect real-world pipeline leakage risk.

### (i) PII Category Breakdown

**In-Scope Mode Category Breakdown:**

| Category | TP | FP | FN | Precision | Recall | F1 | FNR | FPR |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **EMAIL** | 1040 | 58 | 0 | 0.9472 | 1.0000 | 0.9729 | 0.0000 | 0.0528 |
| **SOCIALNUMBER** | 944 | 0 | 2 | 1.0000 | 0.9979 | 0.9989 | 0.0021 | 0.0000 |
| **IDCARD** | 1051 | 0 | 52 | 1.0000 | 0.9529 | 0.9759 | 0.0471 | 0.0000 |
| **IP** | 921 | 118 | 17 | 0.8864 | 0.9819 | 0.9317 | 0.0181 | 0.1136 |
| **TEL** | 825 | 87 | 3 | 0.9046 | 0.9964 | 0.9483 | 0.0036 | 0.0954 |
| **PASS** | 621 | 53 | 16 | 0.9214 | 0.9749 | 0.9474 | 0.0251 | 0.0786 |
| **DATE** | 687 | 1169 | 17 | 0.3702 | 0.9759 | 0.5367 | 0.0241 | 0.6298 |
| **PERSON** | 1763 | 2193 | 339 | 0.4457 | 0.8387 | 0.5820 | 0.1613 | 0.5543 |
| **ADDRESS** | 1937 | 1111 | 1540 | 0.6355 | 0.5571 | 0.5937 | 0.4429 | 0.3645 |
| **ACCOUNTNUMBER** | 0 | 2127 | 0 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 1.0000 |

**Full Mode Category Breakdown:**

| Category | TP | FP | FN | Precision | Recall | F1 | FNR | FPR |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **EMAIL** | 1040 | 58 | 0 | 0.9472 | 1.0000 | 0.9729 | 0.0000 | 0.0528 |
| **SOCIALNUMBER** | 944 | 0 | 2 | 1.0000 | 0.9979 | 0.9989 | 0.0021 | 0.0000 |
| **IDCARD** | 1051 | 0 | 52 | 1.0000 | 0.9529 | 0.9759 | 0.0471 | 0.0000 |
| **IP** | 921 | 118 | 17 | 0.8864 | 0.9819 | 0.9317 | 0.0181 | 0.1136 |
| **TEL** | 825 | 87 | 3 | 0.9046 | 0.9964 | 0.9483 | 0.0036 | 0.0954 |
| **PASS** | 621 | 53 | 16 | 0.9214 | 0.9749 | 0.9474 | 0.0251 | 0.0786 |
| **DATE** | 687 | 1169 | 17 | 0.3702 | 0.9759 | 0.5367 | 0.0241 | 0.6298 |
| **PERSON** | 1763 | 2193 | 339 | 0.4457 | 0.8387 | 0.5820 | 0.1613 | 0.5543 |
| **ADDRESS** | 1937 | 1111 | 1540 | 0.6355 | 0.5571 | 0.5937 | 0.4429 | 0.3645 |
| **ACCOUNTNUMBER** | 0 | 2127 | 0 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 1.0000 |
| **BOD \*** | 0 | 0 | 920 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 0.0000 |
| **BUILDING \*** | 0 | 0 | 718 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 0.0000 |
| **DRIVERLICENSE \*** | 0 | 0 | 988 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 0.0000 |
| **GEOCOORD \*** | 0 | 0 | 79 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 0.0000 |
| **LASTNAME3 \*** | 0 | 0 | 79 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 0.0000 |
| **PASSPORT \*** | 0 | 0 | 1019 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 0.0000 |
| **SECADDRESS \*** | 0 | 0 | 320 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 0.0000 |
| **SEX \*** | 0 | 0 | 843 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 0.0000 |
| **TIME \*** | 0 | 0 | 1539 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 0.0000 |
| **TITLE \*** | 0 | 0 | 769 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 0.0000 |
| **USERNAME \*** | 0 | 0 | 1078 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 0.0000 |

### (ii) Language Breakdown

**In-Scope Evaluation Mode:**

| Language | TP | FP | FN | Precision | Recall | F1 | FNR | FPR |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Dutch** | 1773 | 1246 | 388 | 0.5873 | 0.8205 | 0.6846 | 0.1795 | 0.4127 |
| **English** | 1591 | 1046 | 343 | 0.6033 | 0.8226 | 0.6961 | 0.1774 | 0.3967 |
| **French** | 1668 | 1209 | 296 | 0.5798 | 0.8493 | 0.6891 | 0.1507 | 0.4202 |
| **German** | 1546 | 1239 | 293 | 0.5551 | 0.8407 | 0.6687 | 0.1593 | 0.4449 |
| **Italian** | 1624 | 1064 | 318 | 0.6042 | 0.8363 | 0.7015 | 0.1637 | 0.3958 |
| **Spanish** | 1587 | 1112 | 348 | 0.5880 | 0.8202 | 0.6849 | 0.1798 | 0.4120 |

**Full Evaluation Mode:**

| Language | TP | FP | FN | Precision | Recall | F1 | FNR | FPR |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Dutch** | 1773 | 1246 | 1913 | 0.5873 | 0.4810 | 0.5289 | 0.5190 | 0.4127 |
| **English** | 1591 | 1046 | 1637 | 0.6033 | 0.4929 | 0.5425 | 0.5071 | 0.3967 |
| **French** | 1668 | 1209 | 1641 | 0.5798 | 0.5041 | 0.5393 | 0.4959 | 0.4202 |
| **German** | 1546 | 1239 | 1805 | 0.5551 | 0.4614 | 0.5039 | 0.5386 | 0.4449 |
| **Italian** | 1624 | 1064 | 1611 | 0.6042 | 0.5020 | 0.5484 | 0.4980 | 0.3958 |
| **Spanish** | 1587 | 1112 | 1732 | 0.5880 | 0.4782 | 0.5274 | 0.5218 | 0.4120 |

### (iii) Domain Breakdown

**In-Scope Evaluation Mode:**

| Domain | TP | FP | FN | Precision | Recall | F1 | FNR | FPR |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Business** | 7038 | 4888 | 1490 | 0.5901 | 0.8253 | 0.6882 | 0.1747 | 0.4099 |
| **Education** | 629 | 457 | 98 | 0.5792 | 0.8652 | 0.6939 | 0.1348 | 0.4208 |
| **Finance** | 111 | 61 | 25 | 0.6453 | 0.8162 | 0.7208 | 0.1838 | 0.3547 |
| **Healthcare** | 895 | 630 | 172 | 0.5869 | 0.8388 | 0.6906 | 0.1612 | 0.4131 |
| **Legal Services** | 615 | 531 | 127 | 0.5366 | 0.8288 | 0.6515 | 0.1712 | 0.4634 |
| **Psychology** | 501 | 349 | 74 | 0.5894 | 0.8713 | 0.7032 | 0.1287 | 0.4106 |

**Full Evaluation Mode:**

| Domain | TP | FP | FN | Precision | Recall | F1 | FNR | FPR |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Business** | 7038 | 4888 | 7422 | 0.5901 | 0.4867 | 0.5335 | 0.5133 | 0.4099 |
| **Education** | 629 | 457 | 614 | 0.5792 | 0.5060 | 0.5401 | 0.4940 | 0.4208 |
| **Finance** | 111 | 61 | 97 | 0.6453 | 0.5337 | 0.5842 | 0.4663 | 0.3547 |
| **Healthcare** | 895 | 630 | 893 | 0.5869 | 0.5006 | 0.5403 | 0.4994 | 0.4131 |
| **Legal Services** | 615 | 531 | 784 | 0.5366 | 0.4396 | 0.4833 | 0.5604 | 0.4634 |
| **Psychology** | 501 | 349 | 529 | 0.5894 | 0.4864 | 0.5330 | 0.5136 | 0.4106 |

### (iv) Text Length Breakdown

**In-Scope Evaluation Mode:**

| Length Group | TP | FP | FN | Precision | Recall | F1 | FNR | FPR |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Short (< 426 Chars)** | 4809 | 3337 | 923 | 0.5904 | 0.8390 | 0.6930 | 0.1610 | 0.4096 |
| **Long (>= 426 Chars)** | 4980 | 3579 | 1063 | 0.5818 | 0.8241 | 0.6821 | 0.1759 | 0.4182 |

**Full Evaluation Mode:**

| Length Group | TP | FP | FN | Precision | Recall | F1 | FNR | FPR |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Short (< 426 Chars)** | 4809 | 3337 | 5008 | 0.5904 | 0.4899 | 0.5354 | 0.5101 | 0.4096 |
| **Long (>= 426 Chars)** | 4980 | 3579 | 5331 | 0.5818 | 0.4830 | 0.5278 | 0.5170 | 0.4182 |

### (v) Intersectional Breakdown: Domain x Length

**In-Scope Evaluation Mode:**

| Intersectional Group | TP | FP | FN | Precision | Recall | F1 | FNR | FPR |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Business (Short)** | 3552 | 2451 | 713 | 0.5917 | 0.8328 | 0.6919 | 0.1672 | 0.4083 |
| **Business (Long)** | 3486 | 2437 | 777 | 0.5886 | 0.8177 | 0.6845 | 0.1823 | 0.4114 |
| **Education (Short)** | 276 | 192 | 49 | 0.5897 | 0.8492 | 0.6961 | 0.1508 | 0.4103 |
| **Education (Long)** | 353 | 265 | 49 | 0.5712 | 0.8781 | 0.6922 | 0.1219 | 0.4288 |
| **Finance (Short)** | 49 | 20 | 11 | 0.7101 | 0.8167 | 0.7597 | 0.1833 | 0.2899 |
| **Finance (Long)** | 62 | 41 | 14 | 0.6019 | 0.8158 | 0.6927 | 0.1842 | 0.3981 |
| **Healthcare (Short)** | 406 | 265 | 49 | 0.6051 | 0.8923 | 0.7211 | 0.1077 | 0.3949 |
| **Healthcare (Long)** | 489 | 365 | 123 | 0.5726 | 0.7990 | 0.6671 | 0.2010 | 0.4274 |
| **Legal Services (Short)** | 317 | 274 | 76 | 0.5364 | 0.8066 | 0.6443 | 0.1934 | 0.4636 |
| **Legal Services (Long)** | 298 | 257 | 51 | 0.5369 | 0.8539 | 0.6593 | 0.1461 | 0.4631 |
| **Psychology (Short)** | 209 | 135 | 25 | 0.6076 | 0.8932 | 0.7232 | 0.1068 | 0.3924 |
| **Psychology (Long)** | 292 | 214 | 49 | 0.5771 | 0.8563 | 0.6895 | 0.1437 | 0.4229 |

**Full Evaluation Mode:**

| Intersectional Group | TP | FP | FN | Precision | Recall | F1 | FNR | FPR |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Business (Short)** | 3552 | 2451 | 3700 | 0.5917 | 0.4898 | 0.5359 | 0.5102 | 0.4083 |
| **Business (Long)** | 3486 | 2437 | 3722 | 0.5886 | 0.4836 | 0.5310 | 0.5164 | 0.4114 |
| **Education (Short)** | 276 | 192 | 285 | 0.5897 | 0.4920 | 0.5364 | 0.5080 | 0.4103 |
| **Education (Long)** | 353 | 265 | 329 | 0.5712 | 0.5176 | 0.5431 | 0.4824 | 0.4288 |
| **Finance (Short)** | 49 | 20 | 37 | 0.7101 | 0.5698 | 0.6323 | 0.4302 | 0.2899 |
| **Finance (Long)** | 62 | 41 | 60 | 0.6019 | 0.5082 | 0.5511 | 0.4918 | 0.3981 |
| **Healthcare (Short)** | 406 | 265 | 360 | 0.6051 | 0.5300 | 0.5651 | 0.4700 | 0.3949 |
| **Healthcare (Long)** | 489 | 365 | 533 | 0.5726 | 0.4785 | 0.5213 | 0.5215 | 0.4274 |
| **Legal Services (Short)** | 317 | 274 | 422 | 0.5364 | 0.4290 | 0.4767 | 0.5710 | 0.4636 |
| **Legal Services (Long)** | 298 | 257 | 362 | 0.5369 | 0.4515 | 0.4905 | 0.5485 | 0.4631 |
| **Psychology (Short)** | 209 | 135 | 204 | 0.6076 | 0.5061 | 0.5522 | 0.4939 | 0.3924 |
| **Psychology (Long)** | 292 | 214 | 325 | 0.5771 | 0.4733 | 0.5200 | 0.5267 | 0.4229 |

---

## Key Findings and Audit Reflections
## Finding 1 — Strong in-scope capability, but ~50% performance collapse under full coverage

In in-scope evaluation, the model achieves high recall across supported categories (avg ≈ 0.83), with near-perfect performance on EMAIL (1.0), SOCIALNUMBER (0.9979), and IDCARD (0.9529–1.0 range).

However, in full evaluation, recall drops to ~0.49–0.51 across all settings, reflecting a systematic loss of ~41.5% of ground truth spans due to unsupported label categories.

Conclusion: the model performs well only within a limited operational label space, but overall effectiveness halves when realistic PII coverage is considered.

---

## Finding 2 — Structural coverage gap dominates failure mode (not model accuracy)

The model supports 9 of 21 observed PII categories (42.9%), leaving 12 categories entirely undetected (0 TP across all samples), including:

- USERNAME (1,078)
- PASSPORT (1,019)
- DRIVERLICENSE (988)
- BOD (920)
- TIME (1,539)
- TITLE (769)

These unsupported categories account for a major portion of dataset PII and contribute directly to 8,354 FN spans in full evaluation.

Conclusion: the primary limitation is not detection quality, but missing label space coverage.

---

## Finding 3 — Precision instability concentrated in semantically ambiguous labels

While structured identifiers remain highly precise (EMAIL 0.9472, SOCIALNUMBER 1.0000, TEL 0.9046), ambiguous categories show major degradation:

- DATE precision = 0.3702 (very high FP: 1169)
- PERSON precision = 0.4457 (2193 FP)
- ADDRESS precision = 0.6355 (1540 FN, 1111 FP trade-off)

Conclusion: errors are concentrated in semantically open-ended categories, where boundary definition and context interpretation are required.

---

## Finding 4 — Model is highly robust to language variation (minimal variance)

Across six languages, in-scope F1 ranges only from:

- 0.6687 (German)
- 0.7015 (Italian)
- Δ ≈ 0.033

Full evaluation also shows near-identical degradation patterns across languages (F1 ≈ 0.50–0.55 range).

Conclusion: language is not a meaningful factor in performance variation; failures are label-structure driven rather than linguistic.

---

## Finding 5 — Domain and length effects are weak compared to label effects

Across domains, in-scope F1 varies moderately:
- Finance highest: 0.7208
- Legal lowest: 0.6515

Across text length:
- Short F1 = 0.6930
- Long F1 = 0.6821

Intersectional results show differences remain within ~0.05–0.08 range.

Conclusion: domain and length introduce only marginal variance compared to dominant label-coverage effects.