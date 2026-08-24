# Mandatory Rule: Data Privacy & Git Hygiene

## 1. Zero-PII & Secret Protection Standard
- **Never Commit Real PII**: Real candidate resumes (`.pdf`, `.docx`), phone numbers, personal email addresses, home addresses, or proprietary reports must NEVER be staged or pushed to GitHub.
- **Never Commit Secrets**: Never commit `.env`, `.secure_config.bin`, API keys, private tokens, or personal account URL endpoints.

## 2. Mandatory Pre-Commit Data Masking Workflow
Before executing `git add`, `git commit`, or `git push`:
1. **Local Safe Backup**: Move real/production data files to `local_private_backup/` or `private_data/` (both must be in `.gitignore`).
2. **Sanitize Tracked Datasets**: Replace tracked sample datasets (e.g., `.xlsx`, `.json`, `.csv`) with synthetic mock data using standard placeholders (`@example.com`, `+91 98765 0000X`).
3. **Verify `.gitignore`**: Ensure `.gitignore` covers `.env`, `local_private_backup/`, `private_data/`, `resumes/`, `*.pdf`, `*.docx`, `build/`, `dist/`, and browser profiles.
4. **Pre-Push Scan**: Perform regex verification on staged files to ensure no real phone numbers, emails, or personal usernames are present.
