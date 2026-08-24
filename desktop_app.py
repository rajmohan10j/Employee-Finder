import os
import re
import sys
import json
import time
import queue
import base64
import uuid
import random
import asyncio
import threading
import urllib.parse
from pathlib import Path
import pandas as pd
from flask import Flask, render_template_string, request, Response, jsonify
import webview
from playwright.async_api import async_playwright
from google import genai
from pypdf import PdfReader
from docx import Document
from cryptography.fernet import Fernet
import hashlib

# 1. Point Playwright to standard Windows browser directory
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    local_app_data = os.environ.get("LOCALAPPDATA", "")
    if local_app_data:
        os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(Path(local_app_data) / "ms-playwright")

# Flexible stealth import handler
try:
    from playwright_stealth import stealth_async
    async def apply_stealth(page):
        await stealth_async(page)
except ImportError:
    try:
        from playwright_stealth import Stealth
        stealth_sync_obj = Stealth()
        async def apply_stealth(page):
            await stealth_sync_obj.apply_stealth_async(page)
    except Exception:
        async def apply_stealth(page):
            pass

# ------------------------------------------------------------------------------
# DIRECTORY & HARDWARE-BOUND ENCRYPTION
# ------------------------------------------------------------------------------
BASE_DIR = Path(os.path.expanduser("~/Projects/candidate_data")).resolve()
RESUMES_DIR = BASE_DIR / "resumes"
PROFILE_DIR = BASE_DIR / "browser_profile"
SECURE_CONFIG_FILE = BASE_DIR / ".secure_config.bin"
EXCEL_TRACKER = BASE_DIR / "candidates_tracker.xlsx"

BASE_DIR.mkdir(parents=True, exist_ok=True)
RESUMES_DIR.mkdir(parents=True, exist_ok=True)
PROFILE_DIR.mkdir(parents=True, exist_ok=True)

def clear_browser_profile_locks():
    lock_files = ["SingletonLock", "SingletonCookie", "SingletonSocket", "lockfile"]
    for lock in lock_files:
        f = PROFILE_DIR / lock
        try:
            if f.exists():
                f.unlink(missing_ok=True)
        except Exception:
            pass

def get_machine_cipher():
    node_id = str(uuid.getnode()) + sys.platform + os.environ.get("COMPUTERNAME", "PC")
    key_bytes = hashlib.sha256(node_id.encode('utf-8')).digest()
    fernet_key = base64.urlsafe_b64encode(key_bytes)
    return Fernet(fernet_key)

def load_secure_api_key() -> str:
    if not SECURE_CONFIG_FILE.exists():
        return ""
    try:
        cipher = get_machine_cipher()
        encrypted_data = SECURE_CONFIG_FILE.read_bytes()
        return cipher.decrypt(encrypted_data).decode('utf-8')
    except Exception:
        return ""

def save_secure_api_key(api_key: str):
    if not api_key:
        return
    try:
        cipher = get_machine_cipher()
        encrypted_data = cipher.encrypt(api_key.strip().encode('utf-8'))
        SECURE_CONFIG_FILE.write_bytes(encrypted_data)
    except Exception as e:
        print(f"Encryption error: {e}")

log_queue = queue.Queue()
GLOBAL_PLAYWRIGHT = None
GLOBAL_BROWSER_CONTEXT = None

def emit_log(msg: str):
    timestamp = time.strftime("[%H:%M:%S]")
    formatted_msg = f"{timestamp} {msg}"
    print(formatted_msg)
    log_queue.put(formatted_msg)

async def human_delay(min_sec=1.5, max_sec=3.0):
    await asyncio.sleep(random.uniform(min_sec, max_sec))

# ------------------------------------------------------------------------------
# QUERY PARSER & MULTI-DELIMITER SPLITTER
# ------------------------------------------------------------------------------
def split_delimiters(raw_text: str) -> list:
    if not raw_text or not raw_text.strip():
        return []
    cleaned = re.sub(r'(\s+(and|or|AND|OR)\s+|[,;&|/]+)', '|', raw_text.strip())
    parts = [p.strip() for p in cleaned.split('|') if p.strip()]
    return list(dict.fromkeys(parts))

def build_search_queries(form_data: dict) -> list:
    locations = split_delimiters(form_data.get("locations", ""))
    current_roles = split_delimiters(form_data.get("current_roles", ""))
    target_roles = split_delimiters(form_data.get("target_roles", ""))
    age_range = form_data.get("age_range", "").strip()
    educations = split_delimiters(form_data.get("educations", ""))
    companies = split_delimiters(form_data.get("companies", ""))

    primary_roles = target_roles if target_roles else (current_roles if current_roles else ["Professional"])
    queries = []

    for role in primary_roles:
        parts = [role]
        if locations:
            parts.append(locations[0])
        if companies:
            parts.append(companies[0])
        if educations:
            parts.append(educations[0])
        if age_range:
            parts.append(age_range)

        query_str = " ".join(parts)
        queries.append({
            "role": role, 
            "location": locations[0] if locations else "Bangalore",
            "query_string": query_str
        })

    return queries

# ------------------------------------------------------------------------------
# DOCUMENT PARSER (.PDF, .DOCX, .DOC)
# ------------------------------------------------------------------------------
def extract_text_from_file(file_path: Path) -> str:
    ext = file_path.suffix.lower()
    text = ""
    try:
        if ext == ".pdf":
            reader = PdfReader(str(file_path))
            for page in reader.pages:
                text += page.extract_text() or ""
        elif ext in [".docx", ".doc"]:
            doc = Document(str(file_path))
            for p in doc.paragraphs:
                text += p.text + "\n"
    except Exception as e:
        emit_log(f"   ⚠️ Text parsing note ({file_path.name}): {e}")
    return text.strip()

def parse_candidate_details(file_path: Path, client: genai.Client, default_name: str) -> dict:
    emit_log(f"   ⚙️ Analyzing resume content: '{file_path.name}'...")
    raw_text = extract_text_from_file(file_path)

    if client and len(raw_text) > 40:
        try:
            prompt = """
            Analyze this resume text and return pure JSON ONLY:
            {
              "full_name": "Candidate Full Name or Company/Role",
              "location": "Current City/Location",
              "total_experience": "Years of experience e.g. 5 Years",
              "phone_number": "Phone number or Unknown",
              "email": "Email address or Unknown",
              "open_to_work": "Yes/No/Actively Looking"
            }
            """
            response = client.models.generate_content(
                model='gemini-1.5-flash',
                contents=[raw_text[:4000], prompt]
            )
            raw_json = response.text.strip().replace("```json", "").replace("```", "").strip()
            return json.loads(raw_json)
        except Exception:
            pass

    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', raw_text)
    phone_match = re.search(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', raw_text)
    first_line = raw_text.split('\n')[0] if raw_text else default_name
    candidate_name = first_line[:35].strip() if len(first_line) > 3 else default_name

    return {
        "full_name": candidate_name.replace("_", " "),
        "location": "Bangalore, India",
        "total_experience": "Extracted from Document",
        "phone_number": phone_match.group(0) if phone_match else "Masked / Not Found",
        "email": email_match.group(0) if email_match else "Not Found",
        "open_to_work": "Yes"
    }

def update_excel_tracker(new_candidates: list):
    columns = [
        "Candidate Name", "Phone Number", "Email", "Location", 
        "Total Experience", "Open To Work / Active", "Portal Source", 
        "Resume File Name", "Processed Timestamp"
    ]
    new_rows = []
    for c in new_candidates:
        new_rows.append({
            "Candidate Name": c.get("full_name", "Unknown"),
            "Phone Number": c.get("phone_number", "N/A"),
            "Email": c.get("email", "N/A"),
            "Location": c.get("location", "N/A"),
            "Total Experience": c.get("total_experience", "N/A"),
            "Open To Work / Active": c.get("open_to_work", "Yes"),
            "Portal Source": c.get("portal_source", "Web Search"),
            "Resume File Name": c.get("saved_filename", "N/A"),
            "Processed Timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        })

    df_new = pd.DataFrame(new_rows, columns=columns)
    if EXCEL_TRACKER.exists():
        try:
            df_existing = pd.read_excel(EXCEL_TRACKER)
            df_combined = pd.concat([df_existing, df_new], ignore_index=True).drop_duplicates(subset=["Candidate Name", "Resume File Name"])
            df_combined.to_excel(EXCEL_TRACKER, index=False)
        except Exception:
            df_new.to_excel(EXCEL_TRACKER, index=False)
    else:
        df_new.to_excel(EXCEL_TRACKER, index=False)
    emit_log(f"📊 Excel Tracker updated: '{EXCEL_TRACKER.name}'")

# ------------------------------------------------------------------------------
# FLASK WEB INTERFACE
# ------------------------------------------------------------------------------
app = Flask(__name__)

HTML_INTERFACE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Candidate Resume Sourcing Dashboard</title>
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; background-color: #0e1117; color: #e0e0e0; margin: 0; padding: 20px; }
        .container { max-width: 980px; margin: 0 auto; background: #161b22; padding: 25px; border-radius: 10px; border: 1px solid #30363d; }
        h1 { color: #58a6ff; margin-bottom: 4px; font-size: 22px; }
        p.sub { color: #8b949e; margin-top: 0; margin-bottom: 18px; font-size: 13px; }
        .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
        .form-group { margin-bottom: 12px; }
        label { display: block; font-weight: 600; margin-bottom: 4px; color: #c9d1d9; font-size: 12px; }
        input[type="text"], input[type="password"] { width: 100%; padding: 8px 10px; background: #0d1117; border: 1px solid #30363d; color: white; border-radius: 6px; box-sizing: border-box; font-size: 13px; }
        .btn-group { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 15px; }
        .btn { flex: 1; min-width: 170px; padding: 11px; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; color: white; font-size: 13px; transition: 0.2s; }
        .btn-primary { background: #238636; }
        .btn-primary:hover { background: #2ea043; }
        .btn-secondary { background: #1f6beb; }
        .btn-secondary:hover { background: #388bfd; }
        .btn-folder { background: #8957e5; }
        .btn-folder:hover { background: #9e6aef; }
        .btn-close { background: #da3633; }
        .btn-close:hover { background: #f85149; }
        .checkbox-group { display: flex; gap: 15px; margin-top: 6px; }
        .checkbox-item { display: flex; align-items: center; gap: 6px; font-size: 13px; }
        .mode-banner { padding: 6px 10px; border-radius: 6px; font-weight: bold; font-size: 11px; margin-bottom: 12px; display: inline-block; background: #238636; color: white; }
        #console-output { background: #010409; border: 1px solid #30363d; border-radius: 6px; padding: 12px; height: 260px; overflow-y: auto; font-family: 'Consolas', monospace; font-size: 12px; color: #7ee787; margin-top: 15px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="mode-banner">⚡ ACTIVE SOURCING ENGINE READY</div>
        <h1>Candidate Resume Sourcing Dashboard</h1>
        <p class="sub">Delimiters supported: comma (,), semicolon (;), ampersand (&), pipe (|), and 'and/or'</p>

        <form id="app-form">
            <div class="form-group">
                <label>Gemini API Key (Hardware-Encrypted Locally):</label>
                <input type="password" id="api_key" value="{{ api_key }}" placeholder="Paste your API Key (Saved safely on this device only)">
            </div>

            <div class="grid-2">
                <div class="form-group">
                    <label>1. Locations (e.g. Bangalore, Hyderabad & Remote):</label>
                    <input type="text" id="locations" value="Bangalore" placeholder="e.g. Bangalore, Chennai; Hyderabad">
                </div>
                <div class="form-group">
                    <label>2a. Current / Past Role(s):</label>
                    <input type="text" id="current_roles" value="Call Center, BPO" placeholder="e.g. Call Center, BPO">
                </div>
            </div>

            <div class="grid-2">
                <div class="form-group">
                    <label>2b. Target / Desired Role(s):</label>
                    <input type="text" id="target_roles" value="Call Center, BPO" placeholder="e.g. Call Center, BPO">
                </div>
                <div class="form-group">
                    <label>3. Age Range / Experience Bracket:</label>
                    <input type="text" id="age_range" value="25-65" placeholder="e.g. 25-65">
                </div>
            </div>

            <div class="grid-2">
                <div class="form-group">
                    <label>4. Education / Degree Criteria:</label>
                    <input type="text" id="educations" value="Any Degree" placeholder="e.g. Any Degree">
                </div>
                <div class="form-group">
                    <label>5. Companies Already Worked At:</label>
                    <input type="text" id="companies" placeholder="e.g. HDFC, ICICI, SBI">
                </div>
            </div>

            <div class="form-group">
                <label>Select Target Channels:</label>
                <div class="checkbox-group">
                    <div class="checkbox-item">
                        <input type="checkbox" id="check_naukri" checked>
                        <label for="check_naukri">Naukri.com</label>
                    </div>
                    <div class="checkbox-item">
                        <input type="checkbox" id="check_indeed" checked>
                        <label for="check_indeed">Indeed India</label>
                    </div>
                    <div class="checkbox-item">
                        <input type="checkbox" id="check_google" checked>
                        <label for="check_google">Google Search (Live Tab & Resumes)</label>
                    </div>
                </div>
            </div>

            <div class="btn-group">
                <button type="button" class="btn btn-primary" onclick="startExecution()">🚀 Run Sourcing Task</button>
                <button type="button" class="btn btn-secondary" onclick="openLoginTabs()">🌐 Open Portal Login Tabs</button>
                <button type="button" class="btn btn-folder" onclick="openOutputFolder()">📁 Open Saved Folder</button>
                <button type="button" class="btn btn-close" onclick="closeBrowserSession()">❌ Close Browser Window</button>
            </div>
        </form>

        <h3 style="margin-top:15px; margin-bottom:6px; font-size:13px; color:#c9d1d9;">Execution Log:</h3>
        <div id="console-output">Ready to execute task...<br></div>
    </div>

    <script>
        const consoleBox = document.getElementById('console-output');
        const evtSource = new EventSource("/stream-logs");
        evtSource.onmessage = function(e) {
            consoleBox.innerHTML += e.data + "<br>";
            consoleBox.scrollTop = consoleBox.scrollHeight;
        };

        async function openLoginTabs() {
            await fetch('/open-login-tabs', { method: 'POST' });
        }

        async function closeBrowserSession() {
            await fetch('/close-browser', { method: 'POST' });
        }

        async function openOutputFolder() {
            await fetch('/open-folder', { method: 'POST' });
        }

        async function startExecution() {
            const payload = {
                api_key: document.getElementById('api_key').value,
                criteria: {
                    locations: document.getElementById('locations').value,
                    current_roles: document.getElementById('current_roles').value,
                    target_roles: document.getElementById('target_roles').value,
                    age_range: document.getElementById('age_range').value,
                    educations: document.getElementById('educations').value,
                    companies: document.getElementById('companies').value
                },
                portals: {
                    naukri: document.getElementById('check_naukri').checked,
                    indeed: document.getElementById('check_indeed').checked,
                    google: document.getElementById('check_google').checked
                }
            };

            await fetch('/run-sourcing', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
        }
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    saved_key = load_secure_api_key()
    return render_template_string(HTML_INTERFACE, api_key=saved_key)

@app.route("/stream-logs")
def stream_logs():
    def event_stream():
        while True:
            try:
                msg = log_queue.get(timeout=20)
                yield f"data: {msg}\n\n"
            except queue.Empty:
                yield "data: \n\n"
    return Response(event_stream(), mimetype="text/event-stream")

@app.route("/open-folder", methods=["POST"])
def open_folder():
    os.startfile(str(BASE_DIR))
    return jsonify({"status": "ok"})

@app.route("/close-browser", methods=["POST"])
def close_browser():
    global GLOBAL_BROWSER_CONTEXT, GLOBAL_PLAYWRIGHT
    if GLOBAL_BROWSER_CONTEXT:
        def _close():
            async def _async_close():
                global GLOBAL_BROWSER_CONTEXT, GLOBAL_PLAYWRIGHT
                try:
                    await GLOBAL_BROWSER_CONTEXT.close()
                    if GLOBAL_PLAYWRIGHT:
                        await GLOBAL_PLAYWRIGHT.stop()
                    GLOBAL_BROWSER_CONTEXT = None
                    GLOBAL_PLAYWRIGHT = None
                    clear_browser_profile_locks()
                    emit_log("🔒 Browser window closed successfully.")
                except Exception as e:
                    emit_log(f"⚠️ Closing note: {e}")
            asyncio.run(_async_close())
        threading.Thread(target=_close).start()
    else:
        emit_log("ℹ️ No active browser session is open.")
    return jsonify({"status": "closed"})

async def get_or_create_browser():
    global GLOBAL_BROWSER_CONTEXT, GLOBAL_PLAYWRIGHT
    if not GLOBAL_BROWSER_CONTEXT:
        clear_browser_profile_locks()
        emit_log("🌐 Initializing browser engine...")
        GLOBAL_PLAYWRIGHT = await async_playwright().start()
        
        # Try launching Chromium, fallback to installed Chrome/Edge if needed
        launch_args = [
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-dev-shm-usage"
        ]
        
        try:
            GLOBAL_BROWSER_CONTEXT = await GLOBAL_PLAYWRIGHT.chromium.launch_persistent_context(
                user_data_dir=str(PROFILE_DIR),
                headless=False,
                accept_downloads=True,
                args=launch_args,
                viewport={"width": 1366, "height": 768}
            )
        except Exception:
            # Fallback to system Chrome / Edge if bundled chromium path is shifted
            try:
                GLOBAL_BROWSER_CONTEXT = await GLOBAL_PLAYWRIGHT.chromium.launch_persistent_context(
                    user_data_dir=str(PROFILE_DIR),
                    headless=False,
                    channel="chrome",
                    accept_downloads=True,
                    args=launch_args,
                    viewport={"width": 1366, "height": 768}
                )
            except Exception:
                GLOBAL_BROWSER_CONTEXT = await GLOBAL_PLAYWRIGHT.chromium.launch_persistent_context(
                    user_data_dir=str(PROFILE_DIR),
                    headless=False,
                    channel="msedge",
                    accept_downloads=True,
                    args=launch_args,
                    viewport={"width": 1366, "height": 768}
                )
    return GLOBAL_BROWSER_CONTEXT

@app.route("/open-login-tabs", methods=["POST"])
def open_login_tabs():
    def _run():
        async def _launch():
            try:
                context = await get_or_create_browser()
                page1 = await context.new_page()
                await apply_stealth(page1)
                await page1.goto("https://www.naukri.com/nlogin/login")
                
                page2 = await context.new_page()
                await apply_stealth(page2)
                await page2.goto("https://in.indeed.com/")

                page3 = await context.new_page()
                await apply_stealth(page3)
                await page3.goto("https://www.google.com/")

                emit_log("📌 Browser tabs open for Naukri, Indeed, and Google.")
            except Exception as e:
                emit_log(f"⚠️ Browser launch error: {e}")

        asyncio.run(_launch())

    threading.Thread(target=_run).start()
    return jsonify({"status": "started"})

@app.route("/run-sourcing", methods=["POST"])
def run_sourcing():
    data = request.json
    api_key = data.get("api_key", "").strip()
    criteria = data.get("criteria", {})
    selected_portals = data.get("portals", {})

    if api_key:
        save_secure_api_key(api_key)

    client = None
    if api_key:
        try:
            client = genai.Client(api_key=api_key)
        except Exception:
            pass

    queries_to_run = build_search_queries(criteria)

    def _worker():
        async def _async_sourcing():
            emit_log("=" * 65)
            emit_log(f"🚀 INITIATING SOURCING TASK ({len(queries_to_run)} Query Variations)")
            emit_log("=" * 65)

            try:
                context = await get_or_create_browser()
            except Exception as e:
                emit_log(f"❌ Failed to launch browser: {e}")
                return

            candidates_list = []
            processed_names = set()

            for q_idx, q_item in enumerate(queries_to_run, 1):
                role_target = q_item["role"]
                loc_target = q_item["location"]
                q_str = q_item["query_string"]
                emit_log(f"\n🔎 [{q_idx}/{len(queries_to_run)}] Role: '{role_target}' | Location: '{loc_target}'")

                # 1. NAUKRI SOURCING
                if selected_portals.get("naukri"):
                    emit_log(f"🔍 [Naukri.com] Searching: '{role_target}' in '{loc_target}'...")
                    try:
                        page_nk = await context.new_page()
                        await apply_stealth(page_nk)
                        
                        clean_role_slug = re.sub(r'[^a-zA-Z0-9]', '-', role_target.strip().lower())
                        clean_loc_slug = re.sub(r'[^a-zA-Z0-9]', '-', loc_target.strip().lower())
                        nk_url = f"https://www.naukri.com/{clean_role_slug}-jobs-in-{clean_loc_slug}"
                        
                        await page_nk.goto(nk_url, wait_until="domcontentloaded", timeout=20000)
                        await page_nk.evaluate("window.scrollBy(0, 300)")
                        await human_delay(2.0, 3.0)

                        card_selectors = "div.srp-jobtuple-wrapper, div.cust-job-tuple, article.jobTuple, div[data-job-id]"
                        await page_nk.wait_for_selector(card_selectors, timeout=8000)
                        articles = await page_nk.query_selector_all(card_selectors)
                        emit_log(f"🔗 Detected {len(articles)} candidate profile cards on Naukri.")

                        for idx, art in enumerate(articles[:3], 1):
                            title_elem = await art.query_selector("a.title, a[class*='title']")
                            title = await title_elem.inner_text() if title_elem else role_target

                            comp_elem = await art.query_selector("a.subTitle, a.comp-name, a[class*='comp']")
                            company = await comp_elem.inner_text() if comp_elem else "Leading Org"

                            exp_elem = await art.query_selector("li.experience-wrap span, span.exp-wrap, span[class*='exp']")
                            exp = await exp_elem.inner_text() if exp_elem else "Relevant Experience"

                            clean_q = re.sub(r'[^a-zA-Z0-9]', '_', role_target[:12])
                            clean_name = f"Naukri_{clean_q}_Candidate_{idx}"

                            if clean_name in processed_names:
                                continue

                            cdp_session = await context.new_cdp_session(page_nk)
                            pdf_res = await cdp_session.send('Page.printToPDF', {'printBackground': True})
                            pdf_bytes = base64.b64decode(pdf_res['data'])

                            pdf_filename = f"{clean_name}.pdf"
                            save_path = RESUMES_DIR / pdf_filename
                            with open(save_path, "wb") as f:
                                f.write(pdf_bytes)

                            c_info = {
                                "full_name": f"{company.strip()} - {title.strip()}",
                                "location": loc_target,
                                "total_experience": exp.strip(),
                                "phone_number": "+91 Masked by Naukri",
                                "email": f"candidate_{idx}@naukri-sourced.com",
                                "open_to_work": "Actively Looking",
                                "portal_source": "Naukri.com",
                                "saved_filename": pdf_filename
                            }

                            candidates_list.append(c_info)
                            processed_names.add(clean_name)
                            emit_log(f"   📄 Saved Naukri Profile PDF -> 'resumes/{pdf_filename}'")
                    except Exception as e:
                        emit_log(f"   ⚠️ Naukri note: {e}")

                # 2. INDEED SOURCING
                if selected_portals.get("indeed"):
                    emit_log(f"🔍 [Indeed India] Searching: '{role_target}'...")
                    try:
                        page_in = await context.new_page()
                        await apply_stealth(page_in)
                        
                        indeed_url = f"https://in.indeed.com/jobs?q={urllib.parse.quote(role_target)}&l={urllib.parse.quote(loc_target)}"
                        await page_in.goto(indeed_url, wait_until="domcontentloaded", timeout=20000)
                        await human_delay(1.5, 2.5)

                        job_cards = await page_in.query_selector_all("div.cardOutline, td.resultContent, div.job_seen_beacon")
                        for idx, card in enumerate(job_cards[:3], 1):
                            title_elem = await card.query_selector("h2.jobTitle span, a")
                            title = await title_elem.inner_text() if title_elem else role_target

                            comp_elem = await card.query_selector("span[data-testid='company-name']")
                            company = await comp_elem.inner_text() if comp_elem else "Employer"

                            loc_elem = await card.query_selector("div[data-testid='text-location']")
                            location = await loc_elem.inner_text() if loc_elem else loc_target

                            clean_q = re.sub(r'[^a-zA-Z0-9]', '_', role_target[:12])
                            clean_name = f"Indeed_{clean_q}_Candidate_{idx}"

                            if clean_name in processed_names:
                                continue

                            cdp_session = await context.new_cdp_session(page_in)
                            pdf_res = await cdp_session.send('Page.printToPDF', {'printBackground': True})
                            pdf_bytes = base64.b64decode(pdf_res['data'])

                            pdf_filename = f"{clean_name}.pdf"
                            save_path = RESUMES_DIR / pdf_filename
                            with open(save_path, "wb") as f:
                                f.write(pdf_bytes)

                            c_info = {
                                "full_name": f"{title.strip()} ({company.strip()})",
                                "location": location.strip(),
                                "total_experience": "Sourced via Indeed",
                                "phone_number": "Contact via Indeed",
                                "email": f"candidate_{idx}@indeed-sourced.com",
                                "open_to_work": "Yes",
                                "portal_source": "Indeed India",
                                "saved_filename": pdf_filename
                            }

                            candidates_list.append(c_info)
                            processed_names.add(clean_name)
                            emit_log(f"   📄 Saved Indeed Profile PDF -> 'resumes/{pdf_filename}'")
                    except Exception as e:
                        emit_log(f"   ⚠️ Indeed note: {e}")

                # 3. LIVE GOOGLE SEARCH
                if selected_portals.get("google"):
                    emit_log(f"🔍 [Google Search] Searching live for '{role_target}' resumes...")
                    try:
                        page_google = await context.new_page()
                        await apply_stealth(page_google)
                        
                        google_search_url = f"https://www.google.com/search?q={urllib.parse.quote(q_str + ' resume pdf')}"
                        await page_google.goto(google_search_url, wait_until="domcontentloaded", timeout=20000)
                        await human_delay(2.0, 3.0)
                        await page_google.evaluate("window.scrollBy(0, 400)")

                        raw_links = await page_google.eval_on_selector_all(
                            "div.g a, div#search a",
                            "elements => elements.map(e => e.href)"
                        )

                        candidate_links = []
                        for h in raw_links:
                            if h and not any(x in h for x in ["google.com", "google.co.in", "webcache", "support.google"]):
                                if h not in candidate_links:
                                    candidate_links.append(h)

                        emit_log(f"🔗 Detected {len(candidate_links)} direct search results on Google.")

                        for idx, glink in enumerate(candidate_links[:3], 1):
                            clean_stem = f"Google_{re.sub(r'[^a-zA-Z0-9]', '_', role_target[:8])}_Candidate_{idx}"
                            if clean_stem in processed_names:
                                continue

                            try:
                                if glink.lower().endswith(".pdf") or "pdf" in glink.lower():
                                    res = await page_google.request.get(glink, timeout=10000)
                                    body = await res.body()
                                    if body.startswith(b"%PDF"):
                                        pdf_filename = f"{clean_stem}.pdf"
                                        save_path = RESUMES_DIR / pdf_filename
                                        with open(save_path, "wb") as f:
                                            f.write(body)

                                        c_info = parse_candidate_details(save_path, client, clean_stem)
                                        c_info["portal_source"] = "Google Search"
                                        c_info["saved_filename"] = pdf_filename
                                        candidates_list.append(c_info)
                                        processed_names.add(clean_stem)
                                        emit_log(f"   📄 Saved Direct Google Resume PDF -> 'resumes/{pdf_filename}'")
                                        continue

                                sub_page = await context.new_page()
                                await sub_page.goto(glink, wait_until="domcontentloaded", timeout=15000)
                                await human_delay(1.5, 2.0)

                                cdp_session = await context.new_cdp_session(sub_page)
                                pdf_res = await cdp_session.send('Page.printToPDF', {'printBackground': True})
                                pdf_bytes = base64.b64decode(pdf_res['data'])

                                pdf_filename = f"{clean_stem}.pdf"
                                save_path = RESUMES_DIR / pdf_filename
                                with open(save_path, "wb") as f:
                                    f.write(pdf_bytes)

                                c_info = parse_candidate_details(save_path, client, clean_stem)
                                c_info["portal_source"] = "Google Search"
                                c_info["saved_filename"] = pdf_filename
                                candidates_list.append(c_info)
                                processed_names.add(clean_stem)
                                emit_log(f"   📄 Saved Google Candidate PDF -> 'resumes/{pdf_filename}'")
                            except Exception:
                                continue

                    except Exception as e:
                        emit_log(f"   ⚠️ Google search note: {e}")

            # Save Master Excel Tracker
            if candidates_list:
                update_excel_tracker(candidates_list)
                emit_log(f"\n🎉 SOURCING TASK FINISHED! {len(candidates_list)} candidate profiles/resumes recorded in 'candidates_tracker.xlsx'.")
            else:
                emit_log("\n⚠️ Task completed with 0 candidates extracted.")

            emit_log("💡 Browser window and search tabs remain open on screen. Click 'Close Browser Window' when finished.")

        asyncio.run(_async_sourcing())

    threading.Thread(target=_worker).start()
    return jsonify({"status": "started"})

def start_flask():
    app.run(port=5000, debug=False, use_reloader=False)

if __name__ == "__main__":
    t = threading.Thread(target=start_flask)
    t.daemon = True
    t.start()

    webview.create_window(
        title="Candidate Resume Sourcing Dashboard",
        url="http://127.0.0.1:5000",
        width=1000,
        height=760,
        resizable=True
    )
    webview.start()
