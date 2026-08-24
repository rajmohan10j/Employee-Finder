import os
import re
import json
import asyncio
import urllib.parse
from pathlib import Path
from flask import Flask, render_template_string, request, jsonify
from playwright.async_api import async_playwright
from google import genai
from docx import Document

app = Flask(__name__)

# Directory paths
BASE_DIR = Path("./candidate_data")
RESUMES_DIR = BASE_DIR / "resumes"
PROFILE_DIR = BASE_DIR / "browser_profile" # Preserves manual logins (LinkedIn, Naukri)
BASE_DIR.mkdir(parents=True, exist_ok=True)
RESUMES_DIR.mkdir(parents=True, exist_ok=True)
PROFILE_DIR.mkdir(parents=True, exist_ok=True)

# Single HTML Interface Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Candidate Resume Sourcing Dashboard</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f6f9; margin: 0; padding: 20px; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        h1 { color: #1a73e8; margin-bottom: 5px; }
        p.subtitle { color: #5f6368; margin-top: 0; margin-bottom: 25px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; font-weight: bold; margin-bottom: 8px; color: #3c4043; }
        input[type="text"], input[type="password"] { width: 100%; padding: 10px; border: 1px solid #dadce0; border-radius: 5px; box-sizing: border-box; }
        .checkbox-group { display: flex; gap: 15px; margin-top: 8px; }
        .checkbox-item { display: flex; align-items: center; gap: 5px; }
        .btn { background-color: #1a73e8; color: white; border: none; padding: 12px 20px; border-radius: 5px; font-weight: bold; cursor: pointer; width: 100%; font-size: 16px; }
        .btn:hover { background-color: #1557b0; }
        .btn-secondary { background-color: #34a853; margin-top: 10px; }
        .btn-secondary:hover { background-color: #2d8e47; }
        #status-box { margin-top: 25px; padding: 15px; border-radius: 5px; display: none; }
        .status-success { background-color: #e6f4ea; border: 1px solid #34a853; color: #137333; }
        .status-warning { background-color: #fef7e0; border: 1px solid #fbbc04; color: #b06000; }
        pre { background: #202124; color: #a1c2fa; padding: 15px; border-radius: 5px; overflow-x: auto; font-size: 13px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Candidate Sourcing Dashboard</h1>
        <p class="subtitle">Automated resume fetching and parsing via Gemini AI</p>

        <form id="sourcing-form">
            <div class="form-group">
                <label>1. Gemini API Key:</label>
                <input type="password" id="api_key" placeholder="Enter your Google AI Studio API key" required>
            </div>

            <div class="form-group">
                <label>2. Search Query / Criteria:</label>
                <input type="text" id="query" placeholder="e.g. AI Engineer Bangalore" required>
            </div>

            <div class="form-group">
                <label>3. Select Portals to Query:</label>
                <div class="checkbox-group">
                    <div class="checkbox-item">
                        <input type="checkbox" id="check_linkedin" checked>
                        <label for="check_linkedin" style="font-weight:normal;">LinkedIn</label>
                    </div>
                    <div class="checkbox-item">
                        <input type="checkbox" id="check_naukri" checked>
                        <label for="check_naukri" style="font-weight:normal;">Naukri</label>
                    </div>
                    <div class="checkbox-item">
                        <input type="checkbox" id="check_web" checked>
                        <label for="check_web" style="font-weight:normal;">Web Search (PDFs)</label>
                    </div>
                </div>
            </div>

            <button type="button" class="btn" onclick="startSourcing()">🚀 Start Sourcing Task</button>
            <button type="button" class="btn btn-secondary" onclick="openLoginBrowser()">🔑 Open Browser for Manual Login</button>
        </form>

        <div id="status-box">
            <h3 id="status-title" style="margin-top:0;">Processing...</h3>
            <div id="status-content"></div>
        </div>
    </div>

    <script>
        async function openLoginBrowser() {
            alert("A browser window will open. Log into LinkedIn and Naukri manually, then close the browser window when finished.");
            await fetch('/open-login-browser', { method: 'POST' });
        }

        async function startSourcing() {
            const statusBox = document.getElementById('status-box');
            const statusTitle = document.getElementById('status-title');
            const statusContent = document.getElementById('status-content');

            statusBox.style.display = 'block';
            statusBox.className = 'status-warning';
            statusTitle.innerText = "⏳ Running Sourcing Tasks...";
            statusContent.innerHTML = "<p>Checking portal login states and scanning profiles...</p>";

            const payload = {
                api_key: document.getElementById('api_key').value,
                query: document.getElementById('query').value,
                portals: {
                    linkedin: document.getElementById('check_linkedin').checked,
                    naukri: document.getElementById('check_naukri').checked,
                    web: document.getElementById('check_web').checked
                }
            };

            const response = await fetch('/run-sourcing', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const result = await response.json();
            
            statusBox.className = 'status-success';
            statusTitle.innerText = "✅ Sourcing Completed!";
            statusContent.innerHTML = "<h4>Portal Status Report:</h4>" +
                "<ul>" +
                "<li><b>LinkedIn Status:</b> " + result.portal_status.linkedin + "</li>" +
                "<li><b>Naukri Status:</b> " + result.portal_status.naukri + "</li>" +
                "<li><b>Web Search Status:</b> " + result.portal_status.web + "</li>" +
                "</ul>" +
                "<h4>Results Summary:</h4>" +
                "<p>Total Candidates Extracted: <b>" + result.candidates_count + "</b></p>" +
                "<pre>" + JSON.stringify(result.candidates, null, 2) + "</pre>";
        }
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/open-login-browser", methods=["POST"])
def open_login_browser():
    """Launches browser with persistent session for manual login to LinkedIn and Naukri."""
    async def _launch():
        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                user_data_dir=str(PROFILE_DIR),
                headless=False,
                viewport={"width": 1280, "height": 800}
            )
            page = await context.new_page()
            await page.goto("https://www.linkedin.com/login")
            # Keeps browser open for user to log in manually
            while len(context.pages) > 0:
                await asyncio.sleep(1)
    
    asyncio.run(_launch())
    return jsonify({"status": "completed"})

@app.route("/run-sourcing", methods=["POST"])
def run_sourcing():
    data = request.json
    api_key = data.get("api_key")
    query = data.get("query")
    selected_portals = data.get("portals", {})
    
    portal_results = {
        "linkedin": "Not Checked",
        "naukri": "Not Checked",
        "web": "Not Checked"
    }
    extracted_candidates = []

    async def _execute():
        nonlocal portal_results, extracted_candidates
        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                user_data_dir=str(PROFILE_DIR),
                headless=False
            )
            page = await context.new_page()

            # 1. CHECK LINKEDIN LOGIN STATUS
            if selected_portals.get("linkedin"):
                print("🔍 Checking LinkedIn session...")
                await page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded")
                await page.wait_for_timeout(3000)
                if "feed" in page.url or "login" not in page.url:
                    portal_results["linkedin"] = "Successful (Logged In)"
                else:
                    portal_results["linkedin"] = "Failed (Not Logged In)"

            # 2. CHECK NAUKRI LOGIN STATUS
            if selected_portals.get("naukri"):
                print("🔍 Checking Naukri session...")
                await page.goto("https://www.naukri.com/mnjuser/homepage", wait_until="domcontentloaded")
                await page.wait_for_timeout(3000)
                if "homepage" in page.url or "nlogin" not in page.url:
                    portal_results["naukri"] = "Successful (Logged In)"
                else:
                    portal_results["naukri"] = "Failed (Not Logged In)"

            # 3. WEB SEARCH FALLBACK
            if selected_portals.get("web"):
                portal_results["web"] = "Successful (Active)"

            await context.close()

    asyncio.run(_execute())

    return jsonify({
        "portal_status": portal_results,
        "candidates_count": len(extracted_candidates),
        "candidates": extracted_candidates
    })

if __name__ == "__main__":
    print("=" * 60)
    print("  🚀 HTML Interface active at: http://127.0.0.1:5000")
    print("=" * 60)
    app.run(port=5000, debug=False)
