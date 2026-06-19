# 3.1 Fairness Analysis

### Reframing the Question

Treating unequal privacy protection as a fairness problem requires the same move that
fairness analysis demands of any classifier: moving from "the filter is biased" to "biased
for whom, in what way, based on what evidence, and what follows." Our results give a
concrete answer to the first three of these, and a more uncomfortable answer to the fourth.

The standard discrimination framework distinguishes disparate treatment (a system explicitly
uses a protected attribute) from disparate impact (a facially neutral policy disproportionately
harms a particular group). The OpenAI Privacy Filter applies the same model to every text regardless of who wrote it. But our results show a textbook case of the second: a single, uniformly-applied filtering policy produces sharply
unequal protection outcomes, and the inequality tracks category, not just demographic
group. This matters because treating every input the same
way — does not guarantee equal outcomes when the input space itself is structured unevenly
across groups, languages, or domains. A filter that is blind to PII *category* in this sense
behaves analogously to a model that is blind to a protected attribute: formal neutrality at
the input stage coexists with substantial disparity at the output stage.

### Which Groups, Languages, Domains, or PII Categories Receive Weaker Protection

**PII category is by far the dominant axis of unequal protection — far more than language
or domain.** Our per-category breakdown shows two effectively disjoint populations within
the same dataset:

- **The protected group:** individuals whose identifying information takes the form of
  EMAIL, TEL, PASS, DATE, STREET, GIVENNAME1, or SOCIALNUMBER. For this group, recall sits
  between 0.96 and 1.00 — protection is close to total.
- **The unprotected group:** individuals whose identifying information takes the form of
  DRIVERLICENSE, PASSPORT, USERNAME, IP, IDCARD, BOD, SEX, TIME, TITLE, GEOCOORD, POSTCODE,
  STATE, BUILDING, CITY, COUNTRY, or any LASTNAME variant. For this group, recall is exactly
  0.00. Not low — zero. These are not harder cases that the model gets wrong sometimes; they
  are categories the model was never built to recognise.

Although this might not seem like a fairness problem at first, it very much is. We must keep in mind that *which group a person falls into is not under their control and is not random*. It is determined by which jurisdiction issued their identity
documents, whether their dataset entry happens to include a date of birth field, or whether
their name structure includes a recorded second surname. A person whose only identifiers in
a given text are a driver's licence number and a date of birth receives systematically worse
treatment than a person identified by an email address and a phone number — not because of
anything about who they are, but because of which administrative category their information
happens to fall into. When this category dimension correlates with anything socially
patterned — and identity document formats, naming conventions, and administrative practices
vary considerably by country and culture — category-level unfairness becomes a vector for
group-level unfairness, even though no demographic attribute is read by the model at any
point.

**Language shows comparatively mild disparity.** F1 ranges narrowly from 0.19 (German) to
0.22 (Italian) across the six languages tested, and FNR sits within a few points of the
overall average everywhere. This is a meaningfully different finding from the category
result: it suggests the filter's failure mode is structural (a taxonomy gap) rather than
linguistic (a detection-quality gap). A naive audit that only checked language breakdowns —
the dimension most fairness audits default to — would have concluded the filter is
reasonably equitable. That conclusion would have been wrong, and only the category-level
breakdown reveals why.

**Domain shows a similar pattern to language — present but secondary.** Healthcare,
Finance, Legal Services, Education, Psychology, and Business all cluster within a roughly
10-point FNR band in the full evaluation. Legal Services performs worst (FNR 0.5604) and
Education best (FNR 0.4940), but this spread is modest next to the 0.00 vs. 1.00 split
running through the category breakdown. Crucially, every domain inherits the *same*
category-level gap, because every domain's text contains a mix of in-scope and out-of-scope
PII types. A healthcare domain document with a patient's date of birth and driver's licence
is exposed in exactly the pattern demonstrated in the error analysis, regardless of which
domain bucket it was sorted into.

**The person-name finding deserves separate attention because it shows fairness failure inside a single conceptual category, not just between categories.** The filter maps every
detected person-name span to a single internal category and, in our mapping, only the
GIVENNAME1 ground-truth label is matched. LASTNAME1, LASTNAME2, LASTNAME3, and GIVENNAME2
all sit at FNR 1.0000. Naming conventions that use multiple surnames or multiple given names
— common in many cultures outside a single-given-name-plus-single-surname Anglophone
pattern — are structurally more likely to contain name components in these uncovered slots.
This is a case where a taxonomic gap, not a demographic flag, produces a result that
plausibly tracks naming-convention diversity, again without the model ever processing a
protected attribute directly.

### Which Fairness Standard Is Most Relevant Here

Of the three standard statistical criteria, **none map cleanly onto this problem**, and
working out why is itself informative.

**Equal masking rates (independence)** would ask whether the proportion of text masked is
similar across groups. This is the wrong standard here: equal masking rates could be
trivially satisfied by a filter that masks a similar *percentage* of tokens in every group
while still systematically missing different *categories* of identifier in each group. A
filter could mask 20% of every defendant's text and still leave one group's passport
numbers and another group's licence numbers equally exposed. Masking rate is a volume
measure; it says nothing about whether the *right* things were masked.

**Equal false positive rates** are not the relevant standard either, although our results do
show FPR disparity (driven by span-splitting and label over-generalisation rather than by
any group attribute). The harm we are evaluating is not primarily about over-redaction
imposing an unequal burden across groups — though that is a real and separate cost,
documented in 2.2–2.4. The central harm in a privacy audit is exposure, not inconvenience.

**Equal false negative rates is the right standard, but it needs to be applied at the
category level, not just the group level.** The conventional fairness framing asks whether
FNR is equal across demographic groups *for a fixed outcome category* — e.g., equal miss
rates for loan default prediction across racial groups. Our case inverts the usual structure:
the "categories" doing the work are PII types, and the disparity is not a few percentage
points (the kind addressed by bias mitigation, threshold adjustment, or rebalancing) — it is
the difference between 0% and 100% miss rates. This is not a calibration problem or a
threshold-tuning problem. **Equal FNR across PII category** is the most relevant standard
precisely because the alternative standards either don't apply (sufficiency/calibration
requires a continuous risk score context that doesn't map onto entity detection) or measure
the wrong thing (independence/masking-rate).

We therefore propose that the appropriate fairness lens for this system is: **equal
false-negative-rate across PII category, with category-level FNR additionally
cross-tabulated against language, domain, and naming convention** to surface whether the
categories with structurally zero protection disproportionately affect identifiable
subpopulations. Our results show this lens is necessary, not optional — a fairness audit
that stopped at language and domain breakdowns (the dimensions most readily described as
"protected attributes" in a conventional ML fairness setting) would have missed the central
finding entirely. The unfairness here is not in how the model treats different demographic
groups directly; it is in how an apparently neutral, demographic-blind detection taxonomy
produces a near-total protection gap for some categories of identifying information and
near-total protection for others, and that gap is not visible unless category is treated as
the protected dimension.

### Reflection

There is a real risk of ethics-washing in how a result like ours could be reported. A
provider could correctly state that the filter shows no meaningful disparity across the six
languages tested, and that statement would be true and verifiable. It would also be
profoundly misleading as a fairness claim, because it answers a narrower question than the
one that matters. Choosing language as the axis of fairness evaluation — rather than PII
category — is itself a value-laden choice about which disparities count as worth measuring,
and our findings suggest that the more familiar, demographically-coded axis is not where
the actual unfairness in this system lives. A privacy filter audit that defaults to the
fairness vocabulary built for allocative-harm classifiers (loan approval, recidivism
prediction) risks asking only the questions that vocabulary was built to ask, and missing
the harm that is actually present.