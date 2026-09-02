import os
import sys
import json
import uuid
import socket
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file, send_from_directory

from excel_manager import (
    ExcelManager, TRACKER_HEADERS,
    is_candidate_called, is_candidate_pending, is_candidate_closed,
    is_candidate_busy, is_candidate_not_reachable, is_candidate_followup,
    is_candidate_assigned
)

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
    version_file = BASE_DIR.parent / "Prod" / "VERSION.json"
    if not version_file.exists():
        version_file = BASE_DIR / "VERSION.json"
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
    called = sum(1 for c in candidates if is_candidate_called(c))
    pending_call = sum(1 for c in candidates if is_candidate_pending(c))
    closed_count = sum(1 for c in candidates if is_candidate_closed(c))
    follow_ups = sum(1 for c in candidates if is_candidate_followup(c))
    
    pending_reviews = [r for r in load_json(PENDING_REVIEWS_FILE, []) if r.get("status") == "pending"]
    escalated = 0
    escalation_breakdown = {}
    for c in candidates:
        if is_candidate_assigned(c):
            escalated += 1
            lvl = (c.get("Escalation Level / Person") or "").strip()
            escalation_breakdown[lvl] = escalation_breakdown.get(lvl, 0) + 1
    
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
        "escalation_breakdown": escalation_breakdown,
        "portals": portals,
        "portals_breakdown": portals
    })


def _parse_experience_years(exp_str):
    """Parse experience strings like '4y 8m', '31y 3m', '30+' to numeric years."""
    import re
    if not exp_str or exp_str.strip().lower() in ['', 'extracted from pdf', 'n/a', 'none']:
        return None
    s = exp_str.strip().lower().replace('+', '')
    years = 0
    ym = re.search(r'(\d+)\s*y', s)
    mm = re.search(r'(\d+)\s*m', s)
    if ym:
        years += int(ym.group(1))
    if mm:
        years += int(mm.group(1)) / 12.0
    if not ym and not mm:
        try:
            years = float(s)
        except Exception:
            return None
    return round(years, 1)


def _exp_band(years):
    if years is None: return 'Unknown'
    if years < 5: return '0–5 yrs'
    if years < 10: return '5–10 yrs'
    if years < 15: return '10–15 yrs'
    if years < 20: return '15–20 yrs'
    return '20+ yrs'


def _parse_age(c):
    """Returns (age_int or None, is_explicit_bool)."""
    raw_age = (c.get('Age') or '').strip()
    if raw_age:
        try:
            val = int(float(raw_age))
            if 18 <= val <= 100:
                return val, True
        except Exception:
            pass
    # Approximate from Total Experience if available
    exp_years = _parse_experience_years(c.get('Total Experience', ''))
    if exp_years is not None and exp_years >= 1:
        approx_age = int(round(exp_years + 23))
        return approx_age, False
    return None, False


def _age_band(age):
    if age is None: return 'Unknown'
    if age < 45: return '< 45 yrs'
    if age <= 50: return '45–50 yrs'
    if age <= 55: return '51–55 yrs'
    if age <= 60: return '56–60 yrs'
    return '60+ yrs'


def _get_sector(c):
    """Returns (sector_string, is_explicit_bool)."""
    raw_sec = (c.get('Employment Sector') or '').strip()
    if raw_sec:
        return raw_sec, True
    combined = f"{c.get('Domain / Industry', '')} {c.get('Current Position / Role', '')} {c.get('HR Remarks', '')}".lower()
    if any(k in combined for k in ['government', 'central govt', 'state govt', 'govt']):
        return 'Government', False
    if any(k in combined for k in ['public sector', 'psu', 'ordnance', 'railway', 'lic', 'hal', 'bel', 'bhel', 'ongc', 'iocl', 'ntpc', 'steel authority']):
        return 'Public Sector / PSU', False
    if any(k in combined for k in ['defence', 'army', 'navy', 'air force', 'military', 'armed forces']):
        return 'Defence / Armed Forces', False
    if any(k in combined for k in ['bank', 'insurance', 'financial services']):
        return 'Banking / Insurance', False
    if any(k in combined for k in ['it ', 'software', 'technology', 'telecom', 'private']):
        return 'Private Sector', False
    return 'Unknown', False


def _get_retirement_status(c):
    """Returns (status_string, is_explicit_bool)."""
    raw_ret = (c.get('Retirement Status') or '').strip()
    if raw_ret:
        return raw_ret, True
    combined = f"{c.get('Current Position / Role', '')} {c.get('HR Remarks', '')} {c.get('Domain / Industry', '')}".lower()
    if any(k in combined for k in ['retired', 'ret.', 'vrs', 'superannuated', 'ex-serviceman', 'ex serviceman']):
        return 'Retired', False
    return 'Unknown', False


def _classify_candidate_audience(c):
    """
    Unified Audience Segmentation:
    - P1 Preferred (Confirmed): Age > 50 (51+), Sector == Government, Retirement Status == Retired (explicit).
    - P1 Candidate (Inferred): Meets criteria via profile/experience heuristics; requires explicit confirmation.
    - P2 Expansion: Age >= 45 or Exp >= 15 yrs, or Sectors: Govt, PSU, Defence, Banking.
    - Unclassified: Others or data incomplete.
    """
    age, age_explicit = _parse_age(c)
    sector, sector_explicit = _get_sector(c)
    retirement, ret_explicit = _get_retirement_status(c)
    exp_years = _parse_experience_years(c.get('Total Experience', ''))

    is_govt = sector.lower() in ['government', 'central govt', 'state govt']
    is_retired = 'retired' in retirement.lower()
    is_age_p1 = (age is not None and age > 50)

    if is_age_p1 and is_govt and is_retired:
        if age_explicit and sector_explicit and ret_explicit:
            return 'P1 - Preferred', 'P1: Confirmed (Age 51+, Govt Sector, Retired)', True
        else:
            return 'P1 - Candidate (Inferred)', 'P1: Inferred from profile heuristics (Needs explicit confirmation)', False

    is_p2_age = (age is not None and age >= 45) or (exp_years is not None and exp_years >= 15)
    is_p2_sector = is_govt or any(k in sector.lower() for k in ['public sector', 'psu', 'defence', 'banking', 'insurance'])
    if is_p2_age or is_p2_sector:
        return 'P2 - Expansion', 'P2: Senior / Public Sector / Banking Expansion', False

    return 'Unclassified', 'Unclassified / Incomplete Data', False


def _domain_key(dom_str):
    """Extract first major category from multi-part domain strings."""
    if not dom_str: return 'Unknown'
    import re
    parts = re.split(r'[/&|]', dom_str)
    return parts[0].strip() or 'Unknown'


def _city_key(loc_str):
    if not loc_str: return 'Unknown'
    return loc_str.split(',')[0].strip() or 'Unknown'


def _get_call_response_detailed(c):
    """Returns (response_string, provenance: 'explicit' | 'inferred' | 'pending')."""
    resp = (c.get('Call Response') or '').strip()
    if resp:
        return resp, 'explicit'
    hrc = (c.get('HR Called') or '').strip().lower()
    if 'not interested' in hrc or 'closed' in hrc:
        return 'Negative', 'inferred'
    if 'yes' in hrc and 'not' not in hrc:
        return 'Positive', 'inferred'
    if 'busy' in hrc or 'call later' in hrc or 'call back' in hrc:
        return 'No Response', 'inferred'
    if 'not reachable' in hrc or 'rnr' in hrc or 'not connected' in hrc:
        return 'No Response', 'inferred'
    return 'Pending', 'pending'


def _get_call_response(c):
    resp, _ = _get_call_response_detailed(c)
    return resp


@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    """
    Unified Conversion Intelligence Analytics & Reporting Endpoint.
    Combines core conversion funnel analysis with P1/P2 audience segmentation,
    explicit vs inferred provenance tracking, and data quality metrics.
    """
    all_candidates = excel_mgr.get_all_candidates()

    # Query filters
    filter_segment = (request.args.get('segment') or 'all').strip().lower()
    filter_portal = (request.args.get('portal') or 'all').strip()
    filter_provenance = (request.args.get('provenance') or 'all').strip().lower()

    # Pre-classify and augment all candidates
    augmented = []
    explicit_age_count = 0
    explicit_sector_count = 0
    explicit_ret_count = 0
    explicit_resp_count = 0
    inferred_resp_count = 0

    for c in all_candidates:
        age_val, age_exp = _parse_age(c)
        sec_val, sec_exp = _get_sector(c)
        ret_val, ret_exp = _get_retirement_status(c)
        seg_label, seg_reason, seg_is_confirmed = _classify_candidate_audience(c)
        c_resp, c_prov = _get_call_response_detailed(c)
        exp_years = _parse_experience_years(c.get('Total Experience', ''))
        exp_band_val = _exp_band(exp_years)
        age_band_val = _age_band(age_val)
        dom_val = _domain_key(c.get('Domain / Industry', ''))
        city_val = _city_key(c.get('Location', ''))
        portal_val = (c.get('Portal Source', '') or 'Unknown').strip() or 'Unknown'

        if age_exp: explicit_age_count += 1
        if sec_exp: explicit_sector_count += 1
        if ret_exp: explicit_ret_count += 1
        if c_prov == 'explicit': explicit_resp_count += 1
        elif c_prov == 'inferred': inferred_resp_count += 1

        item = {
            'candidate': c,
            'id': c.get('_row_id'),
            'name': c.get('Candidate Name', 'Unknown'),
            'role': c.get('Current Position / Role', ''),
            'domain': dom_val,
            'city': city_val,
            'portal': portal_val,
            'exp_years': exp_years,
            'exp_band': exp_band_val,
            'age': age_val,
            'age_band': age_band_val,
            'sector': sec_val,
            'retirement': ret_val,
            'segment': seg_label,
            'segment_reason': seg_reason,
            'is_confirmed_p1': seg_is_confirmed,
            'call_response': c_resp,
            'call_provenance': c_prov,
            'interview_agreed': (c.get('Interview / Meeting Agreed') or '').strip() or 'Not Discussed',
            'advisory_interest': (c.get('Advisory Role Interest') or '').strip() or 'Not Discussed'
        }
        augmented.append(item)

    total_pool_size = len(all_candidates)

    # Segment counts across entire database
    overall_segment_counts = {
        'P1 - Preferred (Confirmed)': sum(1 for a in augmented if a['is_confirmed_p1']),
        'P1 - Candidate (Inferred)': sum(1 for a in augmented if a['segment'] == 'P1 - Candidate (Inferred)'),
        'P2 - Expansion': sum(1 for a in augmented if a['segment'] == 'P2 - Expansion'),
        'Unclassified': sum(1 for a in augmented if a['segment'] == 'Unclassified')
    }

    # Apply active filters to subset
    filtered = []
    for a in augmented:
        if filter_segment == 'p1':
            if not (a['is_confirmed_p1'] or a['segment'] == 'P1 - Candidate (Inferred)'):
                continue
        elif filter_segment == 'p1_confirmed':
            if not a['is_confirmed_p1']:
                continue
        elif filter_segment == 'p2':
            if a['segment'] != 'P2 - Expansion':
                continue
        elif filter_segment == 'unclassified':
            if a['segment'] != 'Unclassified':
                continue

        if filter_portal != 'all' and filter_portal != 'All':
            if a['portal'].lower() != filter_portal.lower():
                continue

        if filter_provenance == 'explicit_only':
            if a['call_provenance'] != 'explicit':
                continue

        filtered.append(a)

    band_order = ['0–5 yrs', '5–10 yrs', '10–15 yrs', '15–20 yrs', '20+ yrs', 'Unknown']
    age_band_order = ['< 45 yrs', '45–50 yrs', '51–55 yrs', '56–60 yrs', '60+ yrs', 'Unknown']

    # ---- REPORT 1: Audience & Profile Coverage ----
    exp_distribution = {b: 0 for b in band_order}
    age_distribution = {b: 0 for b in age_band_order}
    sector_distribution = {}
    retirement_distribution = {}
    domain_distribution = {}
    location_distribution = {}
    portal_distribution = {}

    for a in filtered:
        exp_distribution[a['exp_band']] = exp_distribution.get(a['exp_band'], 0) + 1
        age_distribution[a['age_band']] = age_distribution.get(a['age_band'], 0) + 1
        sector_distribution[a['sector']] = sector_distribution.get(a['sector'], 0) + 1
        retirement_distribution[a['retirement']] = retirement_distribution.get(a['retirement'], 0) + 1
        domain_distribution[a['domain']] = domain_distribution.get(a['domain'], 0) + 1
        location_distribution[a['city']] = location_distribution.get(a['city'], 0) + 1
        portal_distribution[a['portal']] = portal_distribution.get(a['portal'], 0) + 1

    # ---- REPORT 2: Outreach & Response Performance ----
    resp_keys = ['Positive', 'Neutral', 'Negative', 'No Response', 'Pending']
    resp_by_domain = {}
    resp_by_exp = {b: {rk: 0 for rk in resp_keys} for b in band_order}
    for b in band_order: resp_by_exp[b]['total'] = 0

    resp_by_segment = {
        'P1 Preferred': {rk: 0 for rk in resp_keys},
        'P2 Expansion': {rk: 0 for rk in resp_keys},
        'Unclassified': {rk: 0 for rk in resp_keys}
    }
    for k in resp_by_segment: resp_by_segment[k]['total'] = 0

    resp_by_location = {}

    for a in filtered:
        resp = a['call_response']
        dom = a['domain']
        band = a['exp_band']
        city = a['city']
        seg_key = 'P1 Preferred' if 'P1' in a['segment'] else ('P2 Expansion' if 'P2' in a['segment'] else 'Unclassified')

        # Domain
        if dom not in resp_by_domain:
            resp_by_domain[dom] = {rk: 0 for rk in resp_keys}
            resp_by_domain[dom]['total'] = 0
        resp_by_domain[dom][resp] = resp_by_domain[dom].get(resp, 0) + 1
        resp_by_domain[dom]['total'] += 1

        # Location
        if city not in resp_by_location:
            resp_by_location[city] = {rk: 0 for rk in resp_keys}
            resp_by_location[city]['total'] = 0
        resp_by_location[city][resp] = resp_by_location[city].get(resp, 0) + 1
        resp_by_location[city]['total'] += 1

        # Experience
        resp_by_exp[band][resp] = resp_by_exp[band].get(resp, 0) + 1
        resp_by_exp[band]['total'] += 1

        # Segment
        resp_by_segment[seg_key][resp] = resp_by_segment[seg_key].get(resp, 0) + 1
        resp_by_segment[seg_key]['total'] += 1

    # ---- REPORT 3: Interview Agreement ----
    interview_by_domain = {}
    interview_by_exp = {b: {'total': 0, 'agreed': 0} for b in band_order}
    interview_by_segment = {
        'P1 Preferred': {'total': 0, 'agreed': 0},
        'P2 Expansion': {'total': 0, 'agreed': 0},
        'Unclassified': {'total': 0, 'agreed': 0}
    }
    interview_mode_split = {'Yes - In Person': 0, 'Yes - Virtual': 0, 'Pending': 0, 'Declined': 0, 'Not Discussed': 0, 'Unknown': 0}
    total_agreed_interview = 0

    for a in filtered:
        iv = a['interview_agreed']
        dom = a['domain']
        band = a['exp_band']
        seg_key = 'P1 Preferred' if 'P1' in a['segment'] else ('P2 Expansion' if 'P2' in a['segment'] else 'Unclassified')
        agreed = iv.startswith('Yes')

        if agreed: total_agreed_interview += 1
        if dom not in interview_by_domain:
            interview_by_domain[dom] = {'total': 0, 'agreed': 0}
        interview_by_domain[dom]['total'] += 1
        if agreed: interview_by_domain[dom]['agreed'] += 1

        interview_by_exp[band]['total'] += 1
        if agreed: interview_by_exp[band]['agreed'] += 1

        interview_by_segment[seg_key]['total'] += 1
        if agreed: interview_by_segment[seg_key]['agreed'] += 1

        mode_key = iv if iv in interview_mode_split else 'Unknown'
        interview_mode_split[mode_key] += 1

    # ---- REPORT 4: Advisory Role Progression & Acceptance ----
    advisory_counts = {'Agreed': 0, 'Interested - More Info Needed': 0, 'Declined': 0, 'Not Discussed': 0, 'Unknown': 0}
    advisory_by_domain = {}
    advisory_by_exp = {b: {'total': 0, 'agreed': 0, 'interested': 0} for b in band_order}
    advisory_by_segment = {
        'P1 Preferred': {'total': 0, 'agreed': 0, 'interested': 0},
        'P2 Expansion': {'total': 0, 'agreed': 0, 'interested': 0},
        'Unclassified': {'total': 0, 'agreed': 0, 'interested': 0}
    }
    advisory_by_location = {}

    for a in filtered:
        adv = a['advisory_interest']
        dom = a['domain']
        band = a['exp_band']
        city = a['city']
        seg_key = 'P1 Preferred' if 'P1' in a['segment'] else ('P2 Expansion' if 'P2' in a['segment'] else 'Unclassified')

        key = adv if adv in advisory_counts else 'Unknown'
        advisory_counts[key] += 1

        is_agreed = (adv == 'Agreed')
        is_interested = (adv == 'Interested - More Info Needed')

        for grp, k in [(advisory_by_domain, dom), (advisory_by_location, city)]:
            if k not in grp: grp[k] = {'total': 0, 'agreed': 0, 'interested': 0}
            grp[k]['total'] += 1
            if is_agreed: grp[k]['agreed'] += 1
            if is_interested: grp[k]['interested'] += 1

        advisory_by_exp[band]['total'] += 1
        if is_agreed: advisory_by_exp[band]['agreed'] += 1
        if is_interested: advisory_by_exp[band]['interested'] += 1

        advisory_by_segment[seg_key]['total'] += 1
        if is_agreed: advisory_by_segment[seg_key]['agreed'] += 1
        if is_interested: advisory_by_segment[seg_key]['interested'] += 1

    # Master Conversion Funnel (Cohort-aware counts with explicit denominators)
    filtered_total = len(filtered)
    total_called = sum(1 for a in filtered if a['call_response'] != 'Pending')
    total_reached = sum(1 for a in filtered if a['call_response'] in ['Positive', 'Neutral', 'Negative'])
    total_positive = sum(1 for a in filtered if a['call_response'] == 'Positive')
    total_positive_explicit = sum(1 for a in filtered if a['call_response'] == 'Positive' and a['call_provenance'] == 'explicit')
    total_positive_inferred = sum(1 for a in filtered if a['call_response'] == 'Positive' and a['call_provenance'] == 'inferred')

    # Rates with stated denominators
    def calc_rate_str(num, den):
        if den == 0: return "N/A"
        return f"{round((num / den) * 100, 1)}%"

    # Privacy-safe drill-down list (no phone, no email)
    drilldown_candidates = [
        {
            'id': a['id'],
            'name': a['name'],
            'role': a['role'],
            'domain': a['domain'],
            'city': a['city'],
            'portal': a['portal'],
            'exp_band': a['exp_band'],
            'age': a['age'] or 'Unknown',
            'sector': a['sector'],
            'retirement': a['retirement'],
            'segment': a['segment'],
            'segment_reason': a['segment_reason'],
            'call_response': a['call_response'],
            'call_provenance': a['call_provenance'],
            'interview_agreed': a['interview_agreed'],
            'advisory_interest': a['advisory_interest']
        }
        for a in filtered
    ]

    return jsonify({
        "success": True,
        "report_version": "2.1.0",
        "definitions_version": "2026.1-unified",
        "as_of": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "active_filters": {
            "segment": filter_segment,
            "portal": filter_portal,
            "provenance": filter_provenance
        },
        "data_completeness": {
            "total_records": total_pool_size,
            "explicit_age_count": explicit_age_count,
            "explicit_age_pct": round((explicit_age_count / max(1, total_pool_size)) * 100, 1),
            "explicit_sector_count": explicit_sector_count,
            "explicit_sector_pct": round((explicit_sector_count / max(1, total_pool_size)) * 100, 1),
            "explicit_ret_count": explicit_ret_count,
            "explicit_ret_pct": round((explicit_ret_count / max(1, total_pool_size)) * 100, 1),
            "explicit_call_responses": explicit_resp_count,
            "inferred_call_responses": inferred_resp_count,
            "call_response_confirmed_pct": round((explicit_resp_count / max(1, (explicit_resp_count + inferred_resp_count))) * 100, 1)
        },
        "audience_summary": {
            "p1_criteria": "Age > 50 (51+), Sector == Government, Status == Retired",
            "p2_criteria": "Age >= 45 or Exp >= 15 yrs, Sectors: Govt, PSU, Banking, Defence",
            "overall_counts": overall_segment_counts,
            "filtered_count": filtered_total
        },
        "funnel": {
            "sourced": filtered_total,
            "called": total_called,
            "reached": total_reached,
            "positive_response": total_positive,
            "positive_explicit": total_positive_explicit,
            "positive_inferred": total_positive_inferred,
            "interview_agreed": total_agreed_interview,
            "advisory_interested": advisory_counts.get('Interested - More Info Needed', 0),
            "advisory_agreed": advisory_counts.get('Agreed', 0),
            "rates": {
                "outreach_rate": calc_rate_str(total_called, filtered_total),
                "reach_rate": calc_rate_str(total_reached, total_called),
                "positive_rate": calc_rate_str(total_positive, total_called),
                "interview_agreement_rate": calc_rate_str(total_agreed_interview, total_called),
                "advisory_interest_rate": calc_rate_str(advisory_counts.get('Interested - More Info Needed', 0), filtered_total),
                "advisory_acceptance_rate": calc_rate_str(advisory_counts.get('Agreed', 0), filtered_total)
            }
        },
        "exp_distribution": exp_distribution,
        "age_distribution": age_distribution,
        "sector_distribution": sector_distribution,
        "retirement_distribution": retirement_distribution,
        "domain_distribution": dict(sorted(domain_distribution.items(), key=lambda x: -x[1])[:15]),
        "location_distribution": dict(sorted(location_distribution.items(), key=lambda x: -x[1])[:15]),
        "portal_distribution": portal_distribution,
        "resp_by_domain": {k: v for k, v in sorted(resp_by_domain.items(), key=lambda x: -x[1]['total'])[:12]},
        "resp_by_exp": resp_by_exp,
        "resp_by_segment": resp_by_segment,
        "resp_by_location": {k: v for k, v in sorted(resp_by_location.items(), key=lambda x: -x[1]['total'])[:12]},
        "interview_by_domain": dict(sorted(interview_by_domain.items(), key=lambda x: -x[1]['total'])[:12]),
        "interview_by_exp": interview_by_exp,
        "interview_by_segment": interview_by_segment,
        "interview_mode_split": interview_mode_split,
        "total_agreed_interview": total_agreed_interview,
        "advisory_counts": advisory_counts,
        "advisory_by_domain": dict(sorted(advisory_by_domain.items(), key=lambda x: -x[1]['total'])[:12]),
        "advisory_by_exp": advisory_by_exp,
        "advisory_by_segment": advisory_by_segment,
        "advisory_by_location": dict(sorted(advisory_by_location.items(), key=lambda x: -x[1]['total'])[:12]),
        "candidates_drilldown": drilldown_candidates
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
