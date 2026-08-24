---
name: playwright-testing
description: >-
  Executes automated Playwright end-to-end (E2E), mobile viewport emulation, and workflow tests for the Employee-Finder application.
  Use this skill whenever testing, validating, verifying changes, checking UI responsiveness, or performing regression testing on the candidate app.
---

# Playwright Automated Testing Skill for Employee-Finder

This skill guides running, validating, and reporting Playwright automated tests for the `candidate_app` web & mobile platform.

## Test Suites

The test scripts are located in `candidate_app/`:

| Suite | Script | Purpose |
| :--- | :--- | :--- |
| **Desktop E2E** | `playwright_e2e_test.py` | Validates dashboard metrics, live search & filtering, 15-field box-item editor, candidate share generation, review & approval queue with visual diffs, reviewer registry, and QR code generation. |
| **Android Mobile Viewport** | `playwright_android_mobile_test.py` | Emulates Google Pixel 7 (393x851), validates horizontal overflow prevention, font/box zoom adjusters, mobile bottom navigation, and 1-tap call/WhatsApp buttons. |
| **Human Simulation** | `playwright_human_simulation_test.py` | Simulates realistic recruiter multi-step workflows, candidate editing, stage reviews, and Excel synchronization. |

## Execution Workflow

1. Navigate to the `candidate_app` directory:
   ```powershell
   cd c:\Users\Raj\Projects\Employee-Finder\candidate_app
   ```

2. Run the desired test suite:
   ```powershell
   python playwright_e2e_test.py
   ```
   or for mobile verification:
   ```powershell
   python playwright_android_mobile_test.py
   ```

3. **Mandatory Reporting Rule**:
   - Every time testing is performed, always output:
     - 🌐 **Testing URLs**:
       - Desktop: `http://127.0.0.1:5000`
       - Android / Mobile: `http://192.168.29.55:5000`
     - 📋 **Step-by-Step Test Sequence Checklist**
     - 📄 Link to [TEST_EXECUTION_GUIDE.md](file:///c:/Users/Raj/Projects/Employee-Finder/TEST_EXECUTION_GUIDE.md)
