import os
import sys
import json
import uuid
import socket
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file, send_from_directory

from excel_manager import ExcelManager, TRACKER_HEADERS

app = Flask(__name__, static_folder='static', template_folder='templates')

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
    return response

BASE_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = BASE_DIR.parent if BASE_DIR.name == "candidate_app" else BASE_DIR

# Determine Excel Path dynamically (Environment variable -> Project root -> Absolute Windows fallback)
env_excel = os.environ.get("EXCEL_PATH")
if env_excel and Path(env_excel).exists():
    EXCEL_PATH = Path(env_excel)
elif (PROJECT_ROOT / "candidates_tracker.xlsx").exists():
    EXCEL_PATH = PROJECT_ROOT / "candidates_tracker.xlsx"
elif Path(r"C:\Users\Raj\Projects\Employee-Finder\candidates_tracker.xlsx").exists():
    EXCEL_PATH = Path(r"C:\Users\Raj\Projects\Employee-Finder\candidates_tracker.xlsx")
else:
    EXCEL_PATH = PROJECT_ROOT / "candidates_tracker.xlsx"

DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

REVIEWERS_FILE = DATA_DIR / "reviewers.json"
PENDING_REVIEWS_FILE = DATA_DIR / "pending_reviews.json"
RESUME_DIRS = [
    PROJECT_ROOT / "resumes",
    DATA_DIR / "resumes",
    Path(r"C:\Users\Raj\Projects\candidate_data\resumes"),
    Path(r"C:\Users\Raj\Projects\Employee-Finder\resumes")
]

excel_mgr = ExcelManager(str(EXCEL_PATH))
# Start background scheduler for Daily (1PM/6PM), Weekly (Sat 6PM), and Monthly (1st 9AM) backups
excel_mgr.backup_mgr.start_scheduler_daemon(interval_seconds=60)

# Helper to load JSON
def load_json(filepath, default_val):
    if not filepath.exists():
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(default_val, f, indent=2)
        return default_val
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return default_val

def save_json(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def get_local_ips():
    ips = []
    # Probe active gateway interface
    for probe_target in [('8.8.8.8', 80), ('1.1.1.1', 80), ('192.168.1.1', 80), ('10.0.0.1', 80)]:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(0.5)
            s.connect(probe_target)
            local_ip = s.getsockname()[0]
            s.close()
            if local_ip and not local_ip.startswith('127.') and not local_ip.startswith('169.254.') and local_ip not in ips:
                ips.append(local_ip)
                break
        except Exception:
            pass

    # Method 2: Hostname inspection
    try:
        hostname = socket.gethostname()
        for ip in socket.gethostbyname_ex(hostname)[2]:
            if not ip.startswith('127.') and not ip.startswith('169.254.') and ip not in ips:
                ips.append(ip)
    except Exception:
        pass

    # Method 3: Socket address info
    try:
        for item in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            ip = item[4][0]
            if not ip.startswith('127.') and not ip.startswith('169.254.') and ip not in ips:
                ips.append(ip)
    except Exception:
        pass

    if not ips:
        ips.append('127.0.0.1')
    return ips

# Initialize defaults if not present
if not REVIEWERS_FILE.exists():
    default_reviewers = [
        {"id": str(uuid.uuid4())[:8], "name": "Raj (Admin)", "phone": "+91 98765 43210", "email": "raj.admin@example.com", "role": "Lead Reviewer", "status": "Active"},
        {"id": str(uuid.uuid4())[:8], "name": "HR Lead / Manager", "phone": "+91 91234 56789", "email": "hr.manager@example.com", "role": "Hiring Lead", "status": "Active"}
    ]
    save_json(REVIEWERS_FILE, default_reviewers)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/version', methods=['GET'])
def get_version():
    version_file = BASE_DIR.parent / "VERSION.json"
    if not version_file.exists():
        version_file = BASE_DIR.parent / "Prod" / "VERSION.json"
    if version_file.exists():
        try:
            with open(version_file, 'r', encoding='utf-8') as f:
                return jsonify(json.load(f))
        except Exception:
            pass
    return jsonify({
        "project": "Employee-Finder Candidate Tracker",
        "version": "1.2.0-prod",
        "environment": "production",
        "status": "stable",
        "release_date": "2026-08-31"
    })

@app.route('/api/stats', methods=['GET'])
def get_stats():
    candidates = excel_mgr.get_all_candidates()
    total = len(candidates)
    called = sum(1 for c in candidates if "yes" in c.get("HR Called", "").lower())
    closed_count = sum(1 for c in candidates if "not interested" in c.get("HR Called", "").lower() or "not interested" in c.get("Open To Work / Active", "").lower() or "closed" in c.get("HR Called", "").lower() or "closed" in c.get("Open To Work / Active", "").lower())
    pending_call = total - called - sum(1 for c in candidates if ("busy" in c.get("HR Called", "").lower() or "not reachable" in c.get("HR Called", "").lower()) and "yes" not in c.get("HR Called", "").lower())
    if pending_call < 0:
        pending_call = 0
    follow_ups = sum(1 for c in candidates if c.get("Follow-up Date") and c.get("Follow-up Date").strip() != "")
    
    pending_reviews = [r for r in load_json(PENDING_REVIEWS_FILE, []) if r.get("status") == "pending"]
    escalated = sum(1 for c in candidates if c.get("Escalation Level / Person") and c.get("Escalation Level / Person").strip() not in ["", "None", "None / No Escalation", "No Escalation"])
    
    portals = {}
    for c in candidates:
        p = c.get("Portal Source", "Unknown") or "Unknown"
        portals[p] = portals.get(p, 0) + 1

    return jsonify({
        "success": True,
        "total": total,
        "total_candidates": total,
        "called": called,
        "called_count": called,
        "pending_call": pending_call,
        "pending_call_count": pending_call,
        "closed_count": closed_count,
        "follow_ups": follow_ups,
        "follow_ups_count": follow_ups,
        "pending_reviews": len(pending_reviews),
        "pending_reviews_count": len(pending_reviews),
        "escalated_count": escalated,
        "portals": portals,
        "portals_breakdown": portals
    })

@app.route('/api/candidates/<int:row_id>/quick_close', methods=['POST'])
def quick_close_candidate(row_id):
    try:
        req_data = request.get_json(silent=True) or {}
        reason = req_data.get('reason', 'Not interested / Closed via 1-click')
        today_str = datetime.now().strftime('%Y-%m-%d')
        
        updates = {
            'HR Called': 'Closed - Not Interested',
            'Open To Work / Active': 'Closed - Not Interested',
            'Date': today_str,
            'HR Remarks': reason
        }
        updated = excel_mgr.update_candidate(row_id, updates)
        return jsonify({"success": True, "candidate": updated, "message": "Candidate marked as Closed / Not Interested."})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/candidates', methods=['GET'])
def get_candidates():
    query = request.args.get('query', '')
    status = request.args.get('status', 'All')
    portal = request.args.get('portal', 'All')
    escalation = request.args.get('escalation', 'All')
    candidates = excel_mgr.get_all_candidates(query=query, filter_status=status, filter_portal=portal, filter_escalation=escalation)
    return jsonify({"success": True, "count": len(candidates), "candidates": candidates})

@app.route('/api/candidates/<int:row_id>', methods=['GET'])
def get_candidate(row_id):
    candidate = excel_mgr.get_candidate_by_id(row_id)
    if not candidate:
        return jsonify({"success": False, "error": "Candidate not found"}), 404
    return jsonify({"success": True, "candidate": candidate})

@app.route('/api/candidates', methods=['POST'])
def add_candidate():
    data = request.json or {}
    try:
        new_cand = excel_mgr.add_candidate(data)
        return jsonify({"success": True, "candidate": new_cand})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/candidates/<int:row_id>', methods=['PUT'])
def update_candidate(row_id):
    data = request.json or {}
    requires_review = request.args.get('stage_for_review', 'false').lower() == 'true'
    
    if requires_review:
        # Submit to staging for review workflow
        current = excel_mgr.get_candidate_by_id(row_id)
        if not current:
            return jsonify({"success": False, "error": "Candidate not found"}), 404
            
        pending_list = load_json(PENDING_REVIEWS_FILE, [])
        review_id = str(uuid.uuid4())[:8]
        
        # Calculate field diffs
        diffs = {}
        for k in TRACKER_HEADERS:
            old_v = str(current.get(k, ""))
            new_v = str(data.get(k, ""))
            if old_v != new_v:
                diffs[k] = {"old": old_v, "new": new_v}

        if not diffs:
            return jsonify({"success": True, "message": "No changes detected", "staged": False})

        review_item = {
            "id": review_id,
            "row_id": row_id,
            "candidate_name": current.get("Candidate Name", "Unknown"),
            "submitted_by": data.get("_submitted_by", "App User"),
            "reviewer_assigned": data.get("_reviewer_assigned", "Unassigned"),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "pending",
            "diffs": diffs,
            "new_data": data
        }
        pending_list.append(review_item)
        save_json(PENDING_REVIEWS_FILE, pending_list)
        return jsonify({"success": True, "message": "Changes submitted for review and approval", "review_id": review_id, "staged": True})
    else:
        # Direct commit to Excel
        try:
            updated = excel_mgr.update_candidate(row_id, data)
            return jsonify({"success": True, "candidate": updated, "staged": False})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/candidates/<int:row_id>', methods=['DELETE'])
def delete_candidate(row_id):
    try:
        excel_mgr.delete_candidate(row_id)
        return jsonify({"success": True, "message": "Candidate deleted"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Reviewers Management
@app.route('/api/reviewers', methods=['GET', 'POST'])
def handle_reviewers():
    if request.method == 'GET':
        reviewers = load_json(REVIEWERS_FILE, [])
        return jsonify({"success": True, "reviewers": reviewers})
    else:
        data = request.json or {}
        reviewers = load_json(REVIEWERS_FILE, [])
        new_rev = {
            "id": str(uuid.uuid4())[:8],
            "name": data.get("name", "").strip(),
            "phone": data.get("phone", "").strip(),
            "email": data.get("email", "").strip(),
            "role": data.get("role", "Reviewer").strip(),
            "status": "Active"
        }
        if not new_rev["name"]:
            return jsonify({"success": False, "error": "Reviewer name is required"}), 400
        reviewers.append(new_rev)
        save_json(REVIEWERS_FILE, reviewers)
        return jsonify({"success": True, "reviewer": new_rev})

@app.route('/api/reviewers/<rev_id>', methods=['DELETE'])
def delete_reviewer(rev_id):
    reviewers = load_json(REVIEWERS_FILE, [])
    reviewers = [r for r in reviewers if r.get("id") != rev_id]
    save_json(REVIEWERS_FILE, reviewers)
    return jsonify({"success": True, "message": "Reviewer removed"})

# Pending Reviews Workflow
@app.route('/api/pending_reviews', methods=['GET'])
def get_pending_reviews():
    reviews = load_json(PENDING_REVIEWS_FILE, [])
    return jsonify({"success": True, "reviews": reviews})

@app.route('/api/commit_review', methods=['POST'])
def commit_review():
    data = request.json or {}
    review_id = data.get("review_id")
    action = data.get("action") # 'approve' or 'reject'
    reviewed_by = data.get("reviewed_by", "Reviewer")
    
    reviews = load_json(PENDING_REVIEWS_FILE, [])
    target = None
    for r in reviews:
        if r.get("id") == review_id and r.get("status") == "pending":
            target = r
            break
            
    if not target:
        return jsonify({"success": False, "error": "Pending review not found"}), 404

    if action == "approve":
        try:
            excel_mgr.update_candidate(target["row_id"], target["new_data"])
            target["status"] = "committed"
            target["reviewed_by"] = reviewed_by
            target["reviewed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            save_json(PENDING_REVIEWS_FILE, reviews)
            return jsonify({"success": True, "message": "Changes approved and committed to Excel master database!"})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
    elif action == "reject":
        target["status"] = "rejected"
        target["reviewed_by"] = reviewed_by
        target["reviewed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        target["reject_reason"] = data.get("reason", "Rejected by reviewer")
        save_json(PENDING_REVIEWS_FILE, reviews)
        return jsonify({"success": True, "message": "Changes rejected"})
    else:
        return jsonify({"success": False, "error": "Invalid action"}), 400

# Network and Android Connection Info
@app.route('/api/network_info', methods=['GET'])
def network_info():
    ips = get_local_ips()
    port = 5000
    urls = [f"http://{ip}:{port}" for ip in ips]
    return jsonify({
        "success": True,
        "local_ips": ips,
        "port": port,
        "primary_url": urls[0] if urls else f"http://127.0.0.1:{port}",
        "all_urls": urls
    })

# Resume viewer / download
@app.route('/api/resumes/<path:filename>')
def get_resume(filename):
    for r_dir in RESUME_DIRS:
        if r_dir.exists():
            file_path = r_dir / filename
            if file_path.exists() and file_path.is_file():
                return send_from_directory(str(r_dir), filename)
    return jsonify({"success": False, "error": "Resume file not found"}), 404

# Import Excel File
@app.route('/api/import', methods=['POST'])
def import_file():
    mode = request.form.get('mode', 'append') if request.form else 'append'
    if request.is_json and request.json:
        mode = request.json.get('mode', 'append')
        file_path = request.json.get('file_path')
        if file_path and os.path.exists(file_path):
            try:
                res = excel_mgr.import_excel_file(file_path, mode=mode)
                return jsonify({"success": True, "imported_count": res["imported_count"], "total_count": res["total_count"]})
            except Exception as e:
                return jsonify({"success": False, "error": str(e)}), 500

    if 'file' not in request.files:
        return jsonify({"success": False, "error": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"success": False, "error": "No file selected"}), 400

    if not (file.filename.endswith('.xlsx') or file.filename.endswith('.xls')):
        return jsonify({"success": False, "error": "Only .xlsx and .xls files are supported"}), 400

    try:
        res = excel_mgr.import_excel_file(file.stream, mode=mode)
        return jsonify({
            "success": True,
            "message": f"Successfully imported {res['imported_count']} candidates!",
            "imported_count": res["imported_count"],
            "total_count": res["total_count"]
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Backup & Version History Endpoints
@app.route('/api/backups', methods=['GET'])
def get_backups():
    try:
        summary = excel_mgr.backup_mgr.get_backup_summary()
        return jsonify({"success": True, "data": summary})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/backups/create', methods=['POST'])
def trigger_backup():
    data = request.json or {}
    tier = data.get('tier', 'manual')
    prefix = data.get('prefix', 'manual_checkpoint')
    try:
        res = excel_mgr.backup_mgr.create_backup(tier=tier, prefix=prefix, force=True)
        return jsonify({"success": True, "result": res})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/backups/restore', methods=['POST'])
def restore_backup_api():
    data = request.json or {}
    filepath = data.get('filepath')
    if not filepath:
        return jsonify({"success": False, "error": "No backup filepath provided"}), 400
    try:
        res = excel_mgr.backup_mgr.restore_backup(filepath)
        if res.get("status") == "success":
            return jsonify({"success": True, "message": res.get("message")})
        else:
            return jsonify({"success": False, "error": res.get("message")}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Export Excel
@app.route('/api/export', methods=['GET'])
def export_file():
    if EXCEL_PATH.exists():
        return send_file(str(EXCEL_PATH), as_attachment=True, download_name=f"candidates_tracker_export_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx")
    return jsonify({"success": False, "error": "Master Excel file missing"}), 404

if __name__ == '__main__':
    port = 5000
    print("\n=======================================================")
    print(" 🚀 CANDIDATES TRACKER WEB & MOBILE SERVER STARTING")
    print("=======================================================")
    for url in [f"http://{ip}:{port}" for ip in get_local_ips()]:
        print(f" 📱 Access from Android / Browser: {url}")
    print("=======================================================\n")
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
