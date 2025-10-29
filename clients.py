from storage import CLIENTS_FILE, load_data, save_data

def _get_all_clients():
    """Helper to load all client data."""
    return load_data(CLIENTS_FILE)

def _save_all_clients(clients_list):
    """Helper to save all client data."""
    save_data(CLIENTS_FILE, clients_list)

def find_client_by_name(client_name):
    """
    Finds the first client matching a name (case-insensitive).
    Returns the client dictionary or None.
    """
    all_clients = _get_all_clients()
    for client in all_clients:
        if client['name'].lower() == client_name.lower():
            return client
    return None

def find_client_by_record_number(record_number):
    """
    Finds a client by their unique record_number.
    Returns the client dictionary or None.
    """
    all_clients = _get_all_clients()
    for client in all_clients:
        if client['record_number'] == record_number:
            return client
    return None

def create_client(client_name):
    """
    Creates a new client, saves it, and returns the new client dict.
    Handles ID generation and duplicate name checks.
    """
    all_clients = _get_all_clients()
    
    # 1. Prevent Duplication
    if any(c['name'].lower() == client_name.lower() for c in all_clients):
        raise ValueError(f"Client with name '{client_name}' already exists.")

    # 2. Generate new ID
    max_id = 0
    for c in all_clients:
        try:
            num_id = int(c['record_number'][1:]) # Get num from "c1"
            if num_id > max_id:
                max_id = num_id
        except (ValueError, TypeError, IndexError):
            continue # Skip malformed record_number
            
    new_id_num = max_id + 1
    new_record_number = f"c{new_id_num}"

    # 3. Create and add the client
    new_client = {
        "name": client_name,
        "record_number": new_record_number,
        "event_history_ids": []
    }
    all_clients.append(new_client)
    
    # 4. Save to file
    _save_all_clients(all_clients)
    
    return new_client

def link_request_to_client(client_record_number, request_id):
    """
    Adds an event request ID to a client's history.
    """
    all_clients = _get_all_clients()
    client_found = False
    for client in all_clients:
        if client['record_number'] == client_record_number:
            if request_id not in client['event_history_ids']:
                client['event_history_ids'].append(request_id)
                client_found = True
                break
    
    if client_found:
        _save_all_clients(all_clients)
    else:
        # This should ideally not happen if checks are done before calling
        print(f"Warning: Could not link request {request_id} to client {client_record_number}. Client not found.")
