# Hackathon Judging & Evaluation Criteria

Projects submitted to the **IBM Db2 TechX Summit 2026** hackathon are evaluated by a panel of IBM engineers, subject matter experts, and academic mentors across five core dimensions:

---

## Evaluation Rubric (Total: 100 Points)

| Dimension | Weight | Key Evaluation Points |
|---|:---:|---|
| **1. IBM Db2 Integration & Depth** | **30%** | • Substantive, non-trivial use of IBM Db2 (storage, querying, indexing, stored procedures, vector/JSON capabilities, or specialized engines).<br>• Correct implementation of drivers, connectors, or framework integrations (e.g. `ibm_db`, SQLAlchemy, LangChain Db2 vector stores / SQL chains).<br>• Clean schema design, efficient querying, and data reliability. |
| **2. Innovation & Impact** | **25%** | • Originality and novelty of the solution addressing real-world problems.<br>• Practical applicability for enterprise, developer tooling, analytics, or AI automation.<br>• Value delivered to end-users or target personas. |
| **3. Technical Architecture & AI Integration** | **20%** | • Sound software engineering principles, modularity, and clean code.<br>• Effective AI/LLM workflow design (RAG, agentic routing, embeddings, prompt engineering, or fallback handling) if applicable.<br>• Clarity and completeness of `architecture.md`. |
| **4. Reproducibility & Code Quality** | **15%** | • Ease of setup and testing following `README.md` instructions.<br>• Working `.env.example` with clear prerequisite instructions.<br>• Presence of automated tests, input validation, and clean error handling. |
| **5. Documentation & Presentation** | **10%** | • Complete, polished documentation following repository templates without unfilled placeholders.<br>• Compelling demonstration (screenshots, live demo URL, or video walk-through).<br>• Adherence to submission rules, naming conventions, and security hygiene (zero secrets committed). |

---

## Disqualification & Penalty Triggers

Submissions may receive score deductions or immediate disqualification for:
- **Zero Db2 Integration**: Cosmetic mention of Db2 in text without actual execution or database interactions in code.
- **Committed Secrets**: Unsanitized production database passwords or API keys pushed to GitHub.
- **Plagiarism**: Direct copying of uncredited third-party repositories without significant unique innovation.
- **Tampering**: Altering repository root configurations, scripts, or another participant's submission folder.
