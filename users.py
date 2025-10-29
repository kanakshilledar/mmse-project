from storage import USERS_FILE, load_data, save_data

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
        print("Username already exists.")
        return
    password = input("Enter password: ").strip()
    role = input("Enter role (SM/PM/FM/HR/SCS/LEAD/MEMBER): ").strip().upper()
    if role in ["LEAD", "MEMBER"]:
        subteam = input(f"Enter subteam {username} is part of: ").strip()
    else:
        subteam = "N/A"
    users = load_data(USERS_FILE)
    user = {"id": len(users) + 1, "username": username, "password": password, 
            "role": role, "subteam": subteam}
    
    users.append(user)
    save_data(USERS_FILE, users)
    print("Registration successful.")

def login_user():
    print("\n=== User Login ===")
    username = input("Enter username: ").strip()
    password = input("Enter password: ").strip()
    user = find_user(username)
    if not user or user["password"] != password:
        print("Invalid credentials.")
        return None
    print(f"Welcome, {user['username']} ({user['role']})")
    return user

def change_password(user):
    print("\n=== Change Password ===")
    old = input("Enter old password: ").strip()
    if old != user["password"]:
        print("Incorrect old password.")
        return
    new = input("Enter new password: ").strip()
    users = load_data(USERS_FILE)
    for u in users:
        if u["username"] == user["username"]:
            u["password"] = new
    save_data(USERS_FILE, users)
    user["password"] = new
    print("Password updated successfully.")
