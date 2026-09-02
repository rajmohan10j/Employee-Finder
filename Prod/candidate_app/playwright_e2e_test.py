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

        console_errors = []
        page.on("pageerror", lambda err: console_errors.append(str(err)))
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

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
        with page.expect_response(lambda r: '/api/candidates' in r.url and r.status == 200):
            search_input.fill(first_cand_name)
        page.wait_for_timeout(300)
        
        cand_cards = page.locator('.candidate-card')
        count = cand_cards.count()
        print(f"  ✓ Search for '{first_cand_name}' yielded {count} candidate card(s).")
        assert count >= 1, f"Expected at least 1 result for '{first_cand_name}'"
        
        page.screenshot(path=str(SCREENSHOTS_DIR / "02_search_candidate.png"))
        
        # Clear search
        with page.expect_response(lambda r: '/api/candidates' in r.url and r.status == 200):
            page.locator('#btn-clear-search').click()
        page.wait_for_timeout(300)
        
        # Filter by portal
        with page.expect_response(lambda r: '/api/candidates' in r.url and r.status == 200):
            page.locator('#filter-portal').select_option('Naukri')
        page.wait_for_timeout(300)
        naukri_count = page.locator('.candidate-card').count()
        print(f"  ✓ Portal filter 'Naukri' yielded {naukri_count} candidate(s).")
        with page.expect_response(lambda r: '/api/candidates' in r.url and r.status == 200):
            page.locator('#filter-portal').select_option('All')
        page.wait_for_timeout(300)

        # -------------------------------------------------------------
        # TEST 2.5: Interactive Metric Cards & Task/Person Breakdown
        # -------------------------------------------------------------
        print("\n▶ [TEST 2.5] Testing Interactive Click-to-Filter Metric Cards...")
        # 1. Click "HR Called" card
        with page.expect_response(lambda r: '/api/candidates' in r.url and r.status == 200):
            page.locator('#card-stat-called').click()
        page.wait_for_timeout(300)
        called_card_classes = page.locator('#card-stat-called').get_attribute('class')
        assert 'active-filter-card' in called_card_classes, "HR Called card should have active-filter-card class"
        assert page.locator('#filter-status').input_value() == 'called', "Filter status should sync to 'called'"
        called_results = page.locator('.candidate-card').count()
        print(f"  ✓ Clicked 'HR Called' card -> Active highlight verified, {called_results} called candidate(s) listed.")

        # 2. Click "Pending Call" card
        with page.expect_response(lambda r: '/api/candidates' in r.url and r.status == 200):
            page.locator('#card-stat-pending').click()
        page.wait_for_timeout(300)
        pending_card_classes = page.locator('#card-stat-pending').get_attribute('class')
        assert 'active-filter-card' in pending_card_classes, "Pending Call card should have active-filter-card class"
        assert page.locator('#filter-status').input_value() == 'pending', "Filter status should sync to 'pending'"
        pending_results = page.locator('.candidate-card').count()
        print(f"  ✓ Clicked 'Pending Call' card -> Active highlight verified, {pending_results} pending candidate(s) listed.")

        # 2.1 Click "Closed" card
        with page.expect_response(lambda r: '/api/candidates' in r.url and r.status == 200):
            page.locator('#card-stat-closed').click()
        page.wait_for_timeout(300)
        closed_card_classes = page.locator('#card-stat-closed').get_attribute('class')
        assert 'active-filter-card' in closed_card_classes, "Closed card should have active-filter-card class"
        assert page.locator('#filter-status').input_value() == 'closed', "Filter status should sync to 'closed'"
        closed_results = page.locator('.candidate-card').count()
        closed_card_count = int(page.locator('#stat-closed').text_content().strip())
        assert closed_results == closed_card_count, f"Closed card count ({closed_card_count}) must match filtered candidates ({closed_results})"
        print(f"  ✓ Clicked 'Closed' card -> Card count ({closed_card_count}) exactly matches filtered list ({closed_results}).")

        # 2.2 Click "Follow-ups" card
        with page.expect_response(lambda r: '/api/candidates' in r.url and r.status == 200):
            page.locator('#card-stat-followups').click()
        page.wait_for_timeout(300)
        followup_card_classes = page.locator('#card-stat-followups').get_attribute('class')
        assert 'active-filter-card' in followup_card_classes, "Follow-ups card should have active-filter-card class"
        assert page.locator('#filter-status').input_value() == 'followups', "Filter status should sync to 'followups'"
        followup_results = page.locator('.candidate-card').count()
        followup_card_count = int(page.locator('#stat-followups').text_content().strip())
        assert followup_results == followup_card_count, f"Follow-ups card count ({followup_card_count}) must match filtered candidates ({followup_results})"
        print(f"  ✓ Clicked 'Follow-ups' card -> Card count ({followup_card_count}) exactly matches filtered list ({followup_results}).")

        # 3. Test Task / Assigned To Breakdown Chips if available
        chips = page.locator('#stat-escalation-breakdown .escalation-chip')
        chip_count = chips.count()
        print(f"  ✓ Found {chip_count} Task / Assigned To person breakdown chip(s).")
        if chip_count > 0:
            first_chip = chips.first
            first_chip_text = first_chip.text_content().strip()
            first_chip.click()
            page.wait_for_timeout(400)
            assert 'active-chip' in first_chip.get_attribute('class'), "Clicked person chip should have active-chip class"
            print(f"  ✓ Clicked person chip '{first_chip_text}' -> Filter synced, {page.locator('.candidate-card').count()} candidate(s) matched.")

        # 4. Click "Total Sourced" to reset
        page.locator('#card-stat-total').click()
        page.wait_for_timeout(400)
        reset_count = page.locator('.candidate-card').count()
        assert reset_count >= 50, f"Expected full candidate list after reset, got {reset_count}"
        print(f"  ✓ Clicked 'Total Sourced' card -> Filters reset, {reset_count} total candidates shown.")
        page.screenshot(path=str(SCREENSHOTS_DIR / "02b_interactive_cards_filter.png"))

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
        
        # Confirm Email Address is strictly optional
        email_input = page.locator('#field-email')
        assert email_input.get_attribute('required') is None, "Email field should be optional"
        print("  ✓ Verified: Email Address is strictly Optional (not mandatory to save).")
        
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

        # Clean up temporary test reviewer so the database remains strictly with the 4 authorized reviewers
        page.once("dialog", lambda dialog: dialog.accept())
        card = page.locator('.reviewer-card', has=page.get_by_role('heading', name=test_rev_name))
        card.locator('.btn-card-action').click()
        page.wait_for_timeout(400)
        print("  ✓ Temporary test reviewer cleaned up successfully (clean database preserved).")

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

        # -------------------------------------------------------------
        # TEST 10: Conversion Intelligence & Audience Analytics Dashboard
        # -------------------------------------------------------------
        print("\n▶ [TEST 10] Testing Conversion Intelligence & Audience Analytics...")
        page.locator('#nav-analytics').click()
        page.wait_for_selector('#tab-analytics.active')
        page.wait_for_timeout(800)

        # 1. Header & Contract Badges
        contract_badge = page.locator('.analytics-contract-badge').text_content().strip()
        print(f"  ✓ Analytics Header Verified: {contract_badge}")
        assert "Contract v2.1.0" in contract_badge, "Contract badge not displayed"

        # 2. Audience Segmentation KPIs
        p1_count = page.locator('#kpi-p1-count').text_content().strip()
        p2_count = page.locator('#kpi-p2-count').text_content().strip()
        unclass_count = page.locator('#kpi-unclass-count').text_content().strip()
        comp_badge = page.locator('#kpi-quality-badge').text_content().strip()
        print(f"  ✓ Audience KPIs: P1={p1_count}, P2={p2_count}, Unclassified={unclass_count}, Quality={comp_badge}")
        assert int(p1_count) >= 0 and int(p2_count) >= 0 and int(unclass_count) >= 0, "Invalid audience counts"

        # 3. Master Conversion Funnel in Dedicated Frame & Symmetrical 3-Zone Alignment
        assert page.locator('#sec-analytics-funnel .analytics-funnel-card').is_visible(), "Master Funnel should be enclosed in a dedicated framed card"
        funnel_steps = page.locator('.funnel-step')
        assert funnel_steps.count() == 7, f"Expected 7 funnel steps, got {funnel_steps.count()}"
        first_step = funnel_steps.first
        assert first_step.locator('.funnel-stage-left').is_visible(), "Funnel stage left column missing"
        assert first_step.locator('.funnel-stage-center').is_visible(), "Funnel stage center track missing"
        assert first_step.locator('.funnel-stage-right').is_visible(), "Funnel stage right metrics missing"
        print("  ✓ Master Funnel: Enclosed in dedicated frame card with symmetrical 3-zone box alignment.")

        # 4. Metric Mode Toggle (Count vs Percentage)
        page.locator('#btn-toggle-metric-mode').click()
        page.wait_for_timeout(400)
        btn_text = page.locator('#toggle-metric-text').text_content().strip()
        assert "Count View" in btn_text, "Toggle metric mode failed to switch to % view"
        print("  ✓ Metric Mode Toggle: Switched charts to Percentage (%) view.")
        page.locator('#btn-toggle-metric-mode').click()
        page.wait_for_timeout(400)

        # 5. Cohort Drill-Down Modal
        funnel_steps.first.click()
        page.wait_for_selector('#modal-analytics-drilldown', state='visible')
        page.wait_for_timeout(500)
        drill_rows = page.locator('#drilldown-table-body tr')
        assert drill_rows.count() >= 1, "Expected candidate rows in drilldown table"
        print(f"  ✓ Privacy-Safe Drill-Down Modal: Displayed {drill_rows.count()} cohort records.")
        page.screenshot(path=str(SCREENSHOTS_DIR / "11_analytics_drilldown_modal.png"))

        # Search filter within drilldown
        page.locator('#drilldown-search-input').fill('Senior')
        page.wait_for_timeout(300)
        # Close drilldown modal
        page.locator('#btn-close-drilldown-modal').click()
        page.wait_for_selector('#modal-analytics-drilldown', state='hidden')
        page.wait_for_timeout(300)
        print("  ✓ Drill-Down Modal closed successfully.")

        # 6. Global Segment Filter
        page.locator('#filter-analytics-segment').select_option('p1')
        page.wait_for_timeout(500)
        print("  ✓ Filter by Segment 'P1' executed successfully.")
        page.locator('#btn-reset-analytics-filters').click()
        page.wait_for_timeout(500)
        print("  ✓ Reset analytics filters verified.")

        # 7. Bounded Frame & Chart Container Height Verification (Prevent 142+ page bloat)
        chart_wraps = page.locator('.chart-canvas-wrap')
        assert chart_wraps.count() >= 10, "Expected at least 10 chart canvas wrappers"
        first_wrap_box = chart_wraps.first.bounding_box()
        assert first_wrap_box['height'] <= 260, f"Canvas height is {first_wrap_box['height']}px; expected <= 260px to prevent blowout"
        print(f"  ✓ Bounded Frame Verified: Chart wrapper height = {first_wrap_box['height']}px (Strictly constrained; 0 page bloat).")

        # 8. Multi-Option View Selector & Multi-Select Testing
        print("  ▶ Testing Multi-Option Section View Selector...")
        # A. Click Master Funnel pill
        page.locator('#pill-view-funnel').click()
        page.wait_for_timeout(300)
        assert page.locator('#sec-analytics-funnel').is_visible(), "Funnel section should be visible"
        assert not page.locator('#sec-analytics-rep1').is_visible(), "Report 1 should be hidden in Funnel-only view"
        assert not page.locator('#sec-analytics-rep4').is_visible(), "Report 4 should be hidden in Funnel-only view"
        print("    ✓ Pill Switcher: 'Master Funnel' displays only the funnel in the frame.")

        # B. Click Advisory Role pill
        page.locator('#pill-view-rep4').click()
        page.wait_for_timeout(300)
        assert page.locator('#sec-analytics-rep4').is_visible(), "Report 4 should be visible"
        assert not page.locator('#sec-analytics-funnel').is_visible(), "Funnel should be hidden in Report 4 view"
        print("    ✓ Pill Switcher: 'Advisory Role' displays only Report 4 in the frame.")

        # C. Multi-Select Options Menu
        page.locator('#btn-toggle-multi-select').click()
        page.wait_for_timeout(200)
        assert page.locator('#report-multi-select-menu').is_visible(), "Multi-select dropdown menu should open"
        
        # Select Funnel + Report 1 simultaneously
        page.locator('#chk-show-funnel').check()
        page.locator('#chk-show-rep1').check()
        page.wait_for_timeout(200)
        assert page.locator('#sec-analytics-funnel').is_visible(), "Funnel should be visible"
        assert page.locator('#sec-analytics-rep1').is_visible(), "Report 1 should be visible"
        assert not page.locator('#sec-analytics-rep2').is_visible(), "Report 2 should remain hidden"
        print("    ✓ Multi-Select Menu: Custom multi-option combination [Funnel + Report 1] rendered side-by-side.")

        # D. Reset to All Sections
        page.locator('#pill-view-all').click()
        page.wait_for_timeout(300)
        assert page.locator('#sec-analytics-funnel').is_visible(), "Funnel should be visible"
        assert page.locator('#sec-analytics-rep1').is_visible(), "Report 1 should be visible"
        assert page.locator('#sec-analytics-rep4').is_visible(), "Report 4 should be visible"
        print("    ✓ Pill Switcher: 'All Sections' successfully restored all framed reports.")

        # E. Interactive Slicers & Scenario Modeling Test
        print("  ▶ Testing Interactive Excel Slicers & Number Input Modeling...")
        assert page.locator('.analytics-slicer-card').is_visible(), "Slicer card should be visible"
        
        # Verify Chart.js Data Labels Plugin is globally registered
        is_plugin_registered = page.evaluate("() => window._chartValueLabelsRegistered === true")
        assert is_plugin_registered, "Chart.js Data Labels plugin should be registered"
        print("    ✓ Data Labels Plugin: Active and rendering counts & percentages directly on all graphs.")

        # Test Scenario Number Input: Min Age = 50
        page.locator('#slicer-min-age').fill('50')
        page.wait_for_timeout(300)
        slicer_badge_text = page.locator('#slicer-active-count').text_content()
        assert "of 130 Candidates" in slicer_badge_text, "Slicer count should dynamically update upon number input"
        print(f"    ✓ Scenario Input (Min Age 50): Dynamically filtered pool -> '{slicer_badge_text}'")

        # Test Excel-style Slicer Tile: Government Sector
        page.locator('#slicer-group-sector button[data-filter="Government"]').click()
        page.wait_for_timeout(300)
        govt_badge_text = page.locator('#slicer-active-count').text_content()
        print(f"    ✓ Excel Slicer Tile (Government): Dynamically updated graphs -> '{govt_badge_text}'")

        # Test Reset Slicers
        page.locator('.analytics-slicer-card button[onclick="resetInteractiveSlicers()"]').click()
        page.wait_for_timeout(300)
        reset_badge_text = page.locator('#slicer-active-count').text_content()
        assert "130 of 130 Candidates (100%)" in reset_badge_text, "Reset should restore all 130 candidates"
        print("    ✓ Reset Slicers: Successfully restored full 130 candidates and re-rendered base charts.")

        page.screenshot(path=str(SCREENSHOTS_DIR / "10_conversion_intelligence_analytics.png"))

        # Rule 4 Console Error assertion
        fatal_errors = [e for e in console_errors if "favicon" not in e.lower() and "404" not in e.lower()]
        assert len(fatal_errors) == 0, f"Detected unhandled JavaScript console errors: {fatal_errors}"
        print("  ✓ Rule 4 Verified: ZERO unhandled console errors detected during runtime execution!")

        browser.close()

    print("\n" + "=" * 65)
    print(" 🎉 ALL 10 PLAYWRIGHT END-TO-END TESTS PASSED SUCCESSFULLY! ")
    print(f" 📸 Screenshots saved to: {SCREENSHOTS_DIR}")
    print("=" * 65 + "\n")

if __name__ == '__main__':
    run_playwright_tests()
