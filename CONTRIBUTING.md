# Contribution Guidelines & Submission Rules

Thank you for contributing to the **IBM Db2 TechX Summit 2026** project showcase!

All hackathon submissions are received and reviewed as GitHub Pull Requests (PRs). Please adhere strictly to the guidelines below to ensure a smooth submission and review process.

---

## Required Workflow & Conventions

### 1. Unique Project Slug
Choose a concise, descriptive `<project-slug>` using lowercase letters, numbers, and hyphens only (`^[a-z0-9]+(-[a-z0-9]+)*$`).
* Examples: `db2-graph-rag`, `financial-fraud-db2`, `health-analytics-watsonx`
* Avoid: `project`, `test`, `submission1`, `final`, or spaces/special characters.

### 2. Branch Naming
All submission work must be committed on a dedicated branch created from `upstream/main`:
```text
submission/<project-slug>
```

### 3. Submission Directory
Your project must reside entirely inside a single folder:
```text
submissions/<project-slug>/
```
Copy `submissions/_template/` to start with a clean, pre-structured layout.

### 4. Pull Request Title
Format your PR title as follows:
```text
[Submission] <project-slug>: <Short Project Title>
```
* Example: `[Submission] db2-graph-rag: Db2 Graph RAG Knowledge Assistant`

### 5. Conventional Commits
Use standard commit messages with your slug as the scope:
```text
feat(<project-slug>): add initial db2 integration and models
docs(<project-slug>): complete architecture and setup instructions
```

---

## Pull Request Rules & Scope Isolation

1. **One Project per PR:** Each pull request must introduce exactly one submission directory under `submissions/<project-slug>/`.
2. **Do Not Touch Other Files:** Do not modify root files, scripts, GitHub templates/workflows, documentation, or other participants' submission folders. PRs modifying files outside their assigned submission slug will fail automated CI checks.
3. **No Committed Credentials or Secrets:** Staged files must be clean of API keys, tokens, or database passwords. Ensure `.env.example` has placeholder keys only.
4. **Complete Documentation:** Submissions must contain a completed `README.md`, `architecture.md`, `submission.json`, and `.env.example`.
5. **Mandatory Google Form Entry:** Opening a PR is Step 1. You must submit your open PR URL into the official Google Form: **[GOOGLE_FORM_LINK_TO_BE_ADDED]**.

---

## Review & Triage Expectations

- **Automated CI Validation:** When you open or update your PR, GitHub Actions automatically verifies directory naming, required file existence, `submission.json` schema, and secrets prevention.
- **Organizer Feedback:** Organizers and reviewers may post comments on your PR requesting clarifications, test reproducibility details, or fixes.
- **Making Revisions:** If changes are requested, commit the updates to your branch and push to your fork. The existing PR will update automatically. Do not close and open a new PR.

---

## Need Help?

If you have questions about the submission process, open an issue using the [Submission Help Template](https://github.com/KunalGolaIBM/IBM_Db2_TechX_Project_Submission/issues/new?template=submission_help.yml) or consult [docs/faq.md](docs/faq.md).
