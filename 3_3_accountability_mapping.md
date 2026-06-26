# 3.3 Accountability Mapping

To analyze the governance failures of the OpenAI Privacy Filter (OPF), we map its ecosystem by identifying the **"Actors"** (entities responsible for taking action and justifying it) and the **"Forums"** (entities that evaluate actions and impose consequences). 

### Part 1: Mapping Actors and Forums

Based on the pipeline we audited, we identify the following **Actors**:
1. **Model Provider (OpenAI)**: The developer of the filter. They define the model's taxonomy and document its capabilities.
2. **Tool Deployer / Data Controller**: Organizations integrating the filter to sanitize records. They hold the legal responsibility for data protection.
3. **Organization Using Filtered Data**: Downstream LLM developers or analysts who ingest the "de-identified" outputs.
4. **Auditor**: Independent evaluators (our team) who measure the actual technical gaps.
5. **Affected Person**: The individuals whose personal data is processed.

The corresponding **Forums** intended to hold these actors accountable are:
1. **Regulators**: Data Protection Authorities ensuring compliance.
2. **Courts**: Legal venues for affected persons to seek redress.
3. **Internal Review Bodies**: Corporate compliance teams approving the filter's deployment.
4. **Users and Affected Communities**: The public, acting as a social forum by withdrawing trust.

### Part 2: Accountability Gaps Identified

Mapping these entities against our empirical findings from Part 2 reveals severe accountability gaps. The safety net is fundamentally broken due to transparency failures and false reassurance:

**1. The Liability Void (Model Provider vs. Tool Deployer)**
Our metrics in Section 2.3 demonstrate that the filter successfully targets only 7 out of 29 PII categories, leaving 22 categories entirely unmasked (0 True Positives). This results in a catastrophic overall False Negative Rate (FNR) of 72.45%. 

However, as documented in Section 2.2, the Model Provider failed to transparently disclose these 22 taxonomic blind spots. Consequently, the Tool Deployer blindly integrates the filter, falsely assuming it provides comprehensive protection. When downstream LLMs leak unredacted data (like dates of birth or passports), the Provider uses its model card to disclaim safety guarantees, while the Deployer blames the "black-box AI." This creates a liability gap where no actor takes responsibility for the 72.45% of PII that structurally leaks.

**2. Performative Oversight (Internal Review Bodies vs. Tool Deployer)**
Internal Review Bodies are supposed to prevent unsafe deployments. However, our downstream black-box check (Section 2.5) exposes why this internal oversight fails. We identified instances of "truncated masking" (e.g., masking a driver's license as `[SOCIALNUMBER]892` in Example 2). 

To an internal compliance reviewer, the visual presence of the `[SOCIALNUMBER]` tag looks like successful redaction, creating a false sense of security. Yet, the downstream LLM simply reproduces the exposed fragment (*"ending in 892"*). Internal forums thus fall into the trap of "compliance theater," unknowingly approving a leaky pipeline because the output superficially appears safe.

**3. The Recourse Asymmetry (Affected Persons vs. Regulators/Courts)**
For accountability to function, external forums (Courts and Regulators) must be able to investigate breaches on behalf of the Affected Person. However, the modular nature of AI pipelines severs this link. As shown in Section 2.4 and 2.5, quasi-identifiers systematically slip through the filter and are memorized by downstream models. 

When an Affected Person's privacy is compromised by the Organization Using Filtered Data, they only see the final generated output. They have no access to the backend logs to prove that the Tool Deployer specifically failed to filter their data. Without this technical trace, external forums lack the evidence to hold the deployers accountable, leaving affected individuals with no practical recourse.
