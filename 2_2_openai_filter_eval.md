# 2.2 OpenAI Privacy Filter Evaluation

We evaluated the OpenAI Privacy Filter (`openai/privacy-filter`) empirically on a stratified
sample of 3,000 examples drawn from the validation split of `ai4privacy/pii-masking-300k`
(500 per language: English, German, French, Spanish, Italian, Dutch; seed 42). The model was
loaded via the HuggingFace `transformers` pipeline with `trust_remote_code=True` and run on
Google Colab (T4 GPU). All predictions were collected, mapped to ai4privacy ground truth
labels, and evaluated against the `privacy_mask` field using overlap-based span matching.


- Performance on PII categories outside the filter's taxonomy (BOD, IP, DRIVERLICENSE,
  PASSPORT, USERNAME, IDCARD, SEX, TIME, TITLE, GEOCOORD, POSTCODE, STATE, BUILDING,
  CITY, COUNTRY, SECADDRESS, CARDISSUER) — confirmed absent from model output, analysed
  via model card
- Threshold choices and confidence score calibration — not disclosed in model card
- Training data composition, fine-tuning details, and subgroup evaluation — not publicly
  available
- Intended and non-intended use cases — taken from OpenAI model card framing

---

Three issues arose during evaluation, each of which is itself a finding:

**1. Label taxonomy mismatch**
The OpenAI filter outputs a proprietary label set with lowercase `private_` prefix convention
(e.g. `private_email`, `private_person`, `secret`). This is not documented in a way that
enables direct comparison with standard NER or PII datasets. Our initial run produced 0 TP
across all 3,000 samples because the label map assumed standard labels (`EMAIL`, `PERSON`).
The correct labels were only discoverable by running the model and logging raw output.
This is a transparency failure: an organisation deploying this filter for data preparation
cannot verify its coverage without running it first.

**2. Span splitting**
The model systematically splits entity spans at subword token boundaries — for example,
`1990A@aol.com` is predicted as two spans: `1990A@aol` [215:224] and `.com` [224:228],
while the ground truth has a single span [215:228]. The first fragment matches the ground
truth via overlap → TP. The second fragment has no remaining unmatched ground truth span →
FP. This inflates FP counts and artificially depresses precision across all categories.
We switched from exact span matching to overlap-based matching to handle this, but the
systematic splitting remains a real limitation of the filter's output format.

**3. Person name taxonomy fragmentation**
The filter outputs a single `PRIVATE_PERSON` label for all person name tokens. The ai4privacy
dataset distinguishes GIVENNAME1, GIVENNAME2, LASTNAME1, LASTNAME2, LASTNAME3. We mapped
`PRIVATE_PERSON` → `GIVENNAME1` only. This means all last name detections count as FP
(wrong label) and all LASTNAME* ground truth spans count as FN (no matching prediction).
This mapping is best-effort and cannot be resolved without token-level disambiguation from
the model, which it does not provide.

---

| OpenAI Filter Label | Mapped to (ai4privacy) | Notes |
|---|---|---|
| private_email | EMAIL | Clean mapping |
| private_phone | TEL | Clean mapping |
| private_url | URL | Maps to URL but model fires on IP addresses too |
| private_date | DATE | Clean mapping |
| private_person | GIVENNAME1 | Partial — LASTNAME* not covered |
| private_address | STREET | Partial — CITY, STATE, POSTCODE, BUILDING not covered |
| account_number | SOCIALNUMBER | Approximate — model uses for IDs, SSNs, licence numbers |
| secret | PASS | Clean mapping |

---


**Sample:** 3,000 validation examples (500 per language)
**Matching strategy:** Overlap-based span matching — prediction is TP if it overlaps any
ground truth span of the same label; each GT span matched at most once.

### Overall

| Metric | Value |
|---|---|
| TP | 5,546 |
| FP | 27,391 |
| FN | 14,582 |
| Precision | 0.1684 |
| Recall | 0.2755 |
| F1 | 0.2090 |
| FNR | 0.7245 |
| FPR | 0.8316 |

### Per-Label Breakdown

| Label | TP | FP | FN | Precision | Recall | F1 | FNR |
|---|---|---|---|---|---|---|---|
| EMAIL | 1040 | 1150 | 0 | 0.4749 | **1.0000** | 0.6440 | **0.0000** |
| TEL | 825 | 962 | 3 | 0.4617 | **0.9964** | 0.6310 | 0.0036 |
| PASS | 623 | 697 | 14 | 0.4720 | **0.9780** | 0.6367 | 0.0220 |
| DATE | 687 | 3014 | 17 | 0.1856 | **0.9759** | 0.3119 | 0.0241 |
| STREET | 690 | 5343 | 23 | 0.1144 | 0.9677 | 0.2046 | 0.0323 |
| GIVENNAME1 | 737 | 6877 | 27 | 0.0968 | 0.9647 | 0.1759 | 0.0353 |
| SOCIALNUMBER | 944 | 7303 | 2 | 0.1145 | **0.9979** | 0.2054 | 0.0021 |
| URL | 0 | 2045 | 0 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| BOD | 0 | 0 | 920 | — | — | — | **1.0000** |
| BUILDING | 0 | 0 | 718 | — | — | — | **1.0000** |
| CITY | 0 | 0 | 723 | — | — | — | **1.0000** |
| COUNTRY | 0 | 0 | 634 | — | — | — | **1.0000** |
| DRIVERLICENSE | 0 | 0 | 988 | — | — | — | **1.0000** |
| GEOCOORD | 0 | 0 | 79 | — | — | — | **1.0000** |
| GIVENNAME2 | 0 | 0 | 188 | — | — | — | **1.0000** |
| IDCARD | 0 | 0 | 1103 | — | — | — | **1.0000** |
| IP | 0 | 0 | 938 | — | — | — | **1.0000** |
| LASTNAME1 | 0 | 0 | 912 | — | — | — | **1.0000** |
| LASTNAME2 | 0 | 0 | 238 | — | — | — | **1.0000** |
| LASTNAME3 | 0 | 0 | 79 | — | — | — | **1.0000** |
| PASSPORT | 0 | 0 | 1019 | — | — | — | **1.0000** |
| POSTCODE | 0 | 0 | 715 | — | — | — | **1.0000** |
| SECADDRESS | 0 | 0 | 320 | — | — | — | **1.0000** |
| SEX | 0 | 0 | 843 | — | — | — | **1.0000** |
| STATE | 0 | 0 | 692 | — | — | — | **1.0000** |
| TIME | 0 | 0 | 1539 | — | — | — | **1.0000** |
| TITLE | 0 | 0 | 769 | — | — | — | **1.0000** |
| USERNAME | 0 | 0 | 1078 | — | — | — | **1.0000** |
| CARDISSUER | 0 | 0 | 1 | — | — | — | **1.0000** |

### Per-Language Breakdown

| Language | TP | FP | FN | Precision | Recall | F1 | FNR |
|---|---|---|---|---|---|---|---|
| Dutch | 1044 | 4789 | 2642 | 0.1790 | 0.2832 | 0.2194 | 0.7168 |
| English | 893 | 4342 | 2335 | 0.1706 | 0.2766 | 0.2110 | 0.7234 |
| French | 917 | 4753 | 2392 | 0.1617 | 0.2771 | 0.2043 | 0.7229 |
| German | 842 | 4604 | 2509 | 0.1546 | 0.2513 | 0.1914 | 0.7487 |
| Italian | 927 | 4429 | 2308 | 0.1731 | 0.2866 | 0.2158 | 0.7134 |
| Spanish | 923 | 4474 | 2396 | 0.1710 | 0.2781 | 0.2118 | 0.7219 |

---


**Finding 1 — Near-perfect recall on structured identifiers, catastrophic miss rate overall**
For the 7 label categories the filter covers (EMAIL, TEL, PASS, DATE, STREET, GIVENNAME1,
SOCIALNUMBER), recall is consistently above 0.96. EMAIL achieves recall of 1.0 and FNR of
0.0 — every email in the sample is detected. However, 22 out of 29 ground truth categories
have 0 TP. The overall FNR is 0.7245 — 72% of all PII entities in the sample are missed
entirely.

**Finding 2 — The filter covers 7 of 29 PII categories**
DRIVERLICENSE (988 instances), PASSPORT (1019), USERNAME (1078), IP (938), IDCARD (1103),
BOD (920), TIME (1539), TITLE (769), SEX (843), POSTCODE (715), CITY (723), COUNTRY (634),
STATE (692), BUILDING (718), LASTNAME1/2/3 (1229 combined) — all completely undetected.
These represent the majority of ground truth entities in the sample.

**Finding 3 — Precision is low due to span splitting and label over-generalisation**
The filter splits entity spans at subword boundaries, producing multiple predictions per
ground truth span. This inflates FP counts: GIVENNAME1 has 6,877 FP, SOCIALNUMBER 7,303 FP,
STREET 5,343 FP. The filter also over-generalises PRIVATE_ADDRESS to cover building numbers,
postcodes, and city names — all labelled STREET, generating FP against BUILDING, CITY,
STATE, POSTCODE ground truth.

**Finding 4 — URL label is a complete mismatch**
2,045 URL predictions, 0 TP. The model maps IP addresses to `private_url` but the dataset
labels them as IP. This is a pure label taxonomy mismatch with no resolution under the
current mapping.

**Finding 5 — Language performance is uniform**
No significant performance gap across the 6 languages. German is marginally worse (F1 0.19
vs 0.21 average) but the difference is small. This is expected given the filter's failure
mode is categorical coverage, not language-specific pattern recognition.

**Finding 6 — Failure against our 1.4 threshold**
Our pre-registered threshold for the healthcare LLM training setting was FNR < 0.1% for
explicit PII. The filter achieves FNR of 0.7245 overall — failing by a factor of 700. Even
for its best-covered category (EMAIL, FNR = 0.0), the precision of 0.47 means nearly half
of all email detections are false positives, creating over-redaction problems for downstream
use.

---

The results reveal a fundamental mismatch between the filter's design scope and the
deployment assumptions organisations may bring to it. For the narrow set of structured
identifiers it was designed to detect (email, phone, password, date, address fragments,
person names), the filter achieves near-perfect recall. This is technically impressive and
confirms the filter works as designed within its intended scope.

The problem is not the filter's performance within its scope — it is the gap between that
scope and what a typical organisation would need for a PII filtering deployment to be
considered adequate. 22 of 29 PII categories in a standard multilingual dataset are entirely
outside the filter's taxonomy. An organisation that runs data through this filter and treats
the output as "de-identified" is making an assumption the filter cannot support.

This is precisely the false reassurance harm identified in 1.1: the filter performs
convincingly on the identifiers most people think of as PII (emails, phone numbers, names),
while leaving behind large volumes of other identifying information (passport numbers, driver
licences, IP addresses, usernames, dates of birth, job titles, gender markers) entirely
untouched.