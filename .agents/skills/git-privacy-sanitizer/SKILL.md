---
name: git-privacy-sanitizer
description: >-
  Scans, masks, and sanitizes personal data (PII), confidential spreadsheets, resumes,
  secrets, and private endpoints before committing and pushing code to Git and GitHub.
---

# Git Privacy & Secret Sanitizer Skill

## Purpose
This skill ensures zero personal identifiable information (PII), personal resumes, candidate contacts, API keys, or private machine endpoints are committed or pushed to public or private Git/GitHub repositories.

---

## When to Execute
- **Mandatory Pre-Commit**: Whenever staging (`git add`), committing (`git commit`), or pushing (`git push`) to Git and GitHub.
- **Project Setup**: When initializing a new repository or onboarding an existing codebase.
- **Review Requests**: When reviewing code or preparing releases for public/shared visibility.

---

## Standard Operating Procedure (SOP)

### Step 1: Secure Local Real Data
Before altering any dataset, safely copy real data to a git-ignored directory:
```powershell
New-Item -ItemType Directory -Force -Path "local_private_backup"
Copy-Item "candidates_tracker.xlsx" "local_private_backup\candidates_tracker_real.xlsx"
Copy-Item "Followup_Tracket.xlsx" "local_private_backup\Followup_Tracket_real.xlsx"
```

### Step 2: Comprehensive `.gitignore` Enforcement
Verify that `.gitignore` contains the following critical entries:
```gitignore
# Environments, credentials & private backups
.env
*.env
.secure_config.bin
local_private_backup/
private_data/

# Raw candidate resumes and proprietary documents
resumes/
Resume-Search-Script/candidate_data/
**/candidate_data/
*.pdf
*.docx

# Build and packaging output
build/
dist/
Candidate_Sourcing_App/

# Browser profiles and cache
browser_profile/
.pytest_cache/
candidate_app/test_screenshots/
```

### Step 3: Anonymize Tracked Data Files
Ensure any files that remain tracked in Git contain only sanitized mock data:
- **Names**: Standard sample names (e.g. *Aarav Sharma*, *Priya Patel*, *Tech Candidate*)
- **Emails**: `@example.com` or `@domain.invalid`
- **Phone numbers**: `+91 98765 00001`, `+91 98765 00002`
- **Endpoints**: Configured via `os.getenv("BASE_URL", "https://api.example.com")` without personal subdomains.

### Step 4: Pre-Commit PII & Secret Scan
Run a verification scan on staged files:
```powershell
git status -s
git diff --cached
```

### Step 5: Safe Git Commit & Push
Commit only sanitized files:
```powershell
git add .
git commit -m "feat/fix: descriptive message with sanitized data"
git push origin main
```
