# 2.5 Qualitative Downstream Black-Box Check

### Method

We selected 5 examples from the 2.4 error analysis, each representing a case where the
OpenAI Privacy Filter either missed a PII entity entirely (taxonomic gap) or mislabelled
and partially redacted it. For each example we constructed three versions:

1. **Raw** — the original, unfiltered text
2. **Fully masked** — what the text would look like if every ground-truth PII span were
   correctly identified and replaced with a category placeholder (the ideal/reference case)
3. **Partly masked** — what the OpenAI Privacy Filter *actually* produced, reconstructed
   from the real predictions recorded in `false_negatives.json` / `false_positives.json`
   (Section 2.4)

Each version was passed through a downstream summarisation task, with the model treated as
a black box: we only inspect the output text, not any internal reasoning. We then check
whether identifiers missed by the filter are reproduced in the summary, and whether
over-redaction in the fully masked version meaningfully reduces output usefulness.

---

### Results

Example 1 — Username (taxonomic gap)
| Version | Summary |
|---|---|
| Raw | *"Individual B is Sir Boldbaatar Byers, a male UK resident with username qhsmlh860605, driver's licence BOLDB8111539173, passport 574222032, and phone 02304-984447, residing at two UK addresses."* |
| Fully masked | *"[PERSON] is a [PERSON] UK resident with masked username, licence, passport, and phone details, residing at a masked UK address."* |
| Partly masked (actual filter) | *"[PERSON] has username qhsmlh860605, driver's licence BOLDB8111539173, passport 574222032, residing at two UK addresses; phone number was redacted."* |

**Finding:** The partly masked summary reproduces the username, driver's licence, and
passport number verbatim — identical to the raw summary for those fields. The filter's
taxonomic gap on USERNAME (and its lack of DRIVERLICENSE/PASSPORT coverage in this sample)
propagates directly into the downstream output. Only the phone number, which the filter does
cover, was actually protected.

Example 2 — Driver's licence (mislabelled, partially redacted)
| Version | Summary |
|---|---|
| Raw | *"Two participants are listed with driver's licences MINAT 758267 9 892 and SERHA.601166.9.646, passports 368752690 and 539304343, and contact email SW@tutanota.com."* |
| Fully masked | *"Two participants are listed with masked driver's licences, passports, and contact email."* |
| Partly masked (actual filter) | *"Two participants are listed; the first has a partially redacted licence ending in 892, passport 368752690; the second has driver's licence SERHA.601166.9.646 and passport 539304343, with email redacted."* |

**Finding:** This is the clearest case of **partial masking creating a false sense of
protection while still leaking the identifier**. The first licence number is truncated
(`[SOCIALNUMBER]892` instead of full redaction) — the summary still surfaces the fragment
"ending in 892," and the second participant's licence and both passport numbers are fully
exposed. A reader of this summary could reasonably believe redaction was applied
("partially redacted") while still recovering identifying fragments.

Example 3 — Date of birth (taxonomic gap)
| Version | Summary |
|---|---|
| Raw | *"Speaker A, born 13/01/1942, and Speaker B, born 1968-06-18, are both identified with usernames K13 and 1968MT and driver's licences G06549259 and MIKAI-606188-MT-099."* |
| Fully masked | *"Speaker A and Speaker B are identified by masked birth dates, usernames, licences, phone numbers, and IP addresses."* |
| Partly masked (actual filter) | *"Speaker A, born 13/01/1942, and Speaker B, born 1968-06-18, have usernames K13 and 1968MT and licences G06549259 and MIKAI-606188-MT-099; phone numbers were redacted."* |

**Finding:** Identical exposure pattern to Example 1 — every category outside the filter's
narrow taxonomy (BOD, USERNAME, DRIVERLICENSE, IP) survives into the summary unchanged. Only
the in-scope TEL category is protected. In a healthcare context, date of birth combined with
a driver's licence number is precisely the kind of quasi-identifier combination flagged in
1.1 and 1.4 — Sweeney's (2000) finding that few attributes are needed for re-identification
applies directly here.

Example 4 — XML-structured driver's licence (taxonomic gap, ignored explicit field tag)
| Version | Summary |
|---|---|
| Raw | *"An individual with title 'Pr' holds driver's licence X096082169682, IP 5980:a44e:8df9:e8a4:1cd3:45f:1c2b:9012; phone and password also listed."* |
| Fully masked | *"An individual's title, licence, phone, IP, and password are all masked."* |
| Partly masked (actual filter) | *"An individual with title 'Pr' holds driver's licence X096082169682 and IP 5980:a44e:8df9:e8a4:1cd3:45f:1c2b:9012; phone and password were redacted."* |

**Finding:** Even with an explicit `<driverlicense>` XML tag providing an unambiguous
contextual cue, the filter does not redact the value. The summary exposes the full licence
number and IP address. This shows that the filter's gap is not a matter of insufficient
context — the context was maximally clear — but a structural absence of the category from
its label space.

Example 5 — Passport number (mislabelled, truncated)
| Version | Summary |
|---|---|
| Raw | *"Three complainants list passport numbers 570044469, 829552083, and 117925111 with US addresses in Leitchfield KY, Beeville TX, and an Arizona location."* |
| Fully masked | *"Three complainants list masked passport numbers and addresses across three US states."* |
| Partly masked (actual filter) | *"Complainant 3's passport is partly redacted (ending 469); complainants 4 and 5 list full passport numbers 829552083 and 117925111 with addresses in Beeville TX and Arizona; passwords were redacted."* |

**Finding:** Only the first of three passport numbers received any redaction at all, and
even that redaction was truncated — leaving the last three digits ("469") exposed in the
summary. The second and third passport numbers passed through completely untouched. This
demonstrates that the filter's failures are not uniform even within a single document: the
same entity type can be partially caught in one instance and missed entirely in another.

---

### Synthesis

**1. Missed identifiers are reliably repeated in downstream output.**
In all 5 examples, every PII category outside the filter's narrow taxonomy (USERNAME, BOD,
DRIVERLICENSE, PASSPORT, IP) survived unchanged from raw text through to the summarisation
output. The downstream LLM does not independently catch or redact anything the upstream
filter missed — it simply reproduces what it received. This confirms the core mechanism of
the **downstream misuse harm** identified in 1.1: a filter's failure does not stay contained
at the filtering stage, it propagates through every subsequent step of the pipeline.

**2. Partial masking can be worse than no masking, from a false-reassurance standpoint.**
In Examples 2 and 5, the truncated redaction (`[SOCIALNUMBER]892`, `[SOCIALNUMBER]469`)
produces a summary that *looks* redacted — a reader sees a placeholder token and a masking
label — while a partial fragment of the actual identifier remains visible. This is more
dangerous than a clean miss, because it actively signals "this was handled" while leaving
real information exposed.

**3. Over-masking (fully masked version) substantially reduces usefulness but is not used in practice.**
The fully masked summaries are notably less informative — in Example 3, "Speaker A and
Speaker B are identified by masked birth dates, usernames, licences..." conveys almost no
analytically useful content. This is the over-redaction harm from 1.1, but it is a
hypothetical comparison point only: the filter's actual behaviour in every tested example was
much closer to the raw text than to this idealised, fully-redacted version. In practice, the
filter trades away almost none of the over-redaction risk in exchange for almost none of the
protection benefit on these categories.

**4. The downstream check confirms the central audit finding.**
None of these five summaries would give a deploying organisation any signal that something
went wrong. The summaries read fluently and look professionally redacted, particularly
Examples 2 and 5 where partial masking is visible. An organisation relying on this filter's
output, without independently testing for taxonomic coverage as this audit has done, would
have no way to detect that driver's licence numbers, passport numbers, dates of birth, and
usernames are passing through its "privacy-filtered" pipeline into every downstream
consumer of that data — including LLM training, third-party data sharing, or human review.

### Conclusion 

The downstream black-box check demonstrates re-identification risk that has nothing to do with the filter's known taxonomic gaps. Even in the fully masked versions (where every category the filter is supposed to catch is replaced with a placeholder), the resulting summaries retain enough structural and contextual information to support identification: nationality, profession-adjacent details, document formats, the co-occurrence of a UK address with a specific licence format, or the pairing of a date of birth with an IP address block. 

None of this is a single explicit identifier; each fragment looks individually harmless, which is exactly the quasi-identifier mechanism described in Sweeney (2000) and revisited in 1.1. 