# Security Policy and Guidelines

## Reporting Security Issues

If you discover a security vulnerability or sensitive information committed in this repository, please report it immediately to the event organizers rather than opening a public issue.

## Strict Prohibition of Committed Secrets

Participants must **never** commit:
- API keys (OpenAI, Gemini, Anthropic, OpenRouter, WatsonX, etc.)
- Database passwords, user credentials, or connection strings containing credentials
- JWT secret keys, SSH private keys, or authentication tokens
- Proprietary, confidential, or customer data
- Non-public internal IBM network endpoints or credentials

## Best Practices for Hackathon Submissions

1. **Use `.env.example`**: Always provide a template `.env.example` in your submission directory showing required configuration variable names with placeholder dummy values (e.g., `DB2_PASSWORD=your_password_here`).
2. **Local `.env`**: Store real credentials in `.env`, which is strictly ignored by the repository's `.gitignore`.
3. **Pre-commit Self-Audit**: Before committing and opening a pull request, run `git diff --staged` or `git status` to verify that no secret files or hidden tokens are included.
4. **Remediation**: If you accidentally commit a secret, rotate/revoke that credential immediately from the provider dashboard and submit a sanitized commit.
