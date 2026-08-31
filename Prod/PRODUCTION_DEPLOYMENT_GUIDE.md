# Production Deployment & Operations Guide

## 📌 Overview
This document outlines the standard operating procedures (SOP) for running and maintaining the **Employee-Finder Candidate Tracker** in a production / multi-device LAN environment.

---

## 🛠️ Prerequisites
* **Operating System**: Windows 10 / Windows 11 / Windows Server
* **Python Runtime**: Python 3.10+ installed and added to system PATH
* **Required Libraries**:
  ```powershell
  pip install -r requirements.txt
  ```
  *(Packages: `flask`, `openpyxl`, `playwright`)*

---

## 🚀 Running the Production Application

### Method 1: Interactive Desktop Console (Recommended for daily active recruiting)
Double-click `Launch_Production_App.bat` or run:
```powershell
c:\Users\Raj\Projects\Employee-Finder\Prod\Launch_Production_App.bat
```
* Binds to `0.0.0.0:5000` (listening on localhost and all LAN network adapters).
* Auto-starts the in-app 60-second GFS backup daemon.
* Opens your default desktop browser to `http://127.0.0.1:5000`.

### Method 2: Silent Background Mode (No Open Command Prompt)
Double-click `Launch_Production_App_Silent.vbs` or run:
```powershell
wscript c:\Users\Raj\Projects\Employee-Finder\Prod\Launch_Production_App_Silent.vbs
```

---

## 📱 Connecting Android Mobile Phones
1. Ensure your phone and PC are connected to the same Wi-Fi network.
2. On your desktop, navigate to the **"Connect Mobile / QR"** tab.
3. Scan the displayed QR code with your phone camera or visit:
   ```text
   http://192.168.29.55:5000
   ```
4. **Install as App (PWA)**: On Android Chrome, tap the menu (⋮) and select **"Add to Home screen"** or **"Install App"**.

---

## 🛡️ Automated GFS Backup Configuration

### In-App Background Daemon (Active when server is running)
* Automatically executes scheduled checks every 60 seconds.
* Automatically creates Daily (1:00 PM / 6:00 PM), Weekly (Saturday 6:00 PM), and Monthly (1st 9:00 AM) snapshots.

### OS-Level Scheduled Tasks (Active even when server is closed)
To register the scheduled backups directly in Windows Task Scheduler:
1. Open Command Prompt / PowerShell as **Administrator**.
2. Run:
   ```powershell
   c:\Users\Raj\Projects\Employee-Finder\Prod\setup_production_backup_scheduler.bat
   ```

---

## 🔄 Instant Disaster Recovery / Rollback
1. Open the Candidate Tracker dashboard.
2. Click **"Backups & Versions"** in the navigation bar.
3. Locate the snapshot in the table and click **"Restore"**.
4. A safety pre-restore backup is automatically created before reverting to the selected snapshot.
