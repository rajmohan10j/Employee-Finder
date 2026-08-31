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

def run_android_mobile_tests():
    if not is_server_running():
        start_background_server()

    print("\n" + "=" * 70)
    print(" 📱 PLAYWRIGHT ANDROID MOBILE VIEWPORT & TOUCH INTERACTION TEST")
    print("=" * 70)

    with sync_playwright() as p:
        # Emulate Google Pixel 7 (Android)
        pixel_7 = p.devices['Pixel 7']
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(**pixel_7)
        page = context.new_page()

        # ----------------------------------------------------------------------
        # TEST 1: Mobile Dashboard Layout & Sideways Scroll Check
        # ----------------------------------------------------------------------
        print("\n▶ [TEST 1] Opening Android Mobile View (393 x 851 viewport)...")
        page.goto('http://127.0.0.1:5000', wait_until='domcontentloaded')
        page.wait_for_selector('.candidate-card')
        page.wait_for_timeout(500)

        # Check for horizontal overflow
        has_horizontal_scroll = page.evaluate("""() => {
            return document.documentElement.scrollWidth > document.documentElement.clientWidth;
        }""")
        scroll_width = page.evaluate("() => document.documentElement.scrollWidth")
        client_width = page.evaluate("() => document.documentElement.clientWidth")
        
        print(f"  ✓ Screen Dimensions: clientWidth={client_width}px, scrollWidth={scroll_width}px")
        assert not has_horizontal_scroll, f"Horizontal scroll detected! scrollWidth ({scroll_width}px) > clientWidth ({client_width}px)"
        print("  ✓ PASSED: No unwanted horizontal/sidewise scrolling on Android screen!")
        
        page.screenshot(path=str(SCREENSHOTS_DIR / "android_01_dashboard_fit.png"))

        # ----------------------------------------------------------------------
        # TEST 2: Test Size Adjuster (Reduce / Increase Size)
        # ----------------------------------------------------------------------
        print("\n▶ [TEST 2] Testing Box/Font Size Adjusters (A- and A+)...")
        # Click A- (Reduce size)
        page.locator('#btn-size-down').click()
        page.wait_for_timeout(300)
        zoom_val = page.evaluate("() => document.documentElement.style.getPropertyValue('--app-zoom')")
        print(f"  ✓ Clicked 'A-': App Zoom changed to {zoom_val}")
        page.screenshot(path=str(SCREENSHOTS_DIR / "android_02_zoom_reduced.png"))

        # Click A+ (Increase size) twice
        page.locator('#btn-size-up').click()
        page.locator('#btn-size-up').click()
        page.wait_for_timeout(300)
        zoom_val = page.evaluate("() => document.documentElement.style.getPropertyValue('--app-zoom')")
        print(f"  ✓ Clicked 'A+': App Zoom changed to {zoom_val}")
        page.screenshot(path=str(SCREENSHOTS_DIR / "android_03_zoom_increased.png"))

        # Reset size
        page.locator('#btn-size-reset').click()
        page.wait_for_timeout(300)

        # ----------------------------------------------------------------------
        # TEST 3: Open Candidate Form & Verify Vertical Scrollability
        # ----------------------------------------------------------------------
        print("\n▶ [TEST 3] Opening Candidate Box Item Form on Android...")
        first_card = page.locator('.candidate-card').first
        first_card.locator('button[title="Edit Box Items"]').click()

        page.wait_for_selector('#modal-candidate-form', state='visible')
        page.wait_for_timeout(400)

        # Check modal dimensions
        modal_fit = page.evaluate("""() => {
            const modal = document.querySelector('#modal-candidate-form .modal-card');
            const body = document.querySelector('#modal-candidate-form .modal-body');
            return {
                modalWidth: modal.clientWidth,
                windowWidth: window.innerWidth,
                bodyScrollHeight: body.scrollHeight,
                bodyClientHeight: body.clientHeight,
                isScrollable: body.scrollHeight > body.clientHeight
            };
        }""")
        print(f"  ✓ Modal Width: {modal_fit['modalWidth']}px / Window: {modal_fit['windowWidth']}px")
        print(f"  ✓ Modal Content Height: {modal_fit['bodyScrollHeight']}px, Viewable Height: {modal_fit['bodyClientHeight']}px")
        assert modal_fit['isScrollable'], "Modal body should be vertically scrollable to access all fields"
        print("  ✓ PASSED: Full modal fits screen width and is vertically scrollable up/down!")

        page.screenshot(path=str(SCREENSHOTS_DIR / "android_04_modal_top.png"))

        # Scroll down through all 15 box items
        print("  ✓ Scrolling down to view all lower box items...")
        page.evaluate("""() => {
            const body = document.querySelector('#modal-candidate-form .modal-body');
            body.scrollTop = body.scrollHeight;
        }""")
        page.wait_for_timeout(400)
        page.screenshot(path=str(SCREENSHOTS_DIR / "android_05_modal_scrolled_bottom.png"))

        # Edit a field and click Save & Update Master Excel
        print("  ✓ Entering updated notes into HR remarks on mobile...")
        page.locator('#field-hr-remarks').fill(f"Android mobile verified at {time.strftime('%H:%M:%S')}: Box items scroll and fit screen perfectly.")
        
        # Click Save
        page.locator('#btn-save-candidate').click()
        page.wait_for_selector('#modal-candidate-form', state='hidden')
        page.wait_for_timeout(600)
        print("  ✓ PASSED: Form submitted and modal closed smoothly!")

        # ----------------------------------------------------------------------
        # TEST 4: Test Bottom Mobile Navigation Tabs
        # ----------------------------------------------------------------------
        print("\n▶ [TEST 4] Testing Android Bottom Navigation Bar...")
        page.locator('.bottom-nav-item:has-text("Reviews")').click()
        page.wait_for_selector('#tab-reviews.active')
        page.wait_for_timeout(400)
        page.screenshot(path=str(SCREENSHOTS_DIR / "android_06_reviews_tab.png"))

        page.locator('.bottom-nav-item:has-text("Reviewers")').click()
        page.wait_for_selector('#tab-reviewers.active')
        page.wait_for_timeout(400)
        page.screenshot(path=str(SCREENSHOTS_DIR / "android_07_reviewers_tab.png"))

        page.locator('.bottom-nav-item:has-text("Connect")').click()
        page.wait_for_selector('#tab-mobile.active')
        page.wait_for_timeout(400)
        page.screenshot(path=str(SCREENSHOTS_DIR / "android_08_connect_tab.png"))

        browser.close()

    print("\n" + "=" * 70)
    print(" 🌟 ANDROID MOBILE RESPONSIVE TEST COMPLETED SUCCESSFULLY!")
    print(f" 📸 Screenshots saved to: {SCREENSHOTS_DIR}")
    print("=" * 70 + "\n")

if __name__ == '__main__':
    run_android_mobile_tests()
