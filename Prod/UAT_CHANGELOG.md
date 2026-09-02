# UAT Testing & Feature Staging Log

This environment is dedicated to staging, testing, and introducing new features without touching or risking the stable **Production Version (V1)**.

---

## 🎯 Active Stage: Preparation for Production Version 2 (V2)

### Pending / Incoming Features to Test in UAT:
- [ ] Feature 1: *To be defined by user*
- [ ] Feature 2: *To be defined by user*
- [ ] Feature 3: *To be defined by user*

---

## 🚀 Promotion Procedure to Production Version 2:
1. Complete feature development under `UAT_Testing/candidate_app/`.
2. Run full Playwright test suite: `python playwright_e2e_test.py` and `python playwright_android_mobile_test.py`.
3. Verify on Desktop (`http://127.0.0.1:5000` or `5001`) and Mobile (`http://192.168.29.55:5000` or `5001`).
4. Once signed off, copy validated code and assets from `UAT_Testing/` into `Production_Version/` as **Production V2**.
