import json
import os

USERS_FILE = "users.json"
REQUESTS_FILE = "requests.json"

def ensure_file(file_path):
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            json.dump([], f)

def load_data(file_path):
    ensure_file(file_path)
    with open(file_path, "r") as f:
        return json.load(f)

def save_data(file_path, data):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)
