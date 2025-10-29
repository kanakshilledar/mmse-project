"""
hr_manager.py
Manages staff recruitment and HR workflows using JSON files.

Data files and schema:
- employees.json    [{"id", "name", "role", "subteam"}]
- staff_requests.json [{"id", "department", "role_required", "reason", "requested_by", "status", "hr_comments"}]
"""

from storage import load_data, save_data, ensure_files
from constants import STAFF_REQ_FILE, DEPARTMENTS, RequestStatus

# Ensure file exists at startup
ensure_files(STAFF_REQ_FILE)


# ---------- Staff Requests ----------

def submit_staff_request(department, role_required, reason, requested_by):
    """Submit a new staff request."""
    if department not in DEPARTMENTS:
        raise ValueError(f"Invalid department: {department}")
    if not role_required or not reason:
        raise ValueError("Role and reason required.")

    requests = load_data(STAFF_REQ_FILE)
    rid = len(requests) + 1
    req = {
        "id": rid,
        "department": department,
        "role_required": role_required,
        "reason": reason,
        "requested_by": requested_by,
        "status": RequestStatus.PENDING,
        "hr_comments": ""
    }
    requests.append(req)
    save_data(STAFF_REQ_FILE, requests)
    return rid


def list_staff_requests():
    """Return all staff requests as a list of dicts."""
    return load_data(STAFF_REQ_FILE)


def review_request(request_id, approve, hr_comment=""):
    """Approve or reject a staff request."""
    requests = load_data(STAFF_REQ_FILE)
    found = False
    for req in requests:
        if req["id"] == request_id or str(req["id"]) == str(request_id):
            req["status"] = RequestStatus.APPROVED if approve else RequestStatus.REJECTED
            req["hr_comments"] = hr_comment
            found = True
            break
    if not found:
        raise ValueError("Request not found")
    save_data(STAFF_REQ_FILE, requests)
    return True
