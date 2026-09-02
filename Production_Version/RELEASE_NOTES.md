# Production Release Notes: v2.0.0-prod

**Release Date:** September 3, 2026  
**Environment:** Production / Live  
**Repository:** [github.com/rajmohan10j/Employee-Finder](https://github.com/rajmohan10j/Employee-Finder)

---

## 🌟 What's New in Production Version 2.0.0

### 1. Conversion Intelligence & Target Audience Analytics Suite
* **Audience Segmentation Engine**: Categorizes candidates into **P1 Preferred Target** (Age > 50, Government, Retired), **P2 Controlled Expansion** (Age 45+, PSU, Senior Banking/Defence), and **Unclassified / Review Queue**.
* **Master Conversion Funnel**: 7 progression stages (*Total Sourced* ➔ *Outreach Attempted* ➔ *Reached / Connected* ➔ *Positive Response* ➔ *Interview / Meeting Agreed* ➔ *Advisory Interested* ➔ *Advisory Formally Accepted*) with stated denominators and symmetrical 3-zone stage alignment.
* **4 Modular Analytical Reports**:
  1. *Report 1: Target Audience Coverage & Sourcing Profile* (Segmentation, Experience, Age-Bands, Sector, Portal Sources, Top Domains).
  2. *Report 2: Outreach Response Performance* (Response Breakdown by Segment, Experience, and Location).
  3. *Report 3: Interview Readiness & Availability* (Interview Acceptance Rates, Meeting Mode Preference: In-Person vs Virtual).
  4. *Report 4: Advisory Role Progression & Conversion* (Interest by Segment, Stage-by-Stage Advisory Acceptance).
* **Direct Graph Data Labels**: Every chart directly renders exact numbers and percentages (`Count (%)`) directly on/above bars and slices (e.g. `56 (43%)`, `30 (23%)`, `47 (36%)`).
* **Interactive Excel-Style Slicers & Scenario Modeling**: Clickable tiles for *Sector*, *Experience Band*, and *Target Pool*, combined with numeric inputs for *Minimum Age* and *Minimum Experience* that dynamically recalculate all 18 graphs in real-time (<10ms).
* **Display Section Selectors**: Multi-option pill switcher and custom multi-select menu for focused executive viewing.

### 2. Enhanced Candidate Master Database (27 Canonical Columns)
* Added dedicated conversion tracking columns: `Call Response`, `Interview / Meeting Agreed`, `Advisory Role Interest`, `Age`, `Employment Sector`, and `Retirement Status`.
* Confirmed and verified **Email Address is 100% Optional** to avoid browser validation blocking.
* Automatic data provenance tracking: Distinguishes between explicit candidate confirmation and inferred heuristics.

### 3. Enterprise Grandfather-Father-Son (GFS) Backup & Version Control
* **Pre-Connection / Startup Snapshots**: Automatically takes an atomic snapshot of `candidates_tracker.xlsx` before connecting or reading data into memory upon server startup.
* **Tiered Retention Schedules**:
  - **Daily Backups (Son)**: Executed twice daily at **01:00 PM** and **06:00 PM** with rolling **7-day auto-pruning**.
  - **Weekly Backups (Father)**: Executed every **Saturday at 06:00 PM** with **8-week archive retention**.
  - **Monthly Backups (Grandfather)**: Executed on the **1st of every month at 09:00 AM** with **12-month long-term retention**.
  - **On-Demand Manual Snapshots**: One-click instant checkpointing directly from the dashboard header.
* **Smart SHA-256 Deduplication**: Prevents redundant identical spreadsheet files when data has not changed.
* **One-Click Instant Restore**: UI-driven rollback that automatically takes a safety backup before restoring.

### 4. Android Mobile LAN Sync & Pure Touch UI
* **Dynamic Local QR Code**: Auto-detects active LAN IP (e.g. `http://192.168.29.55:5000`) for seamless 1-second mobile phone onboarding.
* **1-Tap Quick Action Buttons**: Instant `tel:` direct dialing and WhatsApp candidate messaging from any mobile browser.
* **Touch-Optimized Box Items & Font Scaling**: Built-in `A-` and `A+` scale controls for optimal readability on Android screens.

---

## 🚀 Quick Launch

### Desktop Launch (Console)
```powershell
.\Prod\Launch_Production_App.bat
```

### Background / Silent Launch (No open terminal)
```powershell
wscript .\Prod\Launch_Production_App_Silent.vbs
```

### Access URLs
* **Desktop**: `http://127.0.0.1:5000`
* **Mobile / Android LAN**: `http://192.168.29.55:5000`
* **PythonAnywhere Cloud**: `https://<your-username>.pythonanywhere.com`
