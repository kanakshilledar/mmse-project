import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from storage import REQUESTS_FILE, save_data, load_data

def test_create_and_view_requests():
    save_data(REQUESTS_FILE, [])
    requests = load_data(REQUESTS_FILE)
    requests.append({
        "id": 1,
        "created_by": "alice",
        "amount": "1500",
        "reason": "Office setup",
        "status": "PENDING",
        "fm_note": ""
    })
    save_data(REQUESTS_FILE, requests)

    updated = load_data(REQUESTS_FILE)
    assert len(updated) == 1
    assert updated[0]["created_by"] == "alice"
    print("Test (finance): Create request passed.")

def test_review_request():
    save_data(REQUESTS_FILE, [{
        "id": 1,
        "created_by": "alice",
        "amount": "2000",
        "reason": "Repairs",
        "status": "PENDING",
        "fm_note": ""
    }])

    requests = load_data(REQUESTS_FILE)
    requests[0]["status"] = "APPROVED"
    requests[0]["fm_note"] = "Approved for Q2"
    save_data(REQUESTS_FILE, requests)

    updated = load_data(REQUESTS_FILE)
    assert updated[0]["status"] == "APPROVED"
    assert updated[0]["fm_note"] == "Approved for Q2"
    print("Test (finance): Review request passed.")

if __name__ == "__main__":
    test_create_and_view_requests()
    test_review_request()
    print("All finance tests passed.")
