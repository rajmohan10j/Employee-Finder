# ☁️ 100% Free Cloud & Remote Deployment Guide: Candidate Tracker

This guide provides instructions to host and share the Candidate Tracker app with **3+ remote users on any phone or 4G/5G mobile connection** without requiring the same Wi-Fi.

---

## ⚡ Option A: 1-Click Instant Public HTTPS Tunnel (No Cloud Account Needed)

If you want a free, instant public HTTPS link right from your PC with **zero configuration**:

1. Double-click [`Launch_Public_Tunnel.bat`](file:///c:/Users/Raj/Projects/Employee-Finder/Launch_Public_Tunnel.bat) (or [`Prod/Launch_Public_Tunnel.bat`](file:///c:/Users/Raj/Projects/Employee-Finder/Prod/Launch_Public_Tunnel.bat)).
2. The script will automatically start the server and initialize a Cloudflare Quick Tunnel.
3. Look for the generated URL in the terminal:
   ```text
   https://random-phrase-xyz.trycloudflare.com
   ```
4. Copy and send this URL to your teammates via WhatsApp/Email. They can open it on **any mobile device or remote computer**!

---

## 🌐 Option B: Deploy to PythonAnywhere (100% Free Forever & Native Excel Persistence)

**PythonAnywhere** is the best cloud option for this project because it provides 512MB of permanent Linux disk storage where your `candidates_tracker.xlsx` spreadsheet and GFS backups stay intact permanently without sleeping.

### Step-by-Step Setup (3 Minutes):

1. **Sign Up**:
   - Go to [PythonAnywhere.com](https://www.pythonanywhere.com) and create a **Free Beginner Account**.

2. **Upload Your Files**:
   - Open the **Consoles** tab and start a **Bash Console**.
   - Clone your project repo or upload your project zip:
     ```bash
     git clone <YOUR_GITHUB_REPO_URL> Employee-Finder
     cd Employee-Finder
     pip install --user -r requirements.txt
     ```

3. **Configure Web App**:
   - Click the **Web** tab in PythonAnywhere.
   - Click **Add a new web app** -> Choose **Manual Configuration** -> Select **Python 3.10 or 3.11**.
   - Under **Code** section:
     - **Source code**: `/home/<yourusername>/Employee-Finder`
     - **Working directory**: `/home/<yourusername>/Employee-Finder`
   - Click on the **WSGI configuration file** link to edit it:
     - Clear the default file and paste the contents from [`pythonanywhere_wsgi.py`](file:///c:/Users/Raj/Projects/Employee-Finder/pythonanywhere_wsgi.py):
       ```python
       import sys, os
       username = '<yourusername>'
       project_home = f'/home/{username}/Employee-Finder'
       if project_home not in sys.path:
           sys.path.insert(0, project_home)
       app_dir = os.path.join(project_home, 'candidate_app')
       if app_dir not in sys.path:
           sys.path.insert(1, app_dir)
       os.environ['EXCEL_PATH'] = os.path.join(project_home, 'candidates_tracker.xlsx')
       from app import app as application
       ```
   - Click **Save**, return to the Web tab, and click **Reload <yourusername>.pythonanywhere.com**.

4. **Your Live 24/7 Cloud App**:
   - Your public URL is: `https://<yourusername>.pythonanywhere.com`
   - Accessible by anyone 24/7 from any phone or PC!

---

## 🚀 Option C: Deploy to Render.com (1-Click Auto-Deploy from GitHub)

**Render.com** offers 750 free hours/month with automatic builds directly connected to your GitHub repository.

### Step-by-Step Setup:

1. **Push Code to GitHub**:
   - Make sure your project (with `Procfile`, `wsgi.py`, and `requirements.txt`) is pushed to your GitHub account.
2. **Create Web Service on Render**:
   - Log in at [Render.com](https://render.com) (Free Account).
   - Click **New +** -> **Web Service** -> Connect your GitHub repo.
3. **Settings**:
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn wsgi:app`
   - **Instance Type**: `Free`
4. **Deploy**:
   - Click **Create Web Service**.
   - In 1–2 minutes, Render will provide a permanent URL:
     ```text
     https://employee-finder-tracker.onrender.com
     ```

---

## 🔒 Security & Privacy Notice (GitHub Zero-PII Policy)
Before pushing code to any public Git repository, always ensure you run the privacy sanitizer:
- Real candidate resumes (`.pdf`, `.docx`) and personal phone numbers/emails must remain in `local_private_backup/` or `.gitignore`.
- Use sample masked mock data for the initial cloud deploy, then upload your working master Excel tracker using the in-app **"Import XLSX"** button!
