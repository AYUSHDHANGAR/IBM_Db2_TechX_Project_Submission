# Frequently Asked Questions (FAQ)

### General & Eligibility

**Q: Can we work in teams or only individually?**  
A: Both individual participants and teams are eligible, subject to the official hackathon rules. List all contributing team members in your `submission.json`, project `README.md`, and the Pull Request description.

**Q: Can we use any programming language?**  
A: Yes! You can use Python, Node.js/TypeScript, Java, Go, Rust, C#, Haskell, or any language of your choice, as long as it interfaces with IBM Db2 and includes clear build/run instructions.

**Q: Is using an AI / LLM framework required?**  
A: No, AI integration is optional. Projects can focus on core Db2 data engineering, analytics, developer tooling, security, performance optimization, or AI/LLM applications (such as LangChain, CrewAI, LlamaIndex, or watsonx).

---

### IBM Db2 Environment & Setup

**Q: Where can I get a free IBM Db2 instance for local development?**  
A: You can run **IBM Db2 Community Edition** for free via Docker container. See the [Db2 Setup Guide](db2-setup-guide.md) for step-by-step instructions.

**Q: Can we use IBM Cloud Db2 or watsonx.data?**  
A: Yes. You may connect to IBM Cloud Db2, Db2 on-premises, or watsonx.data Db2 instances. Provide connection instructions in `.env.example` using dummy placeholder variables.

---

### Pull Request & Submission Workflow

**Q: Why was my PR automated check failing?**  
A: Check the GitHub Actions logs. Common reasons include:
- Files modified outside `submissions/<project-slug>/`.
- Missing required files (`README.md`, `architecture.md`, `submission.json`).
- `submission.json` is missing required keys or has invalid JSON syntax.
- Real `.env` file committed instead of `.env.example`.

**Q: Can I update my submission after opening the Pull Request?**  
A: Yes! As long as the submission deadline has not passed, you can push additional commits to your submission branch, and the existing PR will update automatically.

**Q: Do I really need to fill out the Google Form?**  
A: **Yes.** Opening a Pull Request is Step 1. You must submit your PR link via the official Google Form (**[GOOGLE_FORM_LINK_TO_BE_ADDED]**) to be officially logged for judging.
