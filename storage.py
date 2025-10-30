import json
import os

USERS_FILE = "users.json"
REQUESTS_FILE = "requests.json"
CLIENTS_FILE = "clients.json"
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

def ensure_files(*files):
    """Ensure that the specified files exist, creating them as empty JSON arrays if necessary."""
    if len(files) == 1 and isinstance(files[0], (list, tuple)):
        files = files[0]

    for f in files:
        if not os.path.exists(f):
            with open(f, "w", encoding="utf-8") as fh:
                json.dump([], fh)