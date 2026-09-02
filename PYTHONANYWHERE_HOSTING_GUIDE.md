# 🌐 Complete Step-by-Step Guide: Hosting Candidate Tracker on PythonAnywhere

This guide provides the complete, production-grade instructions for hosting the **Employee-Finder Candidate Tracker** application and its master Excel spreadsheet (`candidates_tracker.xlsx`) on [PythonAnywhere.com](https://www.pythonanywhere.com/).

---

## 🌟 Why PythonAnywhere?

| Feature | PythonAnywhere Beginner (Free) | Other Free Cloud Providers (Render, Heroku) |
| :--- | :--- | :--- |
| **Cost** | **100% Free Forever** | Limited free trial or credit card required |
| **Excel Persistence** | **Permanent Local Linux Disk (512 MB)** (`.xlsx` persists across reboots) | Ephemeral disk (Files reset/deleted on restart) |
| **Sleep / Spin-Down** | **Always Available 24/7** (No 15-minute spin-down sleep) | Sleeps after 15 mins of inactivity (50s cold start) |
| **Access** | Public HTTPS URL (`https://<username>.pythonanywhere.com`) | Public URL with cold-boot delays |
| **Mobile & Desktop** | Fully accessible from any phone, tablet, or PC worldwide | Fully accessible |

---

## 📋 Prerequisites

1. An account at [PythonAnywhere.com](https://www.pythonanywhere.com/) (Sign up for a free "Beginner" plan).
2. Your PythonAnywhere username (e.g., `rajmohan`).
3. Your web app URL will automatically be:  
   `https://<your-username>.pythonanywhere.com`

---

## 🚀 Step-by-Step Deployment Instructions

### Step 1: Create a Free Account on PythonAnywhere
1. Open [https://www.pythonanywhere.com/](https://www.pythonanywhere.com/) in your browser.
2. Click **Pricing & signup** -> Select **Create a Beginner account**.
3. Choose a username (e.g. `rajmohan`). **Note**: Your username becomes part of your public link (`https://rajmohan.pythonanywhere.com`).
4. Enter your email and password, confirm registration via email, and log into your Dashboard.

---

### Step 2: Open a Bash Console & Clone the Code
1. On the PythonAnywhere Dashboard, navigate to the **Consoles** tab.
2. Click on **Bash** under **Start a new console**.
3. In the terminal window, clone the GitHub repository:
   ```bash
   git clone https://github.com/rajmohan10j/Employee-Finder.git
   cd Employee-Finder
   ```
4. If the repository is private, you can either:
   - Use a GitHub Personal Access Token (PAT): `git clone https://<token>@github.com/rajmohan10j/Employee-Finder.git`
   - Or zip your local `Prod/` folder and upload it via the **Files** tab (see Step 4 below).

---

### Step 3: Install Required Python Dependencies
In the same Bash console, install the application dependencies using the `--user` flag:
```bash
cd ~/Employee-Finder
pip install --user -r requirements.txt
```
*Required packages installed: `Flask`, `openpyxl`, `pandas`, `cryptography`.*

---

### Step 4: Upload Your Master Excel File (`candidates_tracker.xlsx`)
To ensure your existing candidate data and call notes are available online:
1. Click on the **Files** tab in the PythonAnywhere top navigation bar.
2. Navigate to `/home/<your-username>/Employee-Finder/`.
3. In the **Upload a file** box on the right:
   - Click **Choose File**.
   - Select your local `candidates_tracker.xlsx` from your computer.
   - Click **Upload**.
4. Confirm that `candidates_tracker.xlsx` is located directly inside `/home/<your-username>/Employee-Finder/`.

> [!TIP]
> **Live Web In-App Upload**: You can also upload or replace the master spreadsheet at any time after deployment by opening the web app and clicking the **"Import XLSX File"** button in the sidebar!

---

### Step 5: Configure the Web App in PythonAnywhere
1. Click on the **Web** tab in the top navigation bar.
2. Click the **Add a new web app** button.
   - Click **Next**.
   - Select **Manual configuration (not Django, web2py...)**.
   - Select **Python 3.10** or **Python 3.11** (matching your environment).
   - Click **Next** to finish the wizard.

3. Configure Directory Paths under the **Code** section:
   - **Source code**: `/home/<your-username>/Employee-Finder`
   - **Working directory**: `/home/<your-username>/Employee-Finder`

---

### Step 6: Configure the WSGI File
1. Under the **Code** section of the **Web** tab, click on the link next to **WSGI configuration file** (e.g., `/var/www/<your-username>_pythonanywhere_com_wsgi.py`).
2. Delete all existing default code in the editor.
3. Paste the following configuration (replace `<your-username>` with your actual username, e.g. `rajmohan`):

```python
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# PythonAnywhere WSGI Configuration for Employee-Finder Candidate Tracker
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import sys
import os

# 1. Define username and project paths
username = '<your-username>'  # <-- REPLACE WITH YOUR PYTHONANYWHERE USERNAME
project_home = f'/home/{username}/Employee-Finder'
app_dir = os.path.join(project_home, 'candidate_app')

# 2. Add project and app directories to Python search path
if project_home not in sys.path:
    sys.path.insert(0, project_home)
if app_dir not in sys.path:
    sys.path.insert(1, app_dir)

# 3. Set environment variables for production Excel persistence
os.environ['EXCEL_PATH'] = os.path.join(project_home, 'candidates_tracker.xlsx')
os.environ['FLASK_ENV'] = 'production'

# 4. Import the Flask application
from app import app as application
```

4. Click the green **Save** button in the top right.

---

### Step 7: Configure Static Files Routing (CSS, JS, Fonts, Icons)
To ensure the dark-theme styles, charts, icons, and scripts load at high speed:
1. In the **Web** tab, scroll down to the **Static files** section.
2. Enter the following two mappings:

| URL | Directory Path |
| :--- | :--- |
| `/static/` | `/home/<your-username>/Employee-Finder/candidate_app/static/` |
| `/static/css/` | `/home/<your-username>/Employee-Finder/candidate_app/static/css/` |

---

### Step 8: Reload the Web App
1. Scroll to the top of the **Web** tab.
2. Click the large green button: **Reload <your-username>.pythonanywhere.com**.
3. Wait 5 seconds for the reload to complete.

---

## 🌐 Verifying Your Live Online Web App

1. Open your browser and navigate to:
   ```text
   https://<your-username>.pythonanywhere.com
   ```
2. Verify:
   - **Candidates Tracker**: Confirms all candidates from `candidates_tracker.xlsx` are loaded.
   - **Interactive Analytics**: Check the **Analytics** tab to view the Master Conversion Funnel, interactive Excel slicers, and direct data labels on all graphs.
   - **Editing & Saving**: Click "Edit Box Items" on any candidate, add a note, and click "Save & Update Master Excel". Verify that changes are saved directly to `candidates_tracker.xlsx`.
   - **Automated Backups**: Navigate to "Backups & Versions" to verify GFS point-in-time recovery snapshots are active.

---

## 🔄 How to Overwrite / Update the Online App (Future Releases)

Whenever you make updates to the application or Excel file and want to publish them online:

### Method 1: Git Pull (Fastest)
1. Open the **Consoles** tab -> click your existing **Bash** console.
2. Run:
   ```bash
   cd ~/Employee-Finder
   git pull origin main
   ```
3. Go to the **Web** tab and click **Reload <your-username>.pythonanywhere.com**.

### Method 2: Manual File Upload
1. Open the **Files** tab on PythonAnywhere.
2. Navigate to the folder you want to update (e.g. `candidate_app/static/js/app.js` or `candidates_tracker.xlsx`).
3. Upload the new file.
4. Go to the **Web** tab and click **Reload <your-username>.pythonanywhere.com**.

---

## 🔒 Security & Privacy Best Practices
- **Never commit real PII to public GitHub**: If using a public repository, ensure `candidates_tracker.xlsx` in GitHub contains sanitized mock data, and upload your real `candidates_tracker.xlsx` directly to PythonAnywhere via the private **Files** tab or the in-app **"Import XLSX File"** button.
- **PythonAnywhere Free Account Expiry**: Free accounts require clicking the "Run until 3 months from today" button in the Web tab once every 3 months. PythonAnywhere will send an email reminder before this happens.
