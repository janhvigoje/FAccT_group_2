# 3.3 Accountability Mapping

To analyze the governance issues of the OpenAI Privacy Filter (OPF), we first map its socio-technical ecosystem using standard accountability frameworks (Bovens, 2007; Novelli et al., 2024). Accountability requires a clear relationship between **"Actors"** (who must justify their actions) and **"Forums"** (who evaluate and impose consequences). 

### Part 1: Mapping Actors and Forums

**Actors (The Account-Givers):**
1. **Model Provider (OpenAI):** Develops the filter, defines its 8-category taxonomy, and provides the model card.
2. **Tool Deployer / Data Controller:** Organizations (e.g., healthcare or legal firms) integrating the filter into their data pipelines. Under GDPR, they bear the primary legal duty for data protection.
3. **Organization Using Filtered Data:** Downstream LLM developers or third-party analytics teams who ingest the supposedly "de-identified" data.
4. **Auditor:** Independent evaluators (our role) responsible for stress-testing the system and identifying taxonomic gaps.
5. **Affected Person:** The individuals whose raw data is processed and potentially exposed.

**Forums (The Account-Holders):**
1. **Regulators:** Data Protection Authorities (DPAs) that enforce GDPR compliance.
2. **Courts:** Legal forums where affected persons seek civil remedies for privacy breaches.
3. **Internal Review Bodies:** Corporate compliance and ethics boards responsible for approving the deployment of the filter.
4. **Users and Affected Communities:** The collective public acting as a social and market forum, exercising accountability by withdrawing trust or demanding transparency.

### Part 2: Accountability Gaps Identified

Mapping these entities against our empirical findings from Sections 2.2, 2.3 and 2.5 reveals that the accountability chain is fundamentally broken. We identified three major gaps:

**1. The "Many Hands" Liability Void (Provider vs. Deployer)**
As Nissenbaum (1996) and Cobbe et al. (2023) point out, distributed software supply chains obscure who is responsible when harms occur. Our metrics in Section 2.3 show that the filter successfully detects only 7 out of 29 PII categories, leaving an overall Full False Negative Rate (FNR) of over 51%. 

OpenAI protects itself legally by framing the tool cautiously in its model card, effectively shifting the compliance burden to the Deployers. However, because the tool's severe limitations are not transparent (Section 2.2), Deployers blindly integrate it. When downstream LLMs leak unredacted identifiers (like passport numbers or usernames), the Provider blames the Deployer for misusing the tool, while the Deployer blames the "black-box AI." This creates a liability gap where no single actor takes responsibility for the missing 22 PII categories.

**2. Performative Oversight (Internal Review Bodies vs. Truncated Masking)**
Effective accountability requires meaningful "oversight" from forums (Novelli et al., 2024). Internal Review Bodies are supposed to provide this. However, our downstream black-box check (Section 2.5) exposed a critical flaw: **partial/truncated masking** (e.g., replacing a driver's license with `[SOCIALNUMBER]892`). 

To an internal compliance reviewer, the visual presence of the `[SOCIALNUMBER]` tag creates a false sense of security. But as we demonstrated, downstream LLMs simply repeat the exposed fragment. This turns internal accountability into "compliance theater," where internal forums unknowingly approve ongoing privacy leakage because the output superficially looks redacted.

**3. Lack of Interrogation and Recourse (Affected Persons vs. Regulators/Courts)**
A key condition for accountability is **"interrogation"**—the ability for a forum to scrutinize an actor's decisions (Novelli et al., 2024). When an Affected Person's quasi-identifiers slip through the filter and are reproduced by a downstream LLM, they only see the final output. 

The modularity of the AI supply chain makes it impossible for regular users to access backend logs and prove that the OPF specifically failed to filter their data. Without this technical evidence, external forums like DPAs and Courts cannot effectively hold the Deployers accountable, leaving the victims without any practical recourse.

---
### References
* **Bovens, M. (2007).** Analysing and Assessing Accountability: A Conceptual Framework. *European Law Journal*, 13(4), 447–468. https://doi.org/10.1111/j.1468-0386.2007.00378.x
* **Cobbe, J., et al. (2023).** Understanding Accountability in Algorithmic Supply Chains. *2023 ACM FAccT*, 1186–1197. https://doi.org/10.1145/3593013.3594073
* **Nissenbaum, H. (1996).** Accountability in a computerized society. *Science and Engineering Ethics*, 2(1), 25–42. https://doi.org/10.1007/BF02639315
* **Novelli, C., et al. (2024).** Accountability in Artificial Intelligence: What It Is and How It Works. *AI & SOCIETY*, 39(4), 1871–1882. https://doi.org/10.1007/s00146-023-01635-y
