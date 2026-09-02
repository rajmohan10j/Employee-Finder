import os
import sys
import webbrowser
import threading
import time
from pathlib import Path

# Add current directory to path
current_dir = Path(__file__).parent.resolve()
sys.path.insert(0, str(current_dir))

from app import app, get_local_ips

def open_browser():
    time.sleep(1.2)
    webbrowser.open("http://127.0.0.1:5000")

if __name__ == '__main__':
    port = 5000
    local_ips = get_local_ips()
    
    print("\n" + "=" * 65)
    print(" 🌟 CANDIDATE TRACKER WEB & MOBILE APP (WINDOWS & ANDROID)")
    print("=" * 65)
    print(f" 💻 Desktop Access URL : http://127.0.0.1:{port}")
    for ip in local_ips:
        print(f" 📱 Android Mobile URL : http://{ip}:{port}")
    print("=" * 65)
    print(" 💡 TIP: Connect your Android phone to the same Wi-Fi network")
    print("    and visit the mobile URL, or scan the QR code in the app!")
    print("=" * 65 + "\n")

    # Launch browser in a background thread
    threading.Thread(target=open_browser, daemon=True).start()

    # Start Flask Server
    app.run(host='0.0.0.0', port=port, debug=False)
