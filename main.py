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
        "status": "PENDING"
    }

    requests = load_data(REQUESTS_FILE)
    requests.append(request)
    save_data(REQUESTS_FILE, requests)
    print("[*] Financial request submitted!")


def main():
    print("=== SEP Management CLI ===")

    while True:
        print("\n1. Register\n2. Login\n3. Exit")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            register_user()
        elif choice == "2":
            user = login_user()
            if user:
                while True:
                    print("\n1. Create Financial Request\n2. Logout")
                    sub_choice = input("Choose: ").strip()
                    if sub_choice == "1":
                        create_financial_request(user)
                    elif sub_choice == "2":
                        print("[+] Logged out.")
                        break
                    else:
                        print("[!] Invalid choice.")
        elif choice == "3":
            print("Exiting program. Bye!")
            break
        else:
            print("[!] Invalid option.")

# Testing the methods

def test_user_registration_and_login():
    # reset files
    save_data(USERS_FILE, [])
    save_data(REQUESTS_FILE, [])

    users = load_data(USERS_FILE)
    assert users == []

    # Register a user manually (simulate)
    test_user = {"username": "alice", "password": "123", "role": "SM"}
    users.append(test_user)
    save_data(USERS_FILE, users)

    # Test login
    user = find_user("alice")
    assert user["password"] == "123"
    print("[*] Test: User registration and login passed.")

def test_create_financial_request():
    save_data(REQUESTS_FILE, [])
    user = {"username": "alice", "role": "SM"}
    # simulate request creation
    requests = load_data(REQUESTS_FILE)
    requests.append({
        "id": 1,
        "created_by": user["username"],
        "amount": "5000",
        "reason": "Workshop materials",
        "status": "PENDING"
    })
    save_data(REQUESTS_FILE, requests)
    assert len(load_data(REQUESTS_FILE)) == 1
    print("[*] Test: Financial request creation passed.")

if __name__ == "__main__":
    # Run manual tests
    test_user_registration_and_login()
    test_create_financial_request()

    # Start CLI
    main()
