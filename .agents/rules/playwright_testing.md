# Playwright Automated Testing Policy

## Scope & Trigger
Apply this rule on every code modification, UI update, backend endpoint change, or bug fix in `Employee-Finder`.

## Testing Rules
1. **Always Verify with Playwright**: Do not rely solely on unit tests. Run the automated Playwright browser test suite to ensure no regressions in the DOM, visual layout, or full-stack API integration.
2. **Commands**:
   - Primary E2E: `python playwright_e2e_test.py` (Run from `candidate_app` directory)
   - Mobile Emulation: `python playwright_android_mobile_test.py` (Run from `candidate_app` directory)
   - Full Simulation: `python playwright_human_simulation_test.py` (Run from `candidate_app` directory)
3. **Requirement**: All steps must pass with 100% success before finishing the turn.
