# 2.1 Baselines


For the baseline, we implemented a **regex-based PII detector** covering the five categories specified in the project brief: email addresses, phone numbers, URLs, dates, and IBAN-like strings. We deliberately chose not to add Presidio or spaCy as a second baseline, the regex baseline is sufficient to establish a lower-bound comparison against the OpenAI Privacy Filter, and the audit's core argument concerns quasi-identifiers and linguistic fingerprinting, which neither regex nor Presidio can detect.


The baseline is implemented in `baseline.py` and operates as follows:

**Regex patterns defined:**

| Label | Pattern coverage |
|---|---|
| EMAIL | Standard email format: `local@domain.tld` |
| PHONE | Digit sequences of 7–15 characters including optional `+`, spaces, dashes, parentheses |
| URL | `http://` or `https://` followed by non-whitespace characters |
| DATE | Common date formats: `DD/MM/YYYY`, `YYYY-MM-DD`, and variants using `/`, `-`, `.` separators |
| IBAN | Two uppercase letters followed by two digits and up to 30 alphanumeric characters |

**Evaluation method:**

- Loaded `sample.jsonl` (3,000 stratified examples, 500 per language, seed 42)
- Ground truth taken from the `privacy_mask` field — character-level spans with `{value, start, end, label}`
- Ground truth filtered to only the five labels the regex covers — labels outside this set (e.g. NAME, USERNAME) were excluded to avoid artificially inflating false negatives
- **Exact span + exact label matching** for TP: a prediction is a TP only if both the character boundaries and the label match the ground truth exactly
- Metrics computed: Precision, Recall, F1, FNR, FPR — at overall, per-label, and per-language level
- Results saved to `baseline_results.csv` and `baseline_results.md`

**The results were as follows:**

### Overall
| Metric | Value |
|---|---|
| TP | 1220 |
| FP | 4242 |
| FN | 524 |
| Precision | 0.2234 |
| Recall | 0.6995 |
| F1 | 0.3386 |
| FNR | 0.3005 |
| FPR | 0.7766 |

### Per-Label Breakdown
| Label | TP | FP | FN | Precision | Recall | F1 | FNR |
|---|---|---|---|---|---|---|---|
| DATE | 245 | 691 | 459 | 0.2618 | 0.3480 | 0.2988 | 0.6520 |
| EMAIL | 975 | 77 | 65 | 0.9268 | 0.9375 | 0.9321 | 0.0625 |
| IBAN | 0 | 297 | 0 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| PHONE | 0 | 3177 | 0 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |

### Per-Language Breakdown
| Language | TP | FP | FN | Precision | Recall | F1 | FNR |
|---|---|---|---|---|---|---|---|
| Dutch | 205 | 654 | 93 | 0.2386 | 0.6879 | 0.3544 | 0.3121 |
| English | 211 | 845 | 79 | 0.1998 | 0.7276 | 0.3135 | 0.2724 |
| French | 217 | 719 | 86 | 0.2318 | 0.7162 | 0.3503 | 0.2838 |
| German | 189 | 655 | 88 | 0.2239 | 0.6823 | 0.3372 | 0.3177 |
| Italian | 206 | 656 | 85 | 0.2390 | 0.7079 | 0.3573 | 0.2921 |
| Spanish | 192 | 713 | 93 | 0.2122 | 0.6737 | 0.3227 | 0.3263 |

**We observed the following:**

*EMAIL* is the only label performing well (F1 0.93). Regex is well-suited to structured, format-predictable identifiers — email addresses follow a consistent pattern across all six languages, explaining the strong and language-uniform result.

*PHONE* produced 3,177 false positives and 0 true positives. The regex pattern is too permissive — it fires on any digit sequence of sufficient length, matching numeric strings that are not phone numbers in the dataset. This is a known limitation of pattern-based phone detection: phone number formats vary significantly across countries and the regex cannot distinguish phone numbers from other numeric sequences without contextual understanding. This is a concrete example of **over-redaction**: the baseline would mask large amounts of non-sensitive content.

*IBAN* produced 297 predictions but 0 true positives. The pattern fires but span boundaries do not align with ground truth labels — either the dataset annotates IBAN spans differently, or the regex is capturing surrounding characters. Requires manual inspection of examples.

*DATE* shows poor precision (0.26) — the regex over-fires on non-PII numeric patterns (e.g. version numbers, IDs). Recall is also low (0.35), indicating many date formats in the dataset fall outside the regex's coverage.

*Language performance is uniform* — no significant gap across the six languages, which is expected: regex patterns are language-agnostic and operate purely on character structure.

*URL* defined in the regex pattern set but produced 0 predictions and 0 ground truth matches in the sample. The ai4privacy validation split does not appear to contain URL-labelled entities, or they appear under a different label. No performance can be reported for this category.

**We also observed limitations such as:**

- Regex cannot detect NAME, USERNAME, ADDRESS, SSN, PASSPORT, or any semantically-defined PII category — these account for a large share of ground truth labels and are entirely outside the baseline's scope
- No contextual understanding — the baseline treats each token in isolation, unable to use surrounding text to disambiguate PII from non-PII
- By design, the baseline cannot detect quasi-identifiers or linguistic fingerprints — this is not a failure of the baseline but a fundamental limitation of the pattern-matching paradigm, and is central to this audit's argument
