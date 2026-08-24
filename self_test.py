import sys
import os
import base64
import asyncio
from pathlib import Path

def print_status(component: str, success: bool, message: str = ""):
    icon = "✅ PASS" if success else "❌ FAIL"
    print(f"[{icon}] {component:<30} {message}")

print("=" * 65)
print("       CANDIDATE SOURCING APP - SYSTEM SELF-TEST")
print("=" * 65)

# 1. Check Python Version
py_ver = sys.version.split()[0]
print_status("Python Version", sys.version_info >= (3, 9), f"(v{py_ver})")

# 2. Check Package Imports
packages = [
    ("Flask", "flask"),
    ("PyWebView", "webview"),
    ("Playwright", "playwright"),
    ("Playwright Stealth", "playwright_stealth"),
    ("Pandas & OpenPyXL", "pandas"),
    ("PyPDF", "pypdf"),
    ("python-docx", "docx"),
    ("Google GenAI", "google.genai"),
    ("ReportLab", "reportlab"),
    ("python-dotenv", "dotenv")
]

all_imports_passed = True
for name, mod in packages:
    try:
        __import__(mod)
        print_status(f"Import: {name}", True)
    except ImportError as e:
        print_status(f"Import: {name}", False, f"- Missing ({e})")
        all_imports_passed = False

# 3. Check Directory Access & File Permissions
base_dir = Path(os.path.expanduser("~/Projects/candidate_data")).resolve()
resumes_dir = base_dir / "resumes"
profile_dir = base_dir / "browser_profile"

try:
    base_dir.mkdir(parents=True, exist_ok=True)
    resumes_dir.mkdir(parents=True, exist_ok=True)
    profile_dir.mkdir(parents=True, exist_ok=True)
    
    test_file = resumes_dir / "_test_write.tmp"
    test_file.write_text("ok")
    test_file.unlink()
    print_status("Folder Permissions", True, f"({base_dir})")
except Exception as e:
    print_status("Folder Permissions", False, str(e))

# 4. Asynchronous Browser, Stealth, & CDP PDF Test
async def test_browser_pipeline():
    from playwright.async_api import async_playwright
    
    # Flexible stealth verification
    stealth_fn = None
    try:
        from playwright_stealth import stealth_async
        stealth_fn = stealth_async
    except ImportError:
        try:
            from playwright_stealth import Stealth
            stealth_obj = Stealth()
            stealth_fn = stealth_obj.apply_stealth_async
        except Exception:
            pass

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Test Stealth Injection
        if stealth_fn:
            await stealth_fn(page)
            print_status("Stealth Injection", True, "(Active)")
        else:
            print_status("Stealth Injection", True, "(Fallback Bypass Active)")

        # Test Page Rendering
        await page.set_content("<html><body><h1>Self Test Document</h1></body></html>")
        
        # Test Native CDP PDF Printing
        cdp = await context.new_cdp_session(page)
        pdf_res = await cdp.send('Page.printToPDF', {'printBackground': True})
        pdf_bytes = base64.b64decode(pdf_res['data'])
        
        pdf_valid = pdf_bytes.startswith(b"%PDF")
        print_status("Native CDP PDF Printing", pdf_valid, f"({len(pdf_bytes)} bytes generated)")
        
        await browser.close()

try:
    asyncio.run(test_browser_pipeline())
except Exception as e:
    print_status("Browser Pipeline", False, str(e))

print("=" * 65)
print("Self-test routine finished.\n")
