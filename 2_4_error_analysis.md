# 2.4 Error Analysis

All examples below are drawn from an empirical run of the OpenAI Privacy Filter on 100
samples from the stratified validation set, using overlap-based span matching against
ai4privacy ground truth (`error_analysis.py`). This produced 395 false negatives and 630
false positives, from which we selected representative cases covering both under-redaction
and over-redaction failure modes.

---

### Under-Redaction Examples (Missed PII)

Example 1 — USERNAME completely missed
> *"...Gender: Masculine — Username: **qhsmlh860605** — Driver's License: BOLDB8111539173..."*

**Ground truth:** `USERNAME`, span [222:234], value `qhsmlh860605`
**Filter output:** No prediction for this span at all.
**Likely source:** Dataset limitation / taxonomic narrowness. USERNAME is not a category the
filter's label set covers (confirmed: USERNAME never appears in the filter's raw output
labels across the full 3,000-sample run). This is not a detection failure on a hard case —
it is a structural gap in what the model was built to recognise.

Example 2 — Driver's licence number missed (and misclassified)
> *"...Driver's License: **MINAT 758267 9 892** — Passport: 368752690..."*

**Ground truth:** `DRIVERLICENSE`, span [33:51], value `MINAT 758267 9 892`
**Filter output:** No `DRIVERLICENSE` prediction. Instead, the filter predicted `SOCIALNUMBER`
over a near-identical span [32:48], value ` MINAT 758267 9 `.
**Likely source:** Label mismatch combined with context dependence. The model recognises the
span as *some* kind of structured identifier (high confidence) but has no DRIVERLICENSE
category to assign it to, so it defaults to SOCIALNUMBER — the closest category in its
taxonomy. This produces a false negative on DRIVERLICENSE and a false positive on
SOCIALNUMBER simultaneously, from the same span.

Example 3 — Date of birth missed entirely
> *"...Date of Birth: **13/01/1942** — Username: K13..."*

**Ground truth:** `BOD`, span [27:37], value `13/01/1942`
**Filter output:** No prediction. The adjacent `Username: K13` was also missed, but the
filter did predict `PERSON` for the fragment ` K` [52:54] — a separate, unrelated error.
**Likely source:** Dataset limitation / taxonomic narrowness. BOD (date of birth) is
semantically a DATE, but the filter does not generalise PRIVATE_DATE detection to dates in
a "Date of Birth:" labelled field — suggesting the model relies partly on format pattern
matching rather than full contextual understanding of field semantics.

Example 4 — Driver's licence in structured/XML-like text
> *"...&lt;title&gt;Pr&lt;/title&gt; &lt;driverlicense&gt;**X096082169682**&lt;/driverlicense&gt;..."*

**Ground truth:** `DRIVERLICENSE`, span [236:249], value `X096082169682`
**Filter output:** No DRIVERLICENSE prediction. (The filter did separately mis-tag the title
fragment `Pr` as `PERSON`.)
**Likely source:** Pattern difficulty combined with taxonomic gap. The structured/markup
context (explicit `<driverlicense>` tags) gives an unusually strong contextual cue that the
model still fails to exploit — reinforcing that the miss is about the model's label space,
not its ability to read context.

Example 5 — Passport number missed (and misclassified)
> *"...Passport Number: **570044469** — Country: US — Building Number: 902..."*

**Ground truth:** `PASSPORT`, span [31:40], value `570044469`
**Filter output:** No PASSPORT prediction. Instead `SOCIALNUMBER` was predicted over the
truncated span [31:37], value `570044`.
**Likely source:** Label mismatch and pattern difficulty combined. As with Example 2, the
model detects *a* numeric identifier but assigns the nearest available label
(SOCIALNUMBER) rather than the correct one, and additionally truncates the span — losing
the final three digits of the actual passport number.

---

### Over-Redaction Examples (False Positives)

Example 6 — Username fragment mislabelled as PERSON
> *"...Username: **qhsmlh860**605..."* (filter span ends mid-string)

**Prediction:** `PERSON`, span [221:231], value ` qhsmlh860`
**Ground truth at this location:** `USERNAME` (see Example 1) — no PERSON entity exists here
at all.
**Likely source:** Ambiguity and pattern difficulty. The model appears to apply a generic
"looks like an identifier token" heuristic that misfires on alphanumeric usernames,
labelling them as PERSON. Combined with subword span-splitting (see 2.2 notes), this
produces a confidently-scored but semantically wrong prediction.

Example 7 — Driver's licence span mislabelled as SOCIALNUMBER
> *"...Driver's License: **MINAT 758267 9 892**..."*

**Prediction:** `SOCIALNUMBER`, span [32:48], value ` MINAT 758267 9 `
**Ground truth at this location:** `DRIVERLICENSE` (see Example 2).
**Likely source:** Label mismatch — this is the same underlying span as Example 2, viewed
from the opposite direction. The filter is not "missing" this entity in the sense of failing
to notice it; it notices it, masks it, but mislabels it. This matters operationally: in a
real deployment the text *would* be redacted, so from a pure exposure standpoint this case is
less severe than Examples 1, 3, and 4 — but it still demonstrates the taxonomy gap directly.

Example 8 — Single-character title fragment mislabelled as PERSON
> *"...&lt;title&gt;**Pr**&lt;/title&gt;..."*

**Prediction:** `PERSON`, span [194:196], value `Pr`
**Ground truth at this location:** `TITLE`, value `Pr` (an abbreviated title, e.g. "Professor").
**Likely source:** Ambiguity. A two-character token with no surrounding sentence context is
inherently hard to classify correctly; the model defaults to PERSON, which is its
highest-confidence "human-related" category. This is a low-severity over-redaction case —
both the correct and predicted labels would result in masking — but it illustrates the
model's tendency to collapse distinct human-identity categories (TITLE, PERSON, USERNAME)
into a single PERSON bucket.

---

### Summary of Error Sources

| Error Source | Examples | Pattern |
|---|---|---|
| **Taxonomic narrowness / dataset limitation** | 1, 3, 4 | Entity type (USERNAME, BOD, DRIVERLICENSE) simply has no corresponding label in the filter's output space |
| **Label mismatch** | 2, 5, 7 | Filter detects *something* sensitive at the right location but assigns the wrong category — same span counted as both FN (wrong category missed) and FP (wrong category predicted) |
| **Ambiguity / pattern difficulty** | 6, 8 | Short or context-poor tokens get defaulted to a high-confidence generic category (PERSON) regardless of actual content |
| **Context dependence** | 3, 4 | Strong contextual cues (explicit field labels, XML-like tags) are not exploited even when present |

**The most operationally significant pattern is the label-mismatch cases (2, 5, 7).** These
are not failures of detection — the filter clearly recognises that *something* sensitive is
present — but failures of taxonomy. A downstream pipeline that filters on the OpenAI Privacy
Filter's output would have these spans masked, but logged or reported under the wrong PII
category, which has consequences for any compliance process that relies on knowing *what
kind* of data was removed (e.g. breach notification requirements that differ by data type
under GDPR Article 33).

The taxonomic-narrowness cases (1, 3, 4) are more severe: the PII is not masked at all,
and survives unchanged into any downstream use of the filtered text. These are the cases
carried forward into the 2.5 downstream black-box check.