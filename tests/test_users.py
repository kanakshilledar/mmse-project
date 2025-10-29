import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from storage import USERS_FILE, save_data, load_data
from users import find_user

def test_change_password():
    save_data(USERS_FILE, [{"id": 1, "username": "alice", "password": "123", "role": "SM", "subteam": "N/A"}])
    user = {"id": 1, "username": "alice", "password": "123", "role": "SM", "subteam": "N/A"}

    users = load_data(USERS_FILE)
    users[0]["password"] = "xyz"
    save_data(USERS_FILE, users)

    updated = find_user("alice")
    assert updated["password"] == "xyz"
    print("Test (users): Change password passed.")

def test_user_registration():
    save_data(USERS_FILE, [])
    users = load_data(USERS_FILE)
    users.append({"id": 1, "username": "bob", "password": "abc", "role": "FM", "subteam": "N/A"})
    save_data(USERS_FILE, users)
    found = find_user("bob")
    assert found is not None
    assert found["role"] == "FM"
    print("Test (users): Registration and lookup passed.")

if __name__ == "__main__":
    test_change_password()
    test_user_registration()
    print("All user tests passed.")
