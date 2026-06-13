# 2.2 OpenAI Privacy Filter Evaluation

We evaluated the OpenAI Privacy Filter (`openai/privacy-filter`) empirically on a stratified
sample of 3,000 examples drawn from the validation split of `ai4privacy/pii-masking-300k`
(500 per language: English, German, French, Spanish, Italian, Dutch; seed 42). The model was
loaded via the HuggingFace `transformers` pipeline with `trust_remote_code=True` and run on
Google Colab (T4 GPU). All predictions were collected, mapped to ai4privacy ground truth
labels, and evaluated against the `privacy_mask` field using overlap-based span matching.

The following aspects were not directly measurable and are noted as scope limitations:

- Threshold choices and confidence score calibration — not disclosed in model card
- Training data composition, fine-tuning details, and subgroup evaluation — not publicly
  available
- Intended and non-intended use cases — taken from OpenAI model card framing

---

Three methodological issues arose during evaluation, each of which required correction and
is itself a finding about the filter's transparency and output design.

**1. Label taxonomy mismatch**
The OpenAI filter outputs a proprietary label set with a lowercase `private_` prefix
convention (e.g. `private_email`, `private_person`, `secret`). This is not documented in a
way that enables direct comparison with standard NER or PII datasets. Our initial run
produced 0 TP across all 3,000 samples because the label map assumed standard labels
(`EMAIL`, `PERSON`). The correct labels were only discoverable by running the model and
logging raw output. This is a transparency failure: an organisation deploying this filter
for data preparation cannot verify its coverage without running it first.

**2. Span splitting**
The model systematically splits entity spans at subword token boundaries — for example,
`1990A@aol.com` is predicted as two spans: `1990A@aol` [215:224] and `.com` [224:228],
while the ground truth has a single span [215:228]. Without correction, the first fragment
matches the ground truth via overlap → TP, and the second fragment has no remaining
unmatched ground truth span → FP. Across 3,000 samples, 32,937 raw predicted spans were
reduced to 16,705 after merging — 16,232 merge operations in total. This halving of
predicted span count confirms that span splitting is not incidental but structural to the
model's output format.

**3. Person name and address taxonomy fragmentation**
The filter outputs a single `PRIVATE_PERSON` label for all person name tokens. The
ai4privacy dataset distinguishes GIVENNAME1, GIVENNAME2, LASTNAME1, LASTNAME2, LASTNAME3.
The original evaluation mapped `PRIVATE_PERSON → GIVENNAME1` only, causing all last name
detections to count as FP and all LASTNAME* ground truth spans to count as FN. Similarly,
`PRIVATE_ADDRESS` was mapped only to STREET, leaving CITY, STATE, POSTCODE, BUILDING, and
COUNTRY as permanent FN. Both mappings were corrected by collapsing all name variants into
a single PERSON label and all address sub-types into a single ADDRESS label before scoring.

---

**Evaluation design**

Given these issues, we ran two evaluation modes:

**In-scope evaluation** scores the model only against the PII categories it was designed to
detect. Ground truth spans belonging to unsupported labels are excluded before scoring. This
is the fair assessment of the model's performance within its intended scope.

**Full evaluation** scores the model against all 29 ground truth labels. Misses on
unsupported labels are counted as FN, producing a coverage-penalised view that reflects
real-world deployment risk rather than model capability.

The label mapping applied in both modes is as follows:

| OpenAI Filter Label | Mapped to (canonical) | Notes |
|---|---|---|
| private_email | EMAIL | Clean mapping |
| private_phone | TEL | Clean mapping |
| private_url | URL, IP | Model fires on IP addresses; both credited |
| private_date | DATE | Clean mapping |
| private_person | PERSON | All name variants collapsed |
| private_address | ADDRESS | All address sub-types collapsed |
| account_number | SOCIALNUMBER, ACCOUNTNUMBER, IDCARD, IBAN, CREDITCARDNUMBER, BITCOINADDRESS | Broad ID class |
| secret | PASS | Clean mapping |

**Sample:** 3,000 validation examples (500 per language)
**Matching strategy:** Overlap-based span matching — prediction is TP if it overlaps any
ground truth span of the same label; each GT span matched at most once; predicted spans
merged before scoring.

---

### Coverage

The filter's taxonomy covers 9 of 21 canonical label types observed in the sample (42.9%
label coverage). At the span level, 11,775 of 20,128 ground truth spans fall within
supported categories (58.5% span coverage). The 12 unsupported label types — TIME (1,539
instances), USERNAME (1,078), PASSPORT (1,019), DRIVERLICENSE (988), BOD (920), SEX (843),
TITLE (769), BUILDING (718), SECADDRESS (320), LASTNAME3 (79), GEOCOORD (79), CARDISSUER
(1) — account for the remaining 41.5% of ground truth spans and are structurally
undetectable by the filter.

### Overall

| Metric | In-scope | Full |
|---|---|---|
| TP | 9,789 | 9,789 |
| FP | 6,916 | 6,916 |
| FN | 1,986 | 10,339 |
| Precision | 0.5860 | 0.5860 |
| Recall | 0.8313 | 0.4863 |
| F1 | 0.6874 | 0.5315 |
| FNR | 0.1687 | 0.5137 |
| FPR | 0.4140 | 0.4140 |

### Per-Label Breakdown

| Label | TP | FP | FN | Precision | Recall | F1 | FNR | Scope |
|---|---|---|---|---|---|---|---|---|
| EMAIL | 1,040 | 58 | 0 | 0.9472 | **1.0000** | 0.9729 | **0.0000** | ✓ |
| SOCIALNUMBER | 944 | 0 | 2 | 1.0000 | 0.9979 | 0.9989 | 0.0021 | ✓ |
| IDCARD | 1,051 | 0 | 52 | 1.0000 | 0.9529 | 0.9759 | 0.0471 | ✓ |
| IP | 921 | 118 | 17 | 0.8864 | 0.9819 | 0.9317 | 0.0181 | ✓ |
| TEL | 825 | 87 | 3 | 0.9046 | 0.9964 | 0.9483 | 0.0036 | ✓ |
| PASS | 621 | 53 | 16 | 0.9214 | 0.9749 | 0.9474 | 0.0251 | ✓ |
| DATE | 687 | 1,169 | 17 | 0.3702 | 0.9759 | 0.5367 | 0.0241 | ✓ |
| PERSON | 1,763 | 2,193 | 339 | 0.4457 | 0.8387 | 0.5820 | 0.1613 | ✓ |
| ADDRESS | 1,937 | 1,111 | 1,540 | 0.6355 | 0.5571 | 0.5937 | 0.4429 | ✓ |
| ACCOUNTNUMBER | 0 | 2,127 | 0 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | ✓ |
| BOD | 0 | 0 | 920 | — | — | — | 1.0000 | ✗ |
| BUILDING | 0 | 0 | 718 | — | — | — | 1.0000 | ✗ |
| DRIVERLICENSE | 0 | 0 | 988 | — | — | — | 1.0000 | ✗ |
| GEOCOORD | 0 | 0 | 79 | — | — | — | 1.0000 | ✗ |
| LASTNAME3 | 0 | 0 | 79 | — | — | — | 1.0000 | ✗ |
| PASSPORT | 0 | 0 | 1,019 | — | — | — | 1.0000 | ✗ |
| SECADDRESS | 0 | 0 | 320 | — | — | — | 1.0000 | ✗ |
| SEX | 0 | 0 | 843 | — | — | — | 1.0000 | ✗ |
| TIME | 0 | 0 | 1,539 | — | — | — | 1.0000 | ✗ |
| TITLE | 0 | 0 | 769 | — | — | — | 1.0000 | ✗ |
| USERNAME | 0 | 0 | 1,078 | — | — | — | 1.0000 | ✗ |

### Per-Language Breakdown

| Language | TP | FP | FN | Precision | Recall | F1 | FNR |
|---|---|---|---|---|---|---|---|
| **In-scope** | | | | | | | |
| Dutch | 1,773 | 1,246 | 388 | 0.5873 | 0.8205 | 0.6846 | 0.1795 |
| English | 1,591 | 1,046 | 343 | 0.6033 | 0.8226 | 0.6961 | 0.1774 |
| French | 1,668 | 1,209 | 296 | 0.5798 | 0.8493 | 0.6891 | 0.1507 |
| German | 1,546 | 1,239 | 293 | 0.5551 | 0.8407 | 0.6687 | 0.1593 |
| Italian | 1,624 | 1,064 | 318 | 0.6042 | 0.8363 | 0.7015 | 0.1637 |
| Spanish | 1,587 | 1,112 | 348 | 0.5880 | 0.8202 | 0.6849 | 0.1798 |
| **Full** | | | | | | | |
| Dutch | 1,773 | 1,246 | 1,913 | 0.5873 | 0.4810 | 0.5289 | 0.5190 |
| English | 1,591 | 1,046 | 1,637 | 0.6033 | 0.4929 | 0.5425 | 0.5071 |
| French | 1,668 | 1,209 | 1,641 | 0.5798 | 0.5041 | 0.5393 | 0.4959 |
| German | 1,546 | 1,239 | 1,805 | 0.5551 | 0.4614 | 0.5039 | 0.5386 |
| Italian | 1,624 | 1,064 | 1,611 | 0.6042 | 0.5020 | 0.5484 | 0.4980 |
| Spanish | 1,587 | 1,112 | 1,732 | 0.5880 | 0.4782 | 0.5274 | 0.5218 |

---

**Finding 1 — Strong recall within scope; coverage is the binding constraint**
For the 9 label categories the filter supports, recall is consistently high. EMAIL achieves
recall of 1.0 and FNR of 0.0 — every email address in the sample is detected. SOCIALNUMBER,
IDCARD, IP, TEL, and PASS all achieve recall above 0.95. In-scope overall recall is 0.83.
The constraint is not detection sensitivity but taxonomic coverage: 41.5% of ground truth
spans belong to categories the filter cannot detect at all. The full-mode FNR of 0.51
reflects this gap directly — roughly half of all PII in the sample is structurally invisible
to the filter.

**Finding 2 — The filter covers 9 of 21 observed PII categories**
TIME (1,539 instances), USERNAME (1,078), PASSPORT (1,019), DRIVERLICENSE (988), BOD (920),
SEX (843), TITLE (769), BUILDING (718), SECADDRESS (320) — none detected. These categories
collectively account for 8,354 ground truth spans, all of which produce structural FN
regardless of model behaviour. An organisation that treats filter output as sufficient for
de-identification is making an assumption the filter's own scope does not support.

**Finding 3 — Precision varies substantially across supported categories**
EMAIL, SOCIALNUMBER, IDCARD, TEL, and PASS all achieve precision above 0.88 after span
merging. DATE and PERSON are significantly weaker: DATE precision is 0.37 (the model
over-triggers on number sequences), and PERSON precision is 0.45 (2,193 FP across 3,000
samples). ADDRESS recall is 0.56 — the model misses nearly half of address spans even within
its own scope, likely because the collapsed ADDRESS label aggregates sub-types the model
handles inconsistently.

**Finding 4 — ACCOUNTNUMBER is a broken mapping**
The `account_number` model label produces 2,127 FP and 0 TP. The model is firing on spans
the dataset does not label as any ID category. This suggests either a fundamental mismatch
between what the model considers an account number and what ai4privacy annotates, or that
the model is over-triggering on numeric sequences not annotated as PII. This label cannot
be considered functional under the current evaluation setup.

**Finding 5 — Language performance is uniform**
No significant performance gap across the six languages in either evaluation mode. The
in-scope F1 range is 0.669 (German) to 0.702 (Italian) — a spread of 0.033. This is
consistent with the filter's failure mode being taxonomic rather than linguistic: the model
misses the same categories in all six languages because they are absent from its taxonomy,
not because it fails on non-English text.

**Finding 6 — Failure against the deployment threshold**
The deployment threshold for the healthcare LLM training setting (section 1.4) was FNR <
0.1% for explicit PII. The filter achieves in-scope FNR of 0.1687 — failing by a factor of
168 even on the categories it was designed to cover. The full-mode FNR of 0.5137 reflects
the additional structural gap. The filter does not approach the threshold under either
evaluation mode.

---

An initial evaluation run mapped person name variants to a single sub-type and address
sub-types to STREET only, which artificially inflated FP and FN counts. Once corrected
via label collapsing and span merging, the results are interpretable. The model is not
generically poor — it is narrow.

The problem is precisely that narrowness. For the structured identifiers it was designed to
detect, the filter performs well. What it cannot do — and what its documentation does not
clearly communicate — is cover the majority of PII categories that appear in real multilingual
text. An organisation that deploys this filter and treats the output as de-identified retains
undetected PASSPORT numbers, DRIVERLICENSE strings, USERNAME handles, dates of birth, gender
markers, and job titles in its data. The false reassurance risk identified in section 1.1 is
empirically confirmed: the filter performs convincingly on the identifiers most people
associate with PII while leaving the remainder entirely untouched.