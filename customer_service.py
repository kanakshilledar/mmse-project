# customer_service.py
# CS actions only:
# 1) Create Draft
# 2) Update My Drafts
# 3) Submit Draft → SCS

import clients
import event_requests


# --------------------------
# helpers
# --------------------------

def _in(prompt, required=True):
    while True:
        v = input(f"{prompt}: ").strip()
        if v or not required:
            return v
        print("Required.")

def _int(prompt):
    while True:
        v = input(f"{prompt}: ").strip()
        try:
            return int(v)
        except:
            print("Enter a number.")


# --------------------------
# internal helpers
# --------------------------

def _view_my_drafts(user):
    drafts = event_requests.get_requests_by_status_and_user(user, "DRAFT")
    if not drafts:
        print("No drafts.")
        return []

    print("\n--- My Drafts ---")
    for r in drafts:
        print(f"ID: {r.get('id')}  |  Amount: {r.get('amount')}  |  Reason: {r.get('reason')}")
    return drafts


# --------------------------
# CREATE
# --------------------------

def create_draft(user):
    print("\n=== Create Draft ===")

    cname = _in("Client name")
    c = clients.find_client_by_name(cname)
    if not c:
        print("Client not found. Must create in CS menu first.")
        return

    amount = _int("Estimated Amount")
    reason = _in("Reason")

    req = event_requests.create_draft_request(
        cs_user=user,
        client_dict=c,
        amount=amount,
        reason=reason,
    )

    print(f"✅ Draft created – ID={req['id']}")


# --------------------------
# UPDATE
# --------------------------

def update_draft(user):
    print("\n=== Update Draft ===")

    drafts = _view_my_drafts(user)
    if not drafts:
        return

    req_id = _in("Draft ID")
    req = event_requests.find_request_by_id(req_id)

    if not req or req.get("created_by") != user["username"] or req.get("status") != "DRAFT":
        print("Invalid / not owned.")
        return

    updates = {}

    amount = _in(f"Amount [{req.get('amount')}]", required=False)
    if amount:
        try:
            updates["amount"] = int(amount)
        except:
            print("Invalid amount → ignored")

    reason = _in(f"Reason [{req.get('reason')}]", required=False)
    if reason:
        updates["reason"] = reason

    if not updates:
        print("No changes.")
        return

    event_requests.update_draft_request(req_id, user, updates)
    print("✅ Draft updated.")


# --------------------------
# SUBMIT → SCS
# --------------------------

def submit_draft(user):
    print("\n=== Submit Draft ===")

    drafts = _view_my_drafts(user)
    if not drafts:
        return

    req_id = _in("Draft ID")
    req = event_requests.submit_draft_for_review(req_id, user)

    print(f"✅ Submitted → SCS")
