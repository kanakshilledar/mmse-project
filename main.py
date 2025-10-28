import json
import os

USERS_FILE = "users.json"
REQUESTS_FILE = "requests.json"


def load_data(file_path):
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r") as f:
        return json.load(f)

def save_data(file_path, data):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)

def find_user(username):
    users = load_data(USERS_FILE)
    for user in users:
        if user["username"] == username:
            return user
    return None

def find_request_by_id(request_id):
    requests = load_data(REQUESTS_FILE)
    for req in requests:
        if req["id"] == request_id:
            return req
    return None


def register_user():
    print("\n=== User Registration ===")
    username = input("Enter username: ").strip()
    if find_user(username):
        print("[!] Username already exists.")
        return
    password = input("Enter password: ").strip()
    role = input("Enter role (SM/PM/FM/HR/SCS): ").strip().upper()

    user = {"username": username, "password": password, "role": role}
    users = load_data(USERS_FILE)
    users.append(user)
    save_data(USERS_FILE, users)
    print("[*] Registration successful!")

def login_user():
    print("\n=== User Login ===")
    username = input("Enter username: ").strip()
    password = input("Enter password: ").strip()

    user = find_user(username)
    if not user or user["password"] != password:
        print("[!] Invalid credentials.")
        return None
    print(f"[*] Welcome, {user['username']} ({user['role']})")
    return user


def create_financial_request(user):
    print("\n=== Create Financial Request ===")
    if user["role"] not in ["SM", "PM"]:
        print("[!] Only SM or PM can create financial requests.")
        return

    amount = input("Enter amount: ").strip()
    reason = input("Enter reason: ").strip()
    request = {
        "id": len(load_data(REQUESTS_FILE)) + 1,
        "created_by": user["username"],
        "amount": amount,
        "reason": reason,
        "status": "PENDING",
        "fm_note": ""
    }

    requests = load_data(REQUESTS_FILE)
    requests.append(request)
    save_data(REQUESTS_FILE, requests)
    print("[*] Financial request submitted!")

def view_all_requests():
    requests = load_data(REQUESTS_FILE)
    if not requests:
        print("No requests found.")
        return
    for r in requests:
        print(f"\nID: {r['id']}\nBy: {r['created_by']}\nAmount: {r['amount']}\nReason: {r['reason']}\nStatus: {r['status']}\nFM Note: {r['fm_note']}")

def review_request(user):
    print("\n=== Review Financial Requests ===")
    if user["role"] != "FM":
        print("[!] Only FM can review financial requests.")
        return

    requests = load_data(REQUESTS_FILE)
    pending = [r for r in requests if r["status"] == "PENDING"]
    if not pending:
        print("No pending requests to review.")
        return

    for r in pending:
        print(f"\nRequest ID: {r['id']} | By: {r['created_by']} | Amount: {r['amount']} | Reason: {r['reason']}")
        decision = input("Approve (A) / Reject (R): ").strip().upper()
        note = input("Add a note (optional): ").strip()

        if decision == "A":
            r["status"] = "APPROVED"
        elif decision == "R":
            r["status"] = "REJECTED"
        else:
            print("[!] Invalid input. Skipping this request.")
            continue
        r["fm_note"] = note

    save_data(REQUESTS_FILE, requests)
    print("[*] Review process completed.")


def finance_menu(user):
    while True:
        if user["role"] in ["SM", "PM"]:
            print("\n1. Create Financial Request\n2. View All Requests\n3. Logout")
            choice = input("Choose: ").strip()
            if choice == "1":
                create_financial_request(user)
            elif choice == "2":
                view_all_requests()
            elif choice == "3":
                break
            else:
                print("[!] Invalid choice.")
        elif user["role"] == "FM":
            print("\n1. View All Requests\n2. Review Requests\n3. Logout")
            choice = input("Choose: ").strip()
            if choice == "1":
                view_all_requests()
            elif choice == "2":
                review_request(user)
            elif choice == "3":
                break
            else:
                print("[!] Invalid choice.")
        else:
            print("No financial permissions for this role.")
            break


def main():
    print("=== SEP Management CLI (Iteration 2) ===")

    while True:
        print("\n1. Register\n2. Login\n3. Exit")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            register_user()
        elif choice == "2":
            user = login_user()
            if user:
                finance_menu(user)
        elif choice == "3":
            print("[+] Exiting program.")
            break
        else:
            print("[!] Invalid option.")

# Testing the methods

def test_review_request():
    # prepare mock data
    save_data(REQUESTS_FILE, [{
        "id": 1,
        "created_by": "alice",
        "amount": "5000",
        "reason": "Workshop materials",
        "status": "PENDING",
        "fm_note": ""
    }])

    user = {"username": "bob", "role": "FM"}
    requests = load_data(REQUESTS_FILE)
    assert requests[0]["status"] == "PENDING"
    requests[0]["status"] = "APPROVED"
    requests[0]["fm_note"] = "Approved for Q1"
    save_data(REQUESTS_FILE, requests)

    updated = load_data(REQUESTS_FILE)
    assert updated[0]["status"] == "APPROVED"
    assert updated[0]["fm_note"] == "Approved for Q1"
    print("[*] Test: FM review request passed.")

if __name__ == "__main__":
    test_review_request()
    main()
