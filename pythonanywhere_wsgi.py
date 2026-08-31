# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# PythonAnywhere WSGI Configuration for Candidate Tracker
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Instructions:
# 1. In PythonAnywhere Web tab, find "WSGI configuration file" and click it.
# 2. Replace its entire contents with the code below (replace 'yourusername' with your username).
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import sys
import os
from pathlib import Path

# Replace with your actual PythonAnywhere username
username = 'rajmohan'
project_home = f'/home/{username}/Employee-Finder'

if project_home not in sys.path:
    sys.path.insert(0, project_home)

app_dir = os.path.join(project_home, 'candidate_app')
if app_dir not in sys.path:
    sys.path.insert(1, app_dir)

# Set optional environment variables
os.environ['EXCEL_PATH'] = os.path.join(project_home, 'candidates_tracker.xlsx')
os.environ['FLASK_ENV'] = 'production'

# Import Flask app
from app import app as application
