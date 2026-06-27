# 3.6 Assessing the Claim: "Running Data Through a Privacy Filter Before Training an LLM Is Sufficient Privacy Protection"

*Note: as in our previous section, "Section X" below refers to the OpenAI Privacy Filter model card. References to our own report are written out by name.*

### The Claim

The claim under review is a sufficiency claim, not a usefulness claim. It says that pre-training filtering closes the privacy question — that once PII has been stripped from a corpus, the resulting training process and resulting model carry no further privacy exposure that organizations need to manage. This is a much stronger statement than "filtering reduces privacy risk," which our project does not dispute. Our own results, and the broader literature on LLM memorization, both point to the same conclusion: the claim is false in several independent ways that compound rather than substitute for each other. Even a hypothetically perfect filter — one with zero false negatives — would not make the claim true, because several of the risks below do not originate in what the filter missed at all.

### 1. False Negatives: The Filter Itself Does Not Catch Everything

This is the most direct way the claim fails, and it is the one this project measured most thoroughly. Our metrics found an overall false-negative rate of 72.45% across the dataset's 29 PII categories, with 22 of those categories detected at exactly 0% recall — not a low rate, a structural absence of coverage. Categories like DRIVERLICENSE, PASSPORT, USERNAME, and IDCARD were missed in every single instance we tested. 

If a filtered corpus still contains thousands of unredacted passport numbers, driver's license numbers, and birth dates, then "running data through the filter" did not produce a PII-free corpus — it produced a corpus where some PII types are well-suppressed and others pass through entirely unchanged. Our error analysis additionally found that filters miss text spans for entirely mundane reasons — short or ambiguous tokens, label mismatches between taxonomies, and context-dependent identifiers that require world knowledge the filter doesn't have.

### 2. Non-PII Personal Information: The Filter's Taxonomy Is the Wrong Boundary

Even a filter with zero false negatives against its own taxonomy would still leave a training corpus full of information that is personal without being PII in the narrow, named-entity sense the filter is built to detect. Mireshghallah and Li (2025) argue this point directly: privacy risk in LLM systems is not reducible to verbatim memorization of named identifiers. A sentence describing someone's rare medical condition, their unusual commute pattern, a workplace conflict, or a distinctive personal habit contains no span that any PII-detection taxonomy — including this one — is designed to flag, yet it can be more identifying, and more sensitive, than a phone number.

Our own limits-of-anonymization argument makes the same point from the empirical side: our project logged hundreds of unredacted birth dates, gender markers, postcodes, and job titles, none of which are "PII" in the strict sense the filter's eight categories define, but all of which function as quasi-identifiers that narrow down a population until very few people remain consistent with the combination. Sweeney's (2000) foundational result — that ZIP code, birth date, and gender alone re-identify the large majority of the US population — is the formal version of exactly this gap. 

### 3. Memorization: The Training Process Creates Risk Independent of Filtering

Filtering happens to the input text before training. Memorization happens during training, and it is now well documented that even a perfectly filtered corpus does not prevent a model from memorizing and later reproducing whatever content remains in it — including the quasi-identifiers and non-PII personal content described above. Carlini et al.'s work on training-data extraction established that larger models memorize more, that memorization scales with how many times an example is duplicated in the training set, and that this happens even for models that are not visibly overfit on standard validation metrics. 

This matters for the sufficiency claim because filtering changes *what* is available to be memorized, not *whether* memorization occurs. If a filtered corpus still contains a rare combination of birth date, postcode, and job title describing one specific person — exactly the kind of content our analysis shows survives filtering — a sufficiently large model trained on that corpus can memorize that combination as readily as it would have memorized an unredacted name. 

### 4. Model Extraction and Inference-Time Risk

Beyond memorization of literal content, deployed models are vulnerable to a family of attacks that recover information about the training data without ever requiring the model to output a verbatim span. Training-data extraction attacks recover fragments of training examples through repeated, carefully constructed queries; membership inference attacks determine whether a specific record was present in training data at all, which is itself a privacy violation in sensitive domains (e.g., confirming someone's record was part of a clinical or legal training corpus reveals something about them even without recovering the record's contents); and attribute-inference attacks, as catalogued by Mireshghallah and Li (2025) and demonstrated by Staab et al., use a model's general reasoning ability to infer personal attributes about an individual from unstructured text the model has seen, with no extraction of an exact memorized string required at all.

### 5. Logs and Derived Data: The Privacy Perimeter Extends Past the Training Set

A sufficiency claim about "running data through a privacy filter" typically refers to the training corpus itself. But the training corpus is not the only place personal data lives in a real LLM pipeline. Our accountability mapping noted that downstream organizations and affected persons typically only see the final generated output, not the backend logs — but that asymmetry runs in both directions: it also means a great deal of intermediate data exists that was never subject to the same filtering scrutiny applied to the "official" training set, simply because it lives in a different system.

If an organization filters its training corpus but logs raw user inputs, retains pre-filtering snapshots for debugging, or stores evaluation that include the filter's own false negatives as recorded examples, the privacy perimeter the organization believes it has secured is narrower than the actual perimeter.

### 6. Deletion and Unlearning: The Claim Doesn't Survive Contact With "Right to Erasure"

The clearest demonstration that pre-training filtering cannot be sufficient privacy protection is that it has nothing to say about deletion after the fact. GDPR Article 17's right to erasure requires that, on request, a data controller take reasonable steps to remove an individual's personal data. For a structured database, this is a deletion operation. For a trained LLM, it is close to an open problem: once personal data has been used to update a model's weights, its influence is distributed across billions of parameters in a way that cannot be cleanly isolated.

A person's right to have their data removed can ideally be exercised at any time after training, indefinitely, and pre-training filtering has no mechanism to honor that request once the model exists.

## Conclusion

Each of the six considerations above fails the sufficiency claim for a structurally different reason, and that diversity is itself the point. 

A defender of pre-training filtering could, in principle, address any one of these by adding a complementary control: better taxonomies and red-teaming for (1), differential privacy or data minimization policy for (2)–(3), governance over logging and retention for (5), and unlearning research or contractual retraining commitments for (6). 

But each fix is a *different* technical and organizational intervention, layered on top of filtering rather than achieved by it, which is itself the strongest evidence against the original claim: "sufficient" is a claim about one mechanism doing the whole job, and the actual privacy guarantee — to the extent one is achievable at all — only emerges, if it does, from several independently maintained layers working together. Pre-training filtering is one input into that system. It is not the system.

---

### Sources

- Sweeney, L. (2000). Simple Demographics Often Identify People Uniquely. *Carnegie Mellon University, Data Privacy Working Paper 3*. — k-anonymity and re-identification via quasi-identifiers, cited here as in our project's original scope statement.
- Carlini, N., et al. (2021). Extracting Training Data from Large Language Models. *USENIX Security Symposium*. — foundational training-data extraction attack methodology and scaling-with-model-size finding.
- Mireshghallah, N., & Li, T. (2025). Position: Privacy Is Not Just Memorization! [arXiv:2510.01645](https://arxiv.org/pdf/2510.01645) — argument that LLM privacy risk extends beyond verbatim extraction to inference-time and attribute-inference risks; used here for the non-PII / model-extraction sections.
- Staab, R., et al. (2023). Beyond Memorization: Violating Privacy Via Inference with Large Language Models. — attribute inference from unstructured text without verbatim extraction, referenced via Mireshghallah & Li (2025) above.
- MDPI *Future Internet* (2025). GDPR and Large Language Models: Technical and Legal Obstacles. [mdpi.com/1999-5903/17/4/151](https://www.mdpi.com/1999-5903/17/4/151) — technical and legal analysis of why Article 17 (Right to Erasure) is difficult to satisfy for trained LLMs, and the state of machine unlearning as a partial remedy.
- TechPolicy.Press (2025). The Right to Be Forgotten Is Dead: Data Lives Forever in AI. [techpolicy.press](https://www.techpolicy.press/the-right-to-be-forgotten-is-dead-data-lives-forever-in-ai/) — accessible overview of the infeasibility of full erasure from trained model weights absent retraining.
- OpenAI. (2026, April 22). *Model Card for OpenAI Privacy Filter*, Section 4.1 and Section 6.1. [PDF](https://cdn.openai.com/pdf/c66281ed-b638-456a-8ce1-97e9f5264a90/OpenAI-Privacy-Filter-Model-Card.pdf)
