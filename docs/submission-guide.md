# End-to-End Submission Guide

This guide walks you through the step-by-step process of preparing, formatting, and submitting your project for the **IBM Db2 TechX Summit 2026** hackathon.

---

## Submission Lifecycle Overview

```text
1. Fork Repository  ──>  2. Create Branch  ──>  3. Copy submissions/_template/
                                                        │
                                                        ▼
6. Fill Google Form <──  5. Open Pull Request <── 4. Build, Test & Document
```

---

## Step 1: Fork and Clone the Repository

1. Navigate to the canonical repository: `https://github.com/KunalGolaIBM/IBM_Db2_TechX_Project_Submission`.
2. Click **Fork** (top-right corner) to create a copy under your personal or organizational GitHub account.
3. Clone your fork locally:
   ```bash
   git clone https://github.com/<your-username>/IBM_Db2_TechX_Project_Submission.git
   cd IBM_Db2_TechX_Project_Submission
   ```
4. Set up the upstream remote to sync changes if needed:
   ```bash
   git remote add upstream https://github.com/KunalGolaIBM/IBM_Db2_TechX_Project_Submission.git
   ```

---

## Step 2: Create a Feature Branch

Create and switch to a new branch specifically for your submission. Use the format `submission/<project-slug>`:

```bash
# Fetch latest main from upstream
git fetch upstream main

# Create and checkout your branch
git checkout -b submission/my-project-slug upstream/main
```

> **Slug Rules:** Use lowercase alphanumeric characters and hyphens only (`[a-z0-9-]`). Example: `submission/db2-sql-assistant`.

---

## Step 3: Copy the Submission Template

Copy the starter template folder located at `submissions/_template/` to your own project folder inside `submissions/`:

```bash
# Copy the template folder to your slug
cp -r submissions/_template submissions/my-project-slug
```

Your project directory will look like this:
```text
submissions/my-project-slug/
├── README.md               # Project overview, setup, running instructions
├── architecture.md        # Architecture, component flow, Db2 design
├── submission.json        # Structured project & team metadata
├── .env.example           # Configuration variable keys with mock dummy values
├── src/                   # Your source code
├── tests/                 # Unit/integration tests (optional but recommended)
└── docs/
    └── screenshots/       # UI/CLI screenshots or architectural diagrams
```

---

## Step 4: Develop, Test, and Document

1. **Implement your application** inside `submissions/<project-slug>/src/`.
2. **Complete `submission.json`**: Ensure all metadata fields (project name, team members, Db2 tools, tech stack) are populated and valid JSON.
3. **Fill in `README.md`**: Detail the problem statement, solution, Db2 integration, prerequisites, and reproducible execution steps.
4. **Fill in `architecture.md`**: Detail the system components, data flow, Db2 queries/schemas, and AI/LLM flow (if applicable).
5. **Verify Security**: Ensure **NO real secrets, API keys, or credentials** are committed. Populate `.env.example` with blank or placeholder values.
6. **Local Validation**: Run the submission validation script:
   ```bash
   python scripts/validate_submission.py submissions/my-project-slug
   ```

---

## Step 5: Commit and Push Changes

Stage and commit only your project files:

```bash
# Stage only your project folder
git add submissions/my-project-slug

# Commit using conventional commits
git commit -m "feat(my-project-slug): add hackathon project submission"

# Push branch to your personal fork
git push -u origin submission/my-project-slug
```

---

## Step 6: Open a Pull Request

1. Go to your fork on GitHub and click **Contribute -> Open pull request** (or **New pull request**).
2. Set base repository: `KunalGolaIBM/IBM_Db2_TechX_Project_Submission`, base branch: `main`.
3. Set head repository: `<your-username>/IBM_Db2_TechX_Project_Submission`, compare branch: `submission/<project-slug>`.
4. Ensure your PR title follows:
   ```text
   [Submission] <project-slug>: <Short Project Title>
   ```
5. Complete the PR template checklist and questions thoroughly.
6. Click **Create Pull Request**.

---

## Step 7: Complete the Official Google Form

> **CRITICAL REQUIREMENT:** A GitHub pull request alone does NOT complete your registration or submission.

1. Copy the URL of your newly created pull request (`https://github.com/KunalGolaIBM/IBM_Db2_TechX_Project_Submission/pull/<number>`).
2. Open the official Google Form: **[GOOGLE_FORM_LINK_TO_BE_ADDED]**.
3. Fill out the team details and paste your PR URL into the submission form.
4. Submit the form before the deadline.
