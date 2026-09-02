import os
import sys
from pathlib import Path

# Add candidate_app and root directory to python path
ROOT_DIR = Path(__file__).parent.resolve()
APP_DIR = ROOT_DIR / "candidate_app"

if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(1, str(ROOT_DIR))

# Import Flask app instance
from app import app, excel_mgr

# WSGI Application entrypoint for Gunicorn, Waitress, PythonAnywhere
application = app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
