"""
hr_manager.py 
Manages staff recruitment and HR workflows.

Data files and schema:
- employees.txt    id|name|role|subteam
- staff_requests.txt id|department|role|reason|requested_by|status|hr_comments
"""

import os
from file_utils import read_lines, write_lines, next_id
from constants import STAFF_REQ_FILE, DEPARTMENTS, RequestStatus

#requests
def submit_staff_request(department, role, reason, requested_by):
    if department not in DEPARTMENTS:
        raise ValueError(f"Invalid department: {department}")
    if not role or not reason:
        raise ValueError("Role and reason required.")
    lines = read_lines(STAFF_REQ_FILE)
    nid = next_id(lines)
    lines.append("|".join([nid, department, role, reason, requested_by, RequestStatus.PENDING, ""]))
    write_lines(STAFF_REQ_FILE, lines)
    return nid

def list_staff_requests():
    lines = read_lines(STAFF_REQ_FILE)
    return [
        dict(
            id=p[0], department=p[1], role=p[2],
            reason=p[3], requested_by=p[4],
            status=p[5], hr_comments=p[6] if len(p) > 6 else ""
        )
        for l in lines if (p := l.split("|"))
    ]

def review_request(request_id, approve, hr_comment=""):
    lines = read_lines(STAFF_REQ_FILE)
    found = False
    new_lines = []
    for l in lines:
        parts = l.split("|")
        if parts[0] == str(request_id):
            found = True
            parts[5] = RequestStatus.APPROVED if approve else RequestStatus.REJECTED
            parts[6] = hr_comment
        new_lines.append("|".join(parts))
    if not found:
        raise ValueError("Request not found.")
    write_lines(STAFF_REQ_FILE, new_lines)
    return True

