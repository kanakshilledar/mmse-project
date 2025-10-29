# event_requests.py
# NEW FILE: Manages all event request data and business logic,
# similar to clients.py and users.py

import storage
import clients
import datetime

REQUESTS_FILE = "event_requests.json"

# --- Internal Helper Functions ---

def _get_all_requests():
    """Helper to load all event request data."""
    return storage.load_data(REQUESTS_FILE)

def _save_all_requests(requests_list):
    """Helper to save all event request data."""
    storage.save_data(REQUESTS_FILE, requests_list)

def _get_next_request_id(all_requests):
    """Calculates the next unique request ID."""
    max_id = 0
    for req in all_requests:
        try:
            if req['request_id'] > max_id:
                max_id = req['request_id']
        except (KeyError, TypeError):
            continue
    return max_id + 1

def _add_comment(request, user, message):
    """Internal helper to add a comment dict to a request."""
    if not message:
        return # Don't add empty comments
        
    comment = {
        "user_username": user['username'],
        "message": message,
        "timestamp": datetime.datetime.now().isoformat()
    }
    request['comments_log'].append(comment)

# --- Public API Functions ---

def find_request_by_id(request_id):
    """
    Finds a request by its unique ID.
    Returns the request dictionary or None.
    """
    try:
        req_id_int = int(request_id)
    except (ValueError, TypeError):
        return None
        
    all_requests = _get_all_requests()
    for req in all_requests:
        if req['request_id'] == req_id_int:
            return req
    return None

def get_requests_for_user(user):
    """
    Gets all requests currently owned by a specific user.
    """
    all_requests = _get_all_requests()
    user_requests = []
    for req in all_requests:
        if req['owner_username'] == user['username']:
            user_requests.append(req)
    return user_requests

def create_draft_request(cs_user, client_dict, event_type, date, preferences, client_expected_budget):
    """
    Creates a new, blank draft request.
    This is initiated by a CS Officer.
    """
    all_requests = _get_all_requests()
    
    new_request_id = _get_next_request_id(all_requests)
    
    new_request = {
        "request_id": new_request_id,
        "status": "Draft",
        
        # Data fields
        "client_record_number": client_dict['record_number'],
        "event_type": event_type,
        "date": date,
        "preferences": preferences,
        "client_expected_budget": client_expected_budget,
        "fm_estimated_cost": None,

        # State and Log
        "initiated_by_username": cs_user['username'],
        "owner_username": cs_user['username'], # CS owns the draft
        "comments_log": []
    }
    
    _add_comment(new_request, cs_user, "Draft created.")
    
    all_requests.append(new_request)
    _save_all_requests(all_requests)
    
    # Link this request to the client's history
    clients.link_request_to_client(client_dict['record_number'], new_request_id)
    
    print(f"New draft request (ID: {new_request_id}) created by '{cs_user['username']}'.")
    return new_request

def update_draft_request(request_id, cs_user, updates):
    """
    Updates fields on an existing draft request.
    'updates' is a dictionary of fields to change.
    """
    all_requests = _get_all_requests()
    request = find_request_by_id(request_id)
    
    if not request:
        raise ValueError(f"Request ID {request_id} not found.")
    
    if request['owner_username'] != cs_user['username'] or request['status'] != "Draft":
        raise PermissionError("You cannot edit this request.")
        
    updated_fields = []
    for key, value in updates.items():
        if key in request and request[key] != value:
            request[key] = value
            updated_fields.append(key)
            
            # If we are updating the client, we need to re-link
            if key == 'client_record_number':
                clients.link_request_to_client(value, request_id)

    if updated_fields:
        _add_comment(request, cs_user, f"Draft updated. Changed fields: {', '.join(updated_fields)}")
        
        # Find the request in the list and replace it
        for i, req in enumerate(all_requests):
            if req['request_id'] == request_id:
                all_requests[i] = request
                break
                
        _save_all_requests(all_requests)
        print(f"Draft request (ID: {request_id}) updated.")
    else:
        print("No changes detected.")
        
    return request

def submit_draft_for_review(request_id, cs_user, scs_user):
    """
    Submits a completed draft to the SCS for approval.
    Workflow: CS -> SCS
    """
    all_requests = _get_all_requests()
    request = find_request_by_id(request_id)

    if not request:
        raise ValueError(f"Request ID {request_id} not found.")
        
    if request['owner_username'] != cs_user['username'] or request['status'] != "Draft":
        raise PermissionError("This request cannot be submitted.")

    # Check for completeness
    if not request['client_record_number'] or not request['event_type'] or not request['date']:
        raise ValueError("Cannot submit incomplete draft. Client, Event Type, and Date are required.")
    
    # --- Update the request ---
    request['status'] = "Pending SCS Review"
    request['owner_username'] = scs_user['username']
    _add_comment(request, cs_user, f"Submitted for review to {scs_user['username']}.")

    # --- Save the changes ---
    for i, req in enumerate(all_requests):
        if req['request_id'] == request_id:
            all_requests[i] = request
            break
            
    _save_all_requests(all_requests)
    
    print(f"Event request (ID: {request_id}) submitted to '{scs_user['username']}'.")
    return request
