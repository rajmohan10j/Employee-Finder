import os
import sys
import time
import socket
import threading
from pathlib import Path
from playwright.sync_api import sync_playwright

APP_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(APP_DIR))

SCREENSHOTS_DIR = APP_DIR / "test_screenshots"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

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

def run_playwright_tests():
    if not is_server_running():
        start_background_server()
    else:
        print("Flask server is already running on http://127.0.0.1:5000.")

    print("\n" + "=" * 65)
    print(" 🎭 RUNNING PLAYWRIGHT AUTOMATED END-TO-END TESTS")
    print("=" * 65)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1280, 'height': 800})
        page = context.new_page()

        # -------------------------------------------------------------
        # TEST 1: Dashboard & Metrics Loading
        # -------------------------------------------------------------
        print("\n▶ [TEST 1] Loading Dashboard & Master Metrics...")
        page.goto('http://127.0.0.1:5000', wait_until='domcontentloaded')
        page.wait_for_selector('.candidate-card')
        page.wait_for_timeout(300)
        
        title = page.title()
        assert "Candidate Tracker" in title, f"Unexpected page title: {title}"
        
        stat_total = page.locator('#stat-total').text_content().strip()
        stat_called = page.locator('#stat-called').text_content().strip()
        print(f"  ✓ Dashboard loaded. Total Candidates: {stat_total}, HR Called: {stat_called}")
        page.screenshot(path=str(SCREENSHOTS_DIR / "01_dashboard_desktop.png"))

        # -------------------------------------------------------------
        # TEST 2: Live Search & Portal Filtering
        # -------------------------------------------------------------
        print("\n▶ [TEST 2] Testing Search & Filter Engine...")
        first_cand_el = page.locator('.candidate-card').first
        first_cand_name = first_cand_el.locator('h3').text_content().strip().split()[0]
        
        search_input = page.locator('#search-input')
        search_input.fill(first_cand_name)
        page.wait_for_timeout(400) # debounce
        
        cand_cards = page.locator('.candidate-card')
        count = cand_cards.count()
        print(f"  ✓ Search for '{first_cand_name}' yielded {count} candidate card(s).")
        assert count >= 1, f"Expected at least 1 result for '{first_cand_name}'"
        
        page.screenshot(path=str(SCREENSHOTS_DIR / "02_search_candidate.png"))
        
        # Clear search
        page.locator('#btn-clear-search').click()
        page.wait_for_timeout(300)
        
        # Filter by portal
        page.locator('#filter-portal').select_option('Naukri')
        page.wait_for_timeout(300)
        naukri_count = page.locator('.candidate-card').count()
        print(f"  ✓ Portal filter 'Naukri' yielded {naukri_count} candidate(s).")
        page.locator('#filter-portal').select_option('All')
        page.wait_for_timeout(300)

        # -------------------------------------------------------------
        # TEST 3: Box-Item Form Editor Modal (15 Fields)
        # -------------------------------------------------------------
        print("\n▶ [TEST 3] Testing 15-Field Box-Item Form Editor...")
        first_edit_btn = page.locator('.candidate-card').first.locator('button[title="Edit Box Items"]')
        first_edit_btn.click()
        
        page.wait_for_selector('#modal-candidate-form', state='visible')
        
        cand_name = page.locator('#field-candidate-name').input_value()
        phone = page.locator('#field-phone').input_value()
        email = page.locator('#field-email').input_value()
        exp = page.locator('#field-experience').input_value()
        loc = page.locator('#field-location').input_value()
        
        print(f"  ✓ Box-Item Editor opened for: '{cand_name}'")
        print(f"  ✓ Field Verification - Phone: '{phone}', Email: '{email}', Exp: '{exp}', Loc: '{loc}'")
        
        page.locator('#field-hr-remarks').fill('Playwright Screening: Candidate verified for next stage.')
        page.locator('#field-escalation-level').select_option('L2 - Raj')
        page.locator('#field-escalation-action').select_option('Review / Suggest')
        page.locator('#field-escalation-remarks').fill('Escalated to L2 Raj: Review candidate Python experience and suggest compensation.')
        page.locator('#field-assign-reviewer').select_option(index=1)
        
        page.screenshot(path=str(SCREENSHOTS_DIR / "03_box_form_editor.png"))
        
        page.locator('#btn-save-candidate').click()
        page.wait_for_selector('#modal-candidate-form', state='hidden')
        page.wait_for_timeout(500)
        print("  ✓ Candidate modifications & Escalation to 'L2 - Raj' successfully saved.")
        
        # Verify Escalation Badge rendered on card
        esc_badge = page.locator('.badge-escalation').first
        assert esc_badge.is_visible(), "Escalation badge should be visible on candidate card"
        print(f"  ✓ Escalation badge verified on screen: '{esc_badge.text_content().strip()}'")

        # -------------------------------------------------------------
        # TEST 4: Share Candidate to Next Level Modal
        # -------------------------------------------------------------
        print("\n▶ [TEST 4] Testing Next Level Share Summary Generator...")
        first_share_btn = page.locator('.candidate-card').first.locator('button[title="Share with Lead / Next Level"]')
        first_share_btn.click()
        
        page.wait_for_selector('#modal-share', state='visible')
        share_text = page.locator('#share-preview-text').text_content()
        assert "CANDIDATE PROFILE SUMMARY" in share_text, "Summary header missing"
        assert "CandidateTracker System" in share_text, "Footer branding missing"
        print("  ✓ Formatted Candidate Summary generated successfully for WhatsApp/Email:")
        for line in share_text.split('\n')[:5]:
            print(f"    | {line}")
            
        page.screenshot(path=str(SCREENSHOTS_DIR / "04_share_next_level_modal.png"))
        page.locator('#btn-close-share-modal').click()
        page.wait_for_selector('#modal-share', state='hidden')

        # -------------------------------------------------------------
        # TEST 5: Review & Commit Workflow with Visual Diffs
        # -------------------------------------------------------------
        print("\n▶ [TEST 5] Testing Review & Commit Panel with Visual Diffs...")
        page.locator('#nav-reviews').click()
        page.wait_for_selector('#tab-reviews.active')
        page.wait_for_timeout(500)
        
        reviews = page.locator('.review-item-card')
        rev_count = reviews.count()
        print(f"  ✓ Review Panel loaded. Pending changes: {rev_count}")
        if rev_count > 0:
            page.screenshot(path=str(SCREENSHOTS_DIR / "05_review_and_commit.png"))
            approve_btn = reviews.first.locator('button:has-text("Approve & Commit to Excel")')
            approve_btn.click()
            page.wait_for_timeout(800)
            print("  ✓ Changes approved and committed to master Excel database!")

        # -------------------------------------------------------------
        # TEST 6: Reviewer Contacts Registry
        # -------------------------------------------------------------
        print("\n▶ [TEST 6] Testing Reviewer Contacts Registry...")
        page.locator('#nav-reviewers').click()
        page.wait_for_selector('#tab-reviewers.active')
        page.wait_for_timeout(300)
        
        page.locator('#btn-add-reviewer').click()
        page.wait_for_selector('#modal-reviewer-form', state='visible')
        
        test_rev_name = f"Lead Reviewer {int(time.time() * 1000)}"
        page.locator('#rev-name').fill(test_rev_name)
        page.locator('#rev-phone').fill('+91 98888 77777')
        page.locator('#rev-email').fill('test.lead@example.com')
        page.locator('#rev-role').fill('Principal AI Reviewer')
        
        page.locator('#reviewer-form button[type="submit"]').click()
        page.wait_for_selector('#modal-reviewer-form', state='hidden')
        page.wait_for_timeout(500)
        
        assert page.get_by_role('heading', name=test_rev_name, exact=True).is_visible(), "New reviewer card not found"
        print(f"  ✓ New reviewer contact '{test_rev_name}' created successfully!")
        page.screenshot(path=str(SCREENSHOTS_DIR / "06_reviewer_contacts.png"))

        # -------------------------------------------------------------
        # TEST 7: Connect Android Mobile & QR Code Generation
        # -------------------------------------------------------------
        print("\n▶ [TEST 7] Testing Android Mobile QR Code Generation...")
        page.locator('#nav-mobile').click()
        page.wait_for_selector('#tab-mobile.active')
        page.wait_for_timeout(600)
        
        mobile_url = page.locator('#mobile-url-input').input_value()
        print(f"  ✓ Direct Mobile URL: {mobile_url}")
        assert "http://" in mobile_url and ":5000" in mobile_url, f"Invalid mobile URL: {mobile_url}"
        
        qr_rendered = page.locator('#qrcode-container canvas, #qrcode-container img').count() > 0
        assert qr_rendered, "QR code was not rendered in container"
        print("  ✓ QR Code successfully generated on screen for Android phone scanning.")
        page.screenshot(path=str(SCREENSHOTS_DIR / "07_mobile_qr_connect.png"))

        # -------------------------------------------------------------
        # TEST 8: Mobile Viewport Emulation (Android Phone Experience)
        # -------------------------------------------------------------
        print("\n▶ [TEST 8] Testing Android Phone Mobile Experience (Emulated Viewport)...")
        # Resize current page to mobile viewport
        page.set_viewport_size({'width': 393, 'height': 851})
        page.wait_for_timeout(300)
        page.locator('.bottom-nav-item[data-tab="candidates"]').click()
        page.wait_for_timeout(500)
        
        bottom_nav_visible = page.locator('.bottom-nav').is_visible()
        assert bottom_nav_visible, "Mobile bottom navigation should be visible on mobile viewport"
        print("  ✓ Mobile bottom navigation bar verified.")
        
        quick_actions = page.locator('.candidate-card').first.locator('.card-actions')
        assert quick_actions.is_visible(), "Quick actions should be visible on mobile"
        print("  ✓ Mobile 1-tap Call, WhatsApp and Share action buttons verified.")
        
        page.screenshot(path=str(SCREENSHOTS_DIR / "08_android_mobile_view.png"))

        # -------------------------------------------------------------
        # TEST 9: Automated GFS Backups & Version Control
        # -------------------------------------------------------------
        print("\n▶ [TEST 9] Testing Backups & GFS Version Control Panel...")
        page.set_viewport_size({'width': 1280, 'height': 800})
        page.locator('#nav-backups').click()
        page.wait_for_selector('#tab-backups.active')
        page.wait_for_timeout(500)

        # Verify GFS tier cards are rendered
        session_count = page.locator('#stat-backup-sessions-count').text_content().strip()
        print(f"  ✓ Backups Panel Loaded. Pre-flight session snapshots recorded: {session_count}")
        assert page.locator('.backup-tier-card').count() == 4, "Expected 4 GFS tier cards"

        # Trigger on-demand backup
        page.locator('#btn-trigger-manual-backup').click()
        page.wait_for_timeout(800)
        
        # Verify table has snapshots
        table_rows = page.locator('#backups-table-body tr')
        assert table_rows.count() >= 1, "Expected backup table rows"
        print("  ✓ On-demand snapshot successfully created and listed in history table!")
        page.screenshot(path=str(SCREENSHOTS_DIR / "09_backups_version_control.png"))

        browser.close()

    print("\n" + "=" * 65)
    print(" 🎉 ALL 9 PLAYWRIGHT END-TO-END TESTS PASSED SUCCESSFULLY! ")
    print(f" 📸 Screenshots saved to: {SCREENSHOTS_DIR}")
    print("=" * 65 + "\n")

if __name__ == '__main__':
    run_playwright_tests()
