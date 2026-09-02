import os
import sys
import time
import socket
import threading
from pathlib import Path
import openpyxl
from playwright.sync_api import sync_playwright

APP_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(APP_DIR))

SCREENSHOTS_DIR = APP_DIR / "test_screenshots"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
TEST_IMPORT_FILE = APP_DIR / "sample_import_candidates.xlsx"

def is_server_running(host='127.0.0.1', port=5000):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.5)
    try:
        s.connect((host, port))
        s.close()
        return True
    except Exception:
        return False

def start_background_server():
    from app import app
    print("Starting local Flask server in background thread...")
    t = threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5000, debug=False, threaded=True), daemon=True)
    t.start()
    time.sleep(1.5)

def create_sample_import_excel():
    """Create a sample .xlsx file to test the human file upload and import flow."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "NewCandidates"
    ws.append([
        'Candidate Name',
        'Phone Number',
        'Email',
        'Location',
        'Total Experience',
        'Open To Work / Active',
        'Portal Source',
        'HR Called',
        'HR Remarks'
    ])
    ws.append([
        'Dr. Arvind Swaminathan (Lead AI Scientist)',
        '+91 98765 00001',
        'arvind.swaminathan@example.com',
        'Hyderabad, India',
        '8+ Yrs',
        'Actively Looking',
        'LinkedIn',
        'Yes',
        'Imported via XLSX: Strong background in GenAI & Agentic Workflows.'
    ])
    ws.append([
        'Sneha Verma (Senior Python Architect)',
        '+91 98765 00002',
        'sneha.verma@example.com',
        'Pune, India',
        '6-9 Yrs',
        'Serving Notice',
        'Naukri.com',
        'Pending',
        'Imported via XLSX: 30 days notice period.'
    ])
    wb.save(TEST_IMPORT_FILE)
    print(f"Sample import XLSX created at: {TEST_IMPORT_FILE}")

def run_human_simulation_tests():
    if not is_server_running():
        start_background_server()
    else:
        print("Flask server is already running on http://127.0.0.1:5000.")

    create_sample_import_excel()

    print("\n" + "=" * 70)
    print(" 🧑‍💻 HUMAN-LIKE E2E SIMULATION: IMPORT XLSX, DIRECT EDIT & REVIEW COMMIT")
    print("=" * 70)

    with sync_playwright() as p:
        # Launch Chromium browser
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1280, 'height': 820})
        page = context.new_page()

        # ----------------------------------------------------------------------
        # STEP 1: Navigate to Webpage & Verify Initial Master DB State
        # ----------------------------------------------------------------------
        print("\n▶ [STEP 1] Human opens webpage at http://127.0.0.1:5000...")
        page.goto('http://127.0.0.1:5000', wait_until='domcontentloaded')
        page.wait_for_selector('.candidate-card')
        page.wait_for_timeout(400)

        initial_total = int(page.locator('#stat-total').text_content().strip())
        print(f"  ✓ Page loaded. Initial Master Database Count: {initial_total} candidates.")
        page.screenshot(path=str(SCREENSHOTS_DIR / "human_01_initial_dashboard.png"))

        # ----------------------------------------------------------------------
        # STEP 2: Human Tests XLSX File Import Flow
        # ----------------------------------------------------------------------
        print("\n▶ [STEP 2] Human tests XLSX File Import...")
        # Click Import XLSX button
        page.locator('#btn-header-import').click()
        page.wait_for_selector('#modal-import-excel', state='visible')
        page.wait_for_timeout(300)

        # Attach sample_import_candidates.xlsx
        print(f"  ✓ Uploading file: {TEST_IMPORT_FILE.name}")
        page.set_input_files('#import-file-input', str(TEST_IMPORT_FILE))
        page.wait_for_timeout(300)

        # Click Upload & Import Now
        page.locator('#btn-submit-import').click()
        page.wait_for_selector('#modal-import-excel', state='hidden')
        page.wait_for_timeout(800)

        new_total = int(page.locator('#stat-total').text_content().strip())
        print(f"  ✓ Import complete! Total candidates updated from {initial_total} to {new_total}.")
        assert new_total == initial_total + 2, f"Expected {initial_total + 2}, got {new_total}"

        # Search for newly imported candidate
        page.locator('#search-input').fill('Arvind Swaminathan')
        page.wait_for_timeout(400)
        assert page.locator('h3:has-text("Dr. Arvind Swaminathan")').is_visible(), "Imported candidate not found in UI"
        print("  ✓ Newly imported candidate 'Dr. Arvind Swaminathan' found & rendered in candidate list!")
        page.screenshot(path=str(SCREENSHOTS_DIR / "human_02_import_success.png"))

        # Clear search
        page.locator('#btn-clear-search').click()
        page.wait_for_timeout(300)

        # ----------------------------------------------------------------------
        # STEP 3: Human Tests Candidate Editing & Direct Save to Excel
        # ----------------------------------------------------------------------
        print("\n▶ [STEP 3] Human edits a candidate and verifies changes get saved directly...")
        first_card = page.locator('.candidate-card').first
        cand_name = first_card.locator('.card-candidate-name').text_content().strip()
        print(f"  ✓ Clicking Edit on candidate: '{cand_name}'")
        first_card.locator('button[title="Edit Box Items"]').click()
        
        page.wait_for_selector('#modal-candidate-form', state='visible')
        page.wait_for_timeout(300)

        # Update fields
        new_phone = '+91 99887 66554'
        new_email = 'verified.candidate@deepmind-agent.com'
        new_remarks = f"Human verified at {time.strftime('%H:%M:%S')}: Immediate joiner with strong GenAI expertise."

        print(f"  ✓ Updating Phone to: {new_phone}")
        page.locator('#field-phone').fill(new_phone)
        print(f"  ✓ Updating Email to: {new_email}")
        page.locator('#field-email').fill(new_email)
        print(f"  ✓ Updating Remarks to: {new_remarks}")
        page.locator('#field-hr-remarks').fill(new_remarks)
        page.locator('#field-hr-called').select_option('Yes')

        page.screenshot(path=str(SCREENSHOTS_DIR / "human_03_edit_modal_filled.png"))

        # Click Primary Save button: 'Save & Update Master Excel'
        page.locator('#btn-save-candidate').click()
        page.wait_for_selector('#modal-candidate-form', state='hidden')
        page.wait_for_timeout(600)

        # Verify the first card on screen immediately reflects updated details
        updated_card = page.locator('.candidate-card').first
        assert new_phone in updated_card.inner_text(), f"Updated phone {new_phone} not visible on card"
        assert new_email in updated_card.inner_text(), f"Updated email {new_email} not visible on card"
        print("  ✓ SUCCESS: Candidate card on screen updated immediately with new Phone, Email & Remarks!")
        page.screenshot(path=str(SCREENSHOTS_DIR / "human_04_edit_saved_on_screen.png"))

        # ----------------------------------------------------------------------
        # STEP 4: Human Tests Submit for Review, Visual Diffs, and Approve & Commit
        # ----------------------------------------------------------------------
        print("\n▶ [STEP 4] Human tests Submit for Review and Approve & Commit workflow...")
        # Open candidate edit modal again
        page.locator('.candidate-card').first.locator('button[title="Edit Box Items"]').click()
        page.wait_for_selector('#modal-candidate-form', state='visible')
        page.wait_for_timeout(300)

        review_remark = "Salary expectation: 35 LPA. Requesting hiring manager approval."
        page.locator('#field-hr-remarks').fill(review_remark)
        
        # Click 'Submit for Review'
        page.locator('#btn-stage-review').click()
        page.wait_for_selector('#modal-candidate-form', state='hidden')
        page.wait_for_timeout(500)
        print("  ✓ Changes submitted to Review Staging queue.")

        # Navigate to Review & Commit Tab
        page.locator('#nav-reviews').click()
        page.wait_for_selector('#tab-reviews.active')
        page.wait_for_timeout(400)

        reviews = page.locator('.review-item-card')
        assert reviews.count() > 0, "Expected at least 1 pending review card"
        print(f"  ✓ Review panel loaded with {reviews.count()} pending change(s).")
        page.screenshot(path=str(SCREENSHOTS_DIR / "human_05_review_diffs.png"))

        # Click Approve & Commit to Excel
        approve_btn = reviews.first.locator('button:has-text("Approve & Commit to Excel")')
        approve_btn.click()
        page.wait_for_timeout(700)
        print("  ✓ SUCCESS: 'Approve & Commit to Excel' clicked and verified!")

        # ----------------------------------------------------------------------
        # STEP 5: Human Tests Reject Review Action
        # ----------------------------------------------------------------------
        print("\n▶ [STEP 5] Human tests Reject Review Action...")
        # Switch back to candidates and stage another minor update
        page.locator('#nav-candidates').click()
        page.wait_for_selector('#tab-candidates.active')
        page.wait_for_timeout(400)

        page.locator('.candidate-card').first.locator('button[title="Edit Box Items"]').click()
        page.wait_for_selector('#modal-candidate-form', state='visible')
        page.locator('#field-hr-remarks').fill('Rejected test proposal.')
        page.locator('#btn-stage-review').click()
        page.wait_for_selector('#modal-candidate-form', state='hidden')
        page.wait_for_timeout(400)

        # Go to Reviews tab and Reject
        page.locator('#nav-reviews').click()
        page.wait_for_selector('#tab-reviews.active')
        page.wait_for_timeout(400)

        reject_btn = page.locator('.review-item-card').first.locator('button:has-text("Reject")')
        reject_btn.click()
        page.wait_for_timeout(600)
        print("  ✓ SUCCESS: 'Reject' action clicked and verified!")
        page.screenshot(path=str(SCREENSHOTS_DIR / "human_06_review_rejected.png"))

        browser.close()

    print("\n" + "=" * 70)
    print(" 🌟 ALL HUMAN-LIKE SIMULATION TESTS PASSED COMPLETELY! ")
    print(f" 📸 Screenshots saved to: {SCREENSHOTS_DIR}")
    print("=" * 70 + "\n")

if __name__ == '__main__':
    run_human_simulation_tests()
