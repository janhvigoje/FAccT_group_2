# 3.3 Accountability Mapping

To analyze the governance issues of the OpenAI Privacy Filter (OPF), we mapped its socio-technical ecosystem using standard accountability frameworks (Bovens, 2007; Novelli et al., 2024). The ecosystem consists of **Actors** (Model Provider [OpenAI], Tool Deployer/Data Controller, Downstream LLM User, and the Affected Person) and **Forums** (Data Protection Authorities [DPAs], Courts, Internal Review Boards, and the User Base acting as a social forum).

However, mapping these entities reveals that accountability is easily lost across the AI supply chain. Grounded in our empirical findings from Sections 2.2, 2.3 and 2.5, we identified three major accountability gaps:

### 1. The "Many Hands" Problem in the Algorithmic Supply Chain
As Nissenbaum (1996) and Cobbe et al. (2023) point out, distributed software supply chains obscure who is responsible when harms occur. Our metrics in Section 2.3 show that the filter successfully detects only **7 out of 29 PII categories**, leaving **22 categories** with zero True Positives. This creates a massive Full False Negative Rate (FNR) of over 51%. 

OpenAI protects itself legally by framing the tool cautiously in its model card, effectively shifting the compliance burden to the Deployers. However, because the tool's severe limitations are not transparent (as noted in Section 2.2), Deployers blindly integrate it. When downstream LLMs leak unredacted identifiers (like driver's licenses or birth dates), the Provider blames the Deployer for misusing the tool, while the Deployer blames the "black-box AI." This creates a liability gap where no single actor takes responsibility for the missing 22 PII categories.

### 2. Performative Oversight and the Truncated Masking Flaw
According to Novelli et al. (2024), effective accountability requires "oversight" (monitoring and reviewing decisions). Corporate Internal Review Boards are supposed to provide this oversight. However, our downstream black-box check (Section 2.5) exposed a critical flaw: **partial/truncated masking** (e.g., replacing a driver's license with `[SOCIALNUMBER]892`). 

To an internal compliance reviewer, the presence of the `[SOCIALNUMBER]` tag looks like the tool is working, creating a false sense of security. But as we demonstrated, downstream LLMs simply repeat the exposed fragment (*"ending in 892"*). This turns internal accountability into "compliance theater," where oversight forums unknowingly approve ongoing privacy leakage because the output superficially looks redacted.

### 3. Lack of Interrogation and Recourse for Affected Persons
A key condition for accountability is **"interrogation"**—the ability for a forum to scrutinize an actor's decisions (Novelli et al., 2024). When an Affected Person's quasi-identifiers slip through the filter and are reproduced by a downstream LLM, they only see the final output. 

The modularity of the AI supply chain makes it impossible for regular users to access backend logs and prove that the OPF specifically failed to filter their data. Without this evidence, external forums like DPAs and Courts cannot effectively hold the Deployers accountable, leaving the victims without any practical recourse.

---
### References
* **Bovens, M. (2007).** Analysing and Assessing Accountability: A Conceptual Framework. *European Law Journal*, 13(4), 447–468. https://doi.org/10.1111/j.1468-0386.2007.00378.x
* **Cobbe, J., et al. (2023).** Understanding Accountability in Algorithmic Supply Chains. *2023 ACM Conference on Fairness, Accountability, and Transparency*, 1186–1197. https://doi.org/10.1145/3593013.3594073
* **Nissenbaum, H. (1996).** Accountability in a computerized society. *Science and Engineering Ethics*, 2(1), 25–42. https://doi.org/10.1007/BF02639315
* **Novelli, C., et al. (2024).** Accountability in Artificial Intelligence: What It Is and How It Works. *AI & SOCIETY*, 39(4), 1871–1882. https://doi.org/10.1007/s00146-023-01635-y
