# event_requests.py
import datetime
import storage
import users
import clients

FILE = "requests.json"
storage.ensure_file(FILE)


# --------------------------
# INTERNAL
# --------------------------
def _load():
    return storage.load_data(FILE)

def _save(data):
    storage.save_data(FILE, data)

def _next_id(allreq):
    mx = 0
    for r in allreq:
        if r.get("id", 0) > mx:
            mx = r["id"]
    return mx + 1


# --------------------------
# FINDERS
# --------------------------
def find_request_by_id(rid):
    try:
        rid = int(rid)
    except:
        return None

    for r in _load():
        if r.get("id") == rid:
            return r
    return None

def get_requests_for_user(user):
    uname = user["username"]
    return [r for r in _load() if r.get("created_by") == uname]


# --------------------------
# CS → CREATE DRAFT
# --------------------------
def create_draft_request(cs_user, client_dict, amount, reason):
    allreq = _load()

    r = {
        "id": _next_id(allreq),
        "created_by": cs_user["username"],
        "amount": amount,
        "reason": reason,
        "status": "DRAFT",
        "fm_note": ""
    }

    allreq.append(r)
    _save(allreq)

    clients.link_request_to_client(client_dict["record_number"], r["id"])
    return r


# --------------------------
# CS → UPDATE DRAFT
# --------------------------
def update_draft_request(rid, cs_user, updates: dict):
    allreq = _load()
    rid = int(rid)

    for idx, r in enumerate(allreq):
        if r.get("id") == rid:
            if r.get("created_by") != cs_user["username"]:
                raise PermissionError("Not allowed")

            for k, v in updates.items():
                if k in ("amount", "reason"):
                    r[k] = v

            allreq[idx] = r
            _save(allreq)
            return r

    raise ValueError("Not found")


# --------------------------
# CS → SCS
# --------------------------
def submit_draft_for_review(rid, cs_user):
    allreq = _load()
    rid = int(rid)

    scs = users.find_user_by_role("SCS")
    if not scs:
        raise Exception("No SCS account")

    for idx, r in enumerate(allreq):
        if r.get("id") == rid:
            if r.get("created_by") != cs_user["username"]:
                raise PermissionError("Not allowed")

            r["status"] = "PENDING_SCS"
            r["review_owner"] = scs["username"]

            allreq[idx] = r
            _save(allreq)
            return r

    raise ValueError("Not found")


# --------------------------
# SCS → FM
# --------------------------
def scs_review(rid, scs_user, approved, msg=""):
    allreq = _load()
    rid = int(rid)

    fm = users.find_user_by_role("FM")
    if not fm:
        raise Exception("No FM")

    for idx, r in enumerate(allreq):
        if r["id"] == rid:
            if r.get("status") != "PENDING_SCS":
                raise PermissionError("Not in SCS queue")

            if r.get("review_owner") != scs_user["username"]:
                raise PermissionError("Not assigned to you")

            # log
            if msg:
                r.setdefault("comments_log", [])
                r["comments_log"].append({
                    "user": scs_user["username"],
                    "message": msg,
                    "ts": datetime.datetime.now().isoformat()
                })

            if approved:
                r["status"] = "PENDING_FM"
                r["owner_username"] = fm["username"]
            else:
                r["status"] = "REJECTED_BY_SCS"

            allreq[idx] = r
            _save(allreq)
            return r

    raise ValueError("Not found")
def get_scs_queue(scs_user):
    return [
        r for r in _load()
        if r.get("status") == "PENDING_SCS"
    ]



# --------------------------
# FM → AM / SCS
# --------------------------
def fm_review(rid, fm_user, approved, msg="", cost=None):
    allreq = _load()
    rid = int(rid)

    am = users.find_user_by_role("AM")
    scs = users.find_user_by_role("SCS")

    for idx, r in enumerate(allreq):
        if r.get("id") == rid:
            if r.get("review_owner") != fm_user["username"] or r.get("status") != "PENDING_FM":
                raise PermissionError("Not allowed")

            _add_comment(r, fm_user, msg)

            if cost is not None:
                r["fm_note"] = f"Est Cost: {cost}"

            if approved:
                r["status"] = "PENDING_AM"
                r["review_owner"] = am["username"]
            else:
                r["status"] = "REJECTED_FM"
                r["review_owner"] = scs["username"]

            allreq[idx] = r
            _save(allreq)
            return r

    raise ValueError("Not found")


# --------------------------
# AM → SCS (FINAL)
# --------------------------
def am_review(rid, am_user, approved, msg=""):
    allreq = _load()
    rid = int(rid)

    scs = users.find_user_by_role("SCS")

    for idx, r in enumerate(allreq):
        if r.get("id") == rid:
            if r.get("review_owner") != am_user["username"] or r.get("status") != "PENDING_AM":
                raise PermissionError("Not allowed")

            _add_comment(r, am_user, msg)

            if approved:
                r["status"] = "APPROVED"
            else:
                r["status"] = "REJECTED_AM"

            r["review_owner"] = scs["username"]

            allreq[idx] = r
            _save(allreq)
            return r

    raise ValueError("Not found")


# --------------------------
# COMMENTS
# --------------------------
def _add_comment(r, user, msg):
    if not msg:
        return
    if "comments_log" not in r:
        r["comments_log"] = []
    r["comments_log"].append({
        "user": user["username"],
        "message": msg,
        "ts": datetime.datetime.now().isoformat()
    })


# --------------------------
# FILTER
# --------------------------
def get_requests_by_status_and_user(user, status):
    uname = user["username"]
    return [
        r for r in _load()
        if r.get("created_by") == uname and r.get("status") == status
    ]
