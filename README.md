# 👥 Employee-Finder: Candidate Sourcing & Tracking System

Modern, mobile-responsive Candidate Tracking & Recruitment Management System with Excel two-way synchronization, staging review workflows, task escalation (L1–L4), and mobile QR code connectivity.

---

## 🚀 Quick Start & Live Testing Links

| Target | URL | Description |
| :--- | :--- | :--- |
| 💻 **Desktop Web App** | [http://127.0.0.1:5000](http://127.0.0.1:5000) | Full recruiter dashboard, candidate cards, search, task assignment & review queue |
| 📱 **Android / Mobile LAN** | [http://192.168.29.55:5000](http://192.168.29.55:5000) | Mobile-optimized PWA with 1-tap Call, WhatsApp, and Quick Close action buttons |

---

## ⚡ Core Features & Capabilities

1. **⚡ Task Escalation & Assignment Matrix (L1 to L4)**:
   - **`L1 - HR Person`**: Recruiter / Sourcing Lead.
   - **`L2 - Raj`**: Lead Reviewer & Tech Sourcing.
   - **`L3 - Chaitali`**: Hiring Manager / Department Lead.
   - **`L4 - Matthew`**: Executive Approver / Final Authority.
   - Standard Action Categories: `Need to Talk`, `Review / Suggest`, `Interview Decision`, `Other / Custom Action`.
   - Custom Escalation Comments / Action Details field.
   - 1-Tap `⚡ Assign Task` button and color-coded badges directly on candidate cards.

2. **🚫 1-Click Quick Close & Not Interested Management**:
   - 1-Click **🚫 Quick Close** button on every candidate card to instantly mark candidates as `Closed - Not Interested` and record today's date in Excel.
   - Dedicated **`Closed (Not Int.)`** live metric counter on the dashboard.
   - Dedicated filter to view or hide closed candidates.

3. **📞 Mandatory Call Date Validation**:
   - When `HR Called` is set to `Yes`, the `Call Date` field dynamically becomes mandatory, shakes/highlights on empty submissions, and auto-prefills with today's date.

4. **📊 Master Excel 2-Way Synchronization**:
   - Master spreadsheet at `candidates_tracker.xlsx` synchronized across all 18 columns with full multi-threading lock protection (`RLock`) and automatic rolling backups in `backups/`.

---

## 🛡️ Data Privacy & GitHub Zero-PII Protection

This project enforces strict privacy masking rules for public & team repository safety:
- **No Real PII in Git**: Real candidate resumes (`.pdf`, `.docx`), personal phone numbers, and actual emails are ignored by `.gitignore` and kept in `local_private_backup/`.
- **Sanitized Datasets**: Tracked spreadsheets (`candidates_tracker.xlsx`, `Followup_Tracker.xlsx`) strictly use synthetic mock candidate data (`@example.com`, `+91 98765 0000X`).
- **Standardized Sanitizer Skill**: Follows the `git-privacy-sanitizer` Antigravity skill before every commit and push.
- **Auto-Restoration Guard**: The master working dataset is always preserved in `local_private_backup/` and automatically restored to `candidates_tracker.xlsx` after commits.

---

## 🧪 Testing Guidelines & Playwright Verification

Detailed step-by-step instructions and test sequences are documented in:
📄 **[TEST_EXECUTION_GUIDE.md](file:///c:/Users/Raj/Projects/Employee-Finder/TEST_EXECUTION_GUIDE.md)**

### Quick Commands for Automated Testing:
```powershell
# 1. Navigate to candidate_app
cd candidate_app

# 2. Run Desktop Playwright E2E Test Suite
python playwright_e2e_test.py

# 3. Run Android Mobile Touch & Viewport Suite
python playwright_android_mobile_test.py

# 4. Start Server for Manual Recruiter Testing
python app.py
```
