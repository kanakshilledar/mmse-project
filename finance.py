from storage import REQUESTS_FILE, load_data, save_data
from users import change_password

def create_financial_request(user):
    print("\n=== Create Financial Request ===")
    if user["role"] not in ["SM", "PM"]:
        print("Only SM or PM can create financial requests.")
        return
    amount = input("Enter amount: ").strip()
    reason = input("Enter reason: ").strip()
    requests = load_data(REQUESTS_FILE)
    request = {
        "id": len(requests) + 1,
        "created_by": user["username"],
        "amount": amount,
        "reason": reason,
        "status": "PENDING",
        "fm_note": ""
    }
    requests.append(request)
    save_data(REQUESTS_FILE, requests)
    print("Financial request submitted.")

def view_my_requests(user):
    print("\n=== My Financial Requests ===")
    requests = load_data(REQUESTS_FILE)
    mine = [r for r in requests if r["created_by"] == user["username"]]
    if not mine:
        print("You have no requests.")
        return
    for r in mine:
        print(f"\nID: {r['id']}\nAmount: {r['amount']}\nReason: {r['reason']}\nStatus: {r['status']}\nFM Note: {r['fm_note']}")

def view_all_requests():
    requests = load_data(REQUESTS_FILE)
    if not requests:
        print("No requests found.")
        return
    for r in requests:
        print(f"\nID: {r['id']}\nBy: {r['created_by']}\nAmount: {r['amount']}\nReason: {r['reason']}\nStatus: {r['status']}\nFM Note: {r['fm_note']}")

def review_requests(user):
    if user["role"] != "FM":
        print("Only FM can review financial requests.")
        return
    requests = load_data(REQUESTS_FILE)
    pending = [r for r in requests if r["status"] == "PENDING"]
    if not pending:
        print("No pending requests.")
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
            print("Invalid input. Skipping.")
            continue
        r["fm_note"] = note
    save_data(REQUESTS_FILE, requests)
    print("Review process completed.")

def finance_menu(user):
    while True:
        if user["role"] in ["SM", "PM"]:
            print("\n1. Create Financial Request\n2. View My Requests\n3. Change Password\n4. Logout")
            choice = input("Choose: ").strip()
            if choice == "1":
                create_financial_request(user)
            elif choice == "2":
                view_my_requests(user)
            elif choice == "3":
                change_password(user)
            elif choice == "4":
                break
            else:
                print("Invalid choice.")
        elif user["role"] == "FM":
            print("\n1. View All Requests\n2. Review Requests\n3. Change Password\n4. Logout")
            choice = input("Choose: ").strip()
            if choice == "1":
                view_all_requests()
            elif choice == "2":
                review_requests(user)
            elif choice == "3":
                change_password(user)
            elif choice == "4":
                break
            else:
                print("Invalid choice.")
        else:
            print("No financial permissions for this role.")
            break
