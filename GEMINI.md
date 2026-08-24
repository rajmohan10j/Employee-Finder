# Project Rules: Employee-Finder

## Mandatory Automated Testing & Reporting Policy
For every feature addition, UI change, Excel sync update, bug fix, or code modification in this project:

1. **Mandatory Playwright Execution**:
   - You MUST run and verify the changes using the project's Playwright test suites (`python playwright_e2e_test.py` or `python playwright_android_mobile_test.py` in `candidate_app/`) before concluding any task.
   - Ensure the run finishes with exit code 0 and all assertions pass.

2. **Mandatory Output & Link Sharing Guideline**:
   - In EVERY test response, unless the user has explicitly confirmed rollout for production/live, you MUST provide:
     - 🔗 **Direct Testing URLs**:
       - Desktop: `http://127.0.0.1:5000`
       - Mobile / Android LAN: `http://192.168.29.55:5000`
     - 📋 **Step-by-Step Test Sequence Checklist** (how to run the suites, launch the server, and what manual actions to verify on Desktop and Mobile).
     - 📁 **Reference Link**: Point to [TEST_EXECUTION_GUIDE.md](file:///c:/Users/Raj/Projects/Employee-Finder/TEST_EXECUTION_GUIDE.md).

3. **Mandatory Data Privacy & GitHub Zero-PII Policy**:
   - **Zero Real PII in Git**: Real candidate resumes (`.pdf`, `.docx`), actual personal phone numbers, real candidate emails, addresses, `.env`, tokens, or personal endpoint URLs must NEVER be committed to Git or pushed to GitHub.
   - **Automatic Masking & Anonymization**: All tracked sample data files (`.xlsx`, `.json`, `.csv`) must strictly use realistic mock/dummy data (`@example.com`, `+91 98765 0000X`).
   - **Local Backup Protection**: Real user data must be backed up exclusively to `local_private_backup/` or `private_data/` (both enforced in `.gitignore`).
   - **Mandatory Pre-Commit Sanitization**: Follow the `git-privacy-sanitizer` skill before every `git commit` or `git push`.
