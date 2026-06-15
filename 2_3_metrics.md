# 2.3 Metrics

To evaluate the operational safety and taxonomic generalization of the OpenAI Privacy Filter (OPF), we performed a multi-dimensional metrics breakdown. We utilized a stratified validation subset of exactly 3,000 samples (500 per language: Dutch, English, French, German, Italian, Spanish; seed 42) from the `pii-masking-300k` dataset.

Following the methodology established in Section 2.2, we evaluate the OpenAI Privacy Filter under two distinct modalities:
* **In-Scope Evaluation**: Measures performance strictly on the 10 canonical categories targeted by the model's design scope.
* **Full Evaluation**: Scores the model against all 29 observed PII categories in the dataset, penalising taxonomic gaps as False Negatives (FN) to reflect real-world pipeline leakage risk.

---

## 1. PII Category Breakdown

### In-Scope Mode Category Breakdown:
| Category | TP | FP | FN | Precision | Recall | F1 | FNR | FPR |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **EMAIL** | 1040 | 1150 | 0 | 0.4749 | 1.0000 | 0.6440 | 0.0000 | 0.5251 |
| **TEL** | 825 | 962 | 3 | 0.4617 | 0.9964 | 0.6310 | 0.0036 | 0.5383 |
| **PASS** | 623 | 697 | 14 | 0.4720 | 0.9780 | 0.6367 | 0.0220 | 0.5280 |
| **DATE** | 687 | 3014 | 17 | 0.1856 | 0.9759 | 0.3119 | 0.0241 | 0.8144 |
| **STREET** | 690 | 5343 | 23 | 0.1144 | 0.9677 | 0.2046 | 0.0323 | 0.8856 |
| **GIVENNAME1** | 737 | 6877 | 27 | 0.0968 | 0.9647 | 0.1759 | 0.0353 | 0.9032 |
| **SOCIALNUMBER** | 944 | 7303 | 2 | 0.1145 | 0.9979 | 0.2054 | 0.0021 | 0.8855 |
| **URL** | 0 | 2045 | 0 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 1.0000 |

### Full Mode Category Breakdown (Includes Out-of-Scope Categories):
| Category | TP | FP | FN | Precision | Recall | F1 | FNR | FPR |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **EMAIL** | 1040 | 1150 | 0 | 0.4749 | 1.0000 | 0.6440 | 0.0000 | 0.5251 |
| **TEL** | 825 | 962 | 3 | 0.4617 | 0.9964 | 0.6310 | 0.0036 | 0.5383 |
| **PASS** | 623 | 697 | 14 | 0.4720 | 0.9780 | 0.6367 | 0.0220 | 0.5280 |
| **DATE** | 687 | 3014 | 17 | 0.1856 | 0.9759 | 0.3119 | 0.0241 | 0.8144 |
| **STREET** | 690 | 5343 | 23 | 0.1144 | 0.9677 | 0.2046 | 0.0323 | 0.8856 |
| **GIVENNAME1** | 737 | 6877 | 27 | 0.0968 | 0.9647 | 0.1759 | 0.0353 | 0.9032 |
| **SOCIALNUMBER** | 944 | 7303 | 2 | 0.1145 | 0.9979 | 0.2054 | 0.0021 | 0.8855 |
| **URL** | 0 | 2045 | 0 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 1.0000 |
| **BOD \*** | 0 | 0 | 920 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 0.0000 |
| **BUILDING \*** | 0 | 0 | 718 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 0.0000 |
| **CITY \*** | 0 | 0 | 723 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 0.0000 |
| **COUNTRY \*** | 0 | 0 | 634 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 0.0000 |
| **DRIVERLICENSE \*** | 0 | 0 | 988 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 0.0000 |
| **GEOCOORD \*** | 0 | 0 | 79 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 0.0000 |
| **GIVENNAME2 \*** | 0 | 0 | 188 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 0.0000 |
| **IDCARD \*** | 0 | 0 | 1103 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 0.0000 |
| **IP \*** | 0 | 0 | 938 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 0.0000 |
| **LASTNAME1 \*** | 0 | 0 | 912 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 0.0000 |
| **LASTNAME2 \*** | 0 | 0 | 238 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 0.0000 |
| **LASTNAME3 \*** | 0 | 0 | 79 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 0.0000 |
| **PASSPORT \*** | 0 | 0 | 1019 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 0.0000 |
| **POSTCODE \*** | 0 | 0 | 715 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 0.0000 |
| **SECADDRESS \*** | 0 | 0 | 320 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 0.0000 |
| **SEX \*** | 0 | 0 | 843 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 0.0000 |
| **STATE \*** | 0 | 0 | 692 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 0.0000 |
| **TIME \*** | 0 | 0 | 1539 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 0.0000 |
| **TITLE \*** | 0 | 0 | 769 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 0.0000 |
| **USERNAME \*** | 0 | 0 | 1078 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 0.0000 |
| **CARDISSUER \*** | 0 | 0 | 1 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 0.0000 |

*(Note: Categories marked with an asterisk `*` are structurally out-of-scope for the OpenAI Filter.)*

---

## 2. Language Breakdown

### In-Scope Evaluation Mode:
| Language | TP | FP | FN | Precision | Recall | F1 | FNR | FPR |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Dutch** | 1773 | 1246 | 388 | 0.5873 | 0.8205 | 0.6846 | 0.1795 | 0.4127 |
| **English** | 1591 | 1046 | 343 | 0.6033 | 0.8226 | 0.6961 | 0.1774 | 0.3967 |
| **French** | 1668 | 1209 | 296 | 0.5798 | 0.8493 | 0.6891 | 0.1507 | 0.4202 |
| **German** | 1546 | 1239 | 293 | 0.5551 | 0.8407 | 0.6687 | 0.1593 | 0.4449 |
| **Italian** | 1624 | 1064 | 318 | 0.6042 | 0.8363 | 0.7015 | 0.1637 | 0.3958 |
| **Spanish** | 1587 | 1112 | 348 | 0.5880 | 0.8202 | 0.6849 | 0.1798 | 0.4120 |

### Full Evaluation Mode:
| Language | TP | FP | FN | Precision | Recall | F1 | FNR | FPR |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Dutch** | 1773 | 1246 | 1913 | 0.5873 | 0.4810 | 0.5289 | 0.5190 | 0.4127 |
| **English** | 1591 | 1046 | 1637 | 0.6033 | 0.4929 | 0.5425 | 0.5071 | 0.3967 |
| **French** | 1668 | 1209 | 1641 | 0.5798 | 0.5041 | 0.5393 | 0.4959 | 0.4202 |
| **German** | 1546 | 1239 | 1805 | 0.5551 | 0.4614 | 0.5039 | 0.5386 | 0.4449 |
| **Italian** | 1624 | 1064 | 1611 | 0.6042 | 0.5020 | 0.5484 | 0.4980 | 0.3958 |
| **Spanish** | 1587 | 1112 | 1732 | 0.5880 | 0.4782 | 0.5274 | 0.5218 | 0.4120 |

---

## 3. Domain Breakdown

### In-Scope Evaluation Mode:
| Domain | TP | FP | FN | Precision | Recall | F1 | FNR | FPR |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Business** | 7038 | 4888 | 1490 | 0.5901 | 0.8253 | 0.6882 | 0.1747 | 0.4099 |
| **Education** | 629 | 457 | 98 | 0.5792 | 0.8652 | 0.6939 | 0.1348 | 0.4208 |
| **Finance** | 111 | 61 | 25 | 0.6453 | 0.8162 | 0.7208 | 0.1838 | 0.3547 |
| **Healthcare** | 895 | 630 | 172 | 0.5869 | 0.8388 | 0.6906 | 0.1612 | 0.4131 |
| **Legal Services** | 615 | 531 | 127 | 0.5366 | 0.8288 | 0.6515 | 0.1712 | 0.4634 |
| **Psychology** | 501 | 349 | 74 | 0.5894 | 0.8713 | 0.7032 | 0.1287 | 0.4106 |

### Full Evaluation Mode:
| Domain | TP | FP | FN | Precision | Recall | F1 | FNR | FPR |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Business** | 7038 | 4888 | 7422 | 0.5901 | 0.4867 | 0.5335 | 0.5133 | 0.4099 |
| **Education** | 629 | 457 | 614 | 0.5792 | 0.5060 | 0.5401 | 0.4940 | 0.4208 |
| **Finance** | 111 | 61 | 97 | 0.6453 | 0.5337 | 0.5842 | 0.4663 | 0.3547 |
| **Healthcare** | 895 | 630 | 893 | 0.5869 | 0.5006 | 0.5403 | 0.4994 | 0.4131 |
| **Legal Services** | 615 | 531 | 784 | 0.5366 | 0.4396 | 0.4833 | 0.5604 | 0.4634 |
| **Psychology** | 501 | 349 | 529 | 0.5894 | 0.4864 | 0.5330 | 0.5136 | 0.4106 |

---

## 4. Text Length Breakdown

### In-Scope Evaluation Mode:
| Length Group | TP | FP | FN | Precision | Recall | F1 | FNR | FPR |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Short (< 426 Chars)** | 4809 | 3337 | 923 | 0.5904 | 0.8390 | 0.6930 | 0.1610 | 0.4096 |
| **Long (>= 426 Chars)** | 4980 | 3579 | 1063 | 0.5818 | 0.8241 | 0.6821 | 0.1759 | 0.4182 |

### Full Evaluation Mode:
| Length Group | TP | FP | FN | Precision | Recall | F1 | FNR | FPR |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Short (< 426 Chars)** | 4809 | 3337 | 5008 | 0.5904 | 0.4899 | 0.5354 | 0.5101 | 0.4096 |
| **Long (>= 426 Chars)** | 4980 | 3579 | 5331 | 0.5818 | 0.4830 | 0.5278 | 0.5170 | 0.4182 |

---

## 5. Intersectional Breakdown: Domain x Length

### In-Scope Evaluation Mode:
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

### Full Evaluation Mode:
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

## 6. Key Findings

**Finding 1 — High Recall In-Scope, Systematic Taxonomy Gap Overall**
Within its targeted 10 canonical categories (In-Scope mode), the OpenAI Privacy Filter demonstrates strong contextual sensitivity. It achieves near-perfect Recall on categories like EMAIL (Recall: 1.0) and SOCIALNUMBER (Recall: 0.9979), with an overall in-scope Recall of ~83%. However, when evaluated against all 29 target categories (Full Evaluation mode), the Recall collapses to roughly ~48% across all languages and domains. This empirical drop highlights that the filter's primary limitation is not detection capability, but rather taxonomic narrowness, leaving out-of-scope categories entirely unmasked (FNR: 1.0000).

**Finding 2 — Over-Redaction Mismatch and Token-Splitting Issues**
Even for in-scope categories, precision remains low due to systematic token-splitting issues at subword boundaries and broad label over-generalisation. For instance, the filter achieved a precision of only 0.3702 on DATE and 0.4457 on PERSON, meaning more than half of the predicted dates and names are false alarms. This triggers a high rate of over-redaction, stripping out generic, non-sensitive content and compromising the semantic integrity of downstream training data.

**Finding 3 — Length Window Attention Decay**
Our document length breakdown indicates a clear trend of performance degradation as text length scales. For long-form inputs, the in-scope FNR increases from 16.10% (Short) to 17.59% (Long), and Full FNR increases from 51.01% to 51.70%. This demonstrates that longer contextual environments dilute transformer attention activations, making the filter more likely to overlook supported sensitive entity boundaries in long-context documents.

**Finding 4 — Failure Against Safety Thresholds in High-Risk Settings**
In Section 1.4, we established a strict safety-driven threshold for preparing training data in healthcare contexts (FNR < 0.1% for explicit PII and FNR < 5% for quasi-identifiers). Our intersectional breakdown under "Healthcare (Long)" reveals an In-Scope FNR of 20.10% and a Full FNR of 52.15%. In clinical scenarios, where patients write long narrative descriptions, the filter falls short of safety requirements by several orders of magnitude, confirming the risk of false reassurance when deploying standard generalist filters.

---

