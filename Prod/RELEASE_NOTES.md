# Production Release Notes: v1.2.0-prod

**Release Date:** August 31, 2026  
**Environment:** Production / Live  
**Repository:** [github.com/rajmohan10j/Employee-Finder](https://github.com/rajmohan10j/Employee-Finder)

---

## 🌟 What's New in Production v1.2.0

### 1. Enterprise Grandfather-Father-Son (GFS) Backup & Version Control
* **Pre-Connection / Startup Snapshots**: Automatically takes an atomic snapshot of `candidates_tracker.xlsx` before connecting or reading data into memory upon server startup.
* **Tiered Retention Schedules**:
  - **Daily Backups (Son)**: Executed twice daily at **01:00 PM** and **06:00 PM** with rolling **7-day auto-pruning**.
  - **Weekly Backups (Father)**: Executed every **Saturday at 06:00 PM** with **8-week archive retention**.
  - **Monthly Backups (Grandfather)**: Executed on the **1st of every month at 09:00 AM** with **12-month long-term retention**.
  - **On-Demand Manual Snapshots**: One-click instant checkpointing directly from the dashboard header.
* **Smart SHA-256 Deduplication**: Prevents redundant identical spreadsheet files when data has not changed.
* **One-Click Instant Restore**: UI-driven rollback that automatically takes a safety backup before restoring.

### 2. Android Mobile LAN Sync & Pure Touch UI
* **Dynamic Local QR Code**: Auto-detects active LAN IP (e.g. `http://192.168.29.55:5000`) for seamless 1-second mobile phone onboarding.
* **1-Tap Quick Action Buttons**: Instant `tel:` direct dialing and WhatsApp candidate messaging from any mobile browser.
* **Touch-Optimized Box Items & Font Scaling**: Built-in `A-` and `A+` scale controls for optimal readability on Android screens.

### 3. Comprehensive 15-Field Box Item Form & Escalation Matrix
* **Synchronized Header Mapping**: Full support for Candidate Name, Phone, Email, Location, Experience, Portal Source, Open to Work, HR Called, Date, HR Remarks, Follow-up Date, Follow-up Remarks, Escalation Level/Person, Action Category, and Escalation Remarks.
* **Multi-Level Escalation Routing (L1 to L4)**: Assigns action items to HR Sourcing Lead (L1), Raj (L2), Chaitali (L3), or Matthew (L4).
* **Next-Level Profile Sharing**: Formats clean, structured summary text for 1-click sharing to WhatsApp, Email, or Clipboard.

### 4. Dual Review & Staging Workflow
* Allows staging candidate modifications for approval before committing directly to the master Excel workbook.
* Visual Diffs highlighting previous vs updated values.

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
