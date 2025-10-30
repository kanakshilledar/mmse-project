# cs_manager.py
# Provides the menu and prompt logic for Customer Service (CS) users.

import clients
import event_requests
import users # Needed to find the SCS user
import storage
import datetime

REQUESTS_FILE = "event_requests.json" # Added for in-file request creation

# --- Internal Helper Functions for Event Requests (copied from event_requests.py) ---

def _cs_get_all_requests():
    """Helper to load all event request data."""
    return storage.load_data(REQUESTS_FILE)

def _cs_save_all_requests(requests_list):
    """Helper to save all event request data."""
    storage.save_data(REQUESTS_FILE, requests_list)

def _cs_get_next_request_id(all_requests):
    """Calculates the next unique request ID."""
    max_id = 0
    for req in all_requests:
        try:
            if req['request_id'] > max_id:
                max_id = req['request_id']
        except (KeyError, TypeError):
            continue
    return max_id + 1

def _cs_add_comment(request, user, message):
    """Internal helper to add a comment dict to a request."""
    if not message:
        return # Don't add empty comments
        
    comment = {
        "user_username": user['username'],
        "message": message,
        "timestamp": datetime.datetime.now().isoformat()
    }
    request['comments_log'].append(comment)


# --- Helper Functions (from original file, needed by the new menu) ---

def _handle_create_request(system, user):
    """
    Handles the UI prompts for creating a new draft request.
    [MODIFIED] This function now contains all logic for creating
    a request and no longer calls event_requests.create_draft_request.
    """
    print("\n--- Create New Event Request ---")
    
    # 1. Get Client
    client_name = input("Enter client name: ").strip()
    client = system.search_client_by_name(client_name)
    
    if not client:
        print(f"Client '{client_name}' not found.")
        choice = input("Create this client? (y/n): ").strip().lower()
        if choice == 'y':
            try:
                # [FIXED] Call system.create_client for authorization
                client = system.create_client(client_name)
                print(f"Client '{client['name']}' created with ID {client['record_number']}.")
            except (ValueError, PermissionError) as e:
                print(f"Error creating client: {e}")
                return
        else:
            print("Aborting request. A valid client is required.")
            return

    # 2. Get Event Details
    event_type = input("Enter event type (e.g., Workshop, Conference): ").strip()
    date = input("Enter event date (YYYY-MM-DD): ").strip()
    preferences = input("Enter preferences (e.g., decorations, catering): ").strip()
    
    try:
        budget_str = input("Enter client's expected budget: ").strip()
        client_expected_budget = int(budget_str)
    except ValueError:
        print("Invalid budget. Please enter a number.")
        return

    # 3. [NEW LOGIC] Create the event request directly
    
    all_requests = _cs_get_all_requests()
    
    new_request_id = _cs_get_next_request_id(all_requests)
    
    new_request = {
        "request_id": new_request_id,
        "status": "Draft",
        
        # Data fields
        "client_record_number": client['record_number'],
        "event_type": event_type,
        "date": date,
        "preferences": preferences,
        "client_expected_budget": client_expected_budget,
        "fm_estimated_cost": None,

        # State and Log
        "initiated_by_username": user['username'],
        "owner_username": user['username'], # CS owns the draft
        "comments_log": []
    }
    
    _cs_add_comment(new_request, user, "Draft created.")
    
    all_requests.append(new_request)
    _cs_save_all_requests(all_requests)
    
    # Link this request to the client's history
    clients.link_request_to_client(client['record_number'], new_request_id)
    
    print(f"\nSuccess! Draft request {new_request['request_id']} has been created.")


def _handle_update_draft(system, user):
    """Handles the UI prompts for updating an existing draft."""
    print("\n--- Update Draft Request ---")
    
    _handle_view_my_requests(system, user, "Draft") # Show only drafts
    
    request_id = input("Enter the Request ID of the draft you want to update (or leave blank to cancel): ").strip()
    if not request_id:
        return

    request = event_requests.find_request_by_id(request_id) # Still uses event_requests to find

    if not request:
        print("Error: Request not found.")
        return
    
    if request['owner_username'] != user['username'] or request['status'] != "Draft":
        print("Error: You do not have permission to edit this draft.")
        return

    print(f"Updating Request {request_id}. Press ENTER to skip a field.")
    
    # --- Collect Updates ---
    updates = {}
    
    event_type = input(f"Event Type (current: {request['event_type']}): ").strip()
    if event_type: updates['event_type'] = event_type
    
    date = input(f"Date (current: {request['date']}): ").strip()
    if date: updates['date'] = date
    
    preferences = input(f"Preferences (current: {request['preferences']}): ").strip()
    if preferences: updates['preferences'] = preferences
    
    budget_str = input(f"Budget (current: {request['client_expected_budget']}): ").strip()
    if budget_str:
        try:
            updates['client_expected_budget'] = int(budget_str)
        except ValueError:
            print("Invalid budget, skipping field.")

    # --- Call the function ---
    if updates:
        event_requests.update_draft_request(request['request_id'], user, updates) # Still uses event_requests to update
    else:
        print("No changes made.")


def _handle_submit_draft(system, user):
    """Handles the UI prompts for submitting a draft for review."""
    print("\n--- Submit Draft for Review ---")
    
    _handle_view_my_requests(system, user, "Draft") # Show only drafts
    
    request_id = input("Enter the Request ID of the draft to submit (or leave blank to cancel): ").strip()
    if not request_id:
        return

    request = event_requests.find_request_by_id(request_id) # Still uses event_requests to find

    if not request:
        print("Error: Request not found.")
        return

    # Find the SCS user to assign the request to
    scs_user = system.find_user_by_role("SCS")
    if not scs_user:
        print("System Error: No 'SCS' user found to assign the request to. Aborting.")
        return

    # Call the function
    event_requests.submit_draft_for_review(request['request_id'], user, scs_user) # Still uses event_requests to submit


def _handle_view_my_requests(system, user, status_filter=None):
    """
    Shows all requests currently owned by the user.
    Can optionally filter by a specific status (e.g., "Draft").
    """
    if not status_filter:
        print("\n--- My Event Requests ---")
    
    my_requests = event_requests.get_requests_for_user(user)
    
    if not my_requests:
        print("You do not own any requests.")
        return
        
    found_requests = False
    for req in my_requests:
        # Apply filter if one is provided
        if status_filter and req['status'] != status_filter:
            continue
            
        found_requests = True
        client_name = "N/A"
        client = clients.find_client_by_record_number(req['client_record_number'])
        if client:
            client_name = client['name']
            
        print(f"  ID: {req['request_id']} | Status: {req['status']} | Client: {client_name} | Event: {req['event_type']}")
    
    if not found_requests and status_filter:
        print(f"You have no requests with status '{status_filter}'.")


# --- Main CS Menu (Your new menu structure) ---

def cs_menu(system, user):
    """
    Main menu loop for Customer Service users.
    """
    print(f"\n--- Welcome, {user['username']} (Customer Service) ---")
    
    while True:
        print("\nCustomer Service Menu:")
        print("1. Create New Client")
        print("2. Search for Client")
        print("3. Create New Event Draft")
        print("4. View & Update My Drafts")
        print("5. Submit Draft for Review")
        print("0. Logout")
        
        choice = input("Enter your choice: ").strip()
        
        try:
            if choice == '1':
                # --- Create Client ---
                client_name = input("Enter new client's name: ").strip()
                if client_name:
                    # [FIXED] Call system.create_client to enforce authorization
                    new_client = system.create_client(client_name)
                    print(f"Client '{new_client['name']}' created with ID {new_client['record_number']}.")
                
            elif choice == '2':
                # --- Search Client ---
                client_name = input("Enter client's name to search: ").strip()
                if client_name:
                    # [FIXED] Call system.search_client_by_name for authorization
                    client = system.search_client_by_name(client_name)
                    if client:
                        print("\n--- Client Found ---")
                        print(f"  Name: {client['name']}")
                        print(f"  ID: {client['record_number']}")
                        print(f"  Event History IDs: {client['event_history_ids']}")
                    else:
                        print("No client found with that name.")
            
            elif choice == '3':
                # --- Create Draft ---
                # [FIXED] Call the helper that prompts for all details
                _handle_create_request(system, user)
                
            elif choice == '4':
                # --- View & Update Draft ---
                # [FIXED] Call the helpers for viewing and updating
                _handle_update_draft(system, user)
                
            elif choice == '5':
                # --- Submit Draft ---
                # [FIXED] Call the helper for submitting
                _handle_submit_draft(system, user)
                
            elif choice == '0':
                # --- Logout ---
                print(f"Logging out {user['username']}...")
                break
                
            else:
                print("Invalid choice, please try again.")
        
        except (ValueError, PermissionError) as e:
            print(f"\n--- ERROR: {e} ---")
        except Exception as e:
            # Catch unexpected errors
            print(f"\nAn unexpected error occurred: {e}\n")

