# 👥 Employee-Finder: Candidate Sourcing & Tracking System

Modern, mobile-responsive Candidate Tracking & Recruitment Management System with Excel two-way synchronization, staging review workflows, and mobile QR code connectivity.

---

## 🚀 Quick Start & Live Testing Links

| Target | URL | Description |
| :--- | :--- | :--- |
| 💻 **Desktop Web App** | [http://127.0.0.1:5000](http://127.0.0.1:5000) | Full recruiter dashboard, candidate cards, search & review queue |
| 📱 **Android / Mobile** | [http://192.168.29.55:5000](http://192.168.29.55:5000) | Mobile-optimized PWA with 1-tap call/WhatsApp action buttons |

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

# 4. Run Full Recruiter Workflow Simulation Suite
python playwright_human_simulation_test.py

# 5. Start Server for Manual Testing
python app.py
```
