# system.py
# REFACTORED:
# 1. System now persists 'clients' and 'event_requests' to JSON files.
# 2. __init__ now loads data from files instead of starting empty.
# 3. All workflow delegate methods now save changes back to the JSON files.

import models
import event_workflow
import client_workflow
import users  # This module handles file-based user storage
import storage # Handles low-level file load/save
import datetime

# --- Constants for database files ---
CLIENTS_FILE = "clients.json"
REQUESTS_FILE = "event_requests.json"


class SEP_System:
    """
    The main system class.
    - Loads/Saves data from JSON files (users, clients, requests).
    - Manages authentication (login/logout)
    - Delegates business logic to workflow modules.
    """
    def __init__(self):
        # Ensure database files exist
        storage.ensure_files([CLIENTS_FILE, REQUESTS_FILE, users.USERS_FILE])
        
        # Load all data from files
        self._load_all_data()
        
        self.current_user = None

    # --- Data Persistence (Load/Save) ---

    def _load_all_data(self):
        """Loads and deserializes clients and requests from JSON files."""
        print("Loading data from database files...")
        
        # --- 1. Load Clients ---
        clients_data = storage.load_data(CLIENTS_FILE)
        self.clients = {}
        max_client_id = 0
        for c_data in clients_data:
            try:
                client = models.Client(name=c_data['name'])
                client.record_number = c_data['record_number']
                client.event_history_ids = c_data['event_history_ids']
                self.clients[client.record_number] = client
                
                # Calculate next ID
                num_id = int(client.record_number[1:]) # Get num from "c1"
                if num_id > max_client_id:
                    max_client_id = num_id
            except (KeyError, TypeError, ValueError) as e:
                print(f"Warning: Skipping malformed client data. Error: {e}")
        self.next_client_id = max_client_id + 1

        # --- 2. Load Event Requests (must be after clients) ---
        requests_data = storage.load_data(REQUESTS_FILE)
        self.event_requests = {}
        max_req_id = 0
        for r_data in requests_data:
            try:
                # Re-hydrate references
                initiated_by = self.find_user(r_data.get('initiated_by_username'))
                owner = self.find_user(r_data.get('owner_username'))
                client = self.find_client_by_record_number(r_data.get('client_record_number'))

                if not initiated_by or not owner:
                    print(f"Warning: Skipping request {r_data.get('request_id')}, user not found.")
                    continue

                # Create object
                req = models.EventRequest(
                    initiated_by=initiated_by,
                    client=client,
                    event_type=r_data.get('event_type'),
                    date=r_data.get('date'),
                    preferences=r_data.get('preferences'),
                    client_expected_budget=r_data.get('client_expected_budget')
                )
                
                # Set state fields
                req.request_id = r_data['request_id']
                req.status = r_data['status']
                req.owner = owner
                req.fm_estimated_cost = r_data.get('fm_estimated_cost')
                
                # Re-hydrate comments
                req.comments_log = []
                for c_comment in r_data.get('comments_log', []):
                    comment_user = self.find_user(c_comment['user_username'])
                    if comment_user:
                        comment = models.Comment(user=comment_user, message=c_comment['message'])
                        comment.timestamp = datetime.datetime.fromisoformat(c_comment['timestamp'])
                        req.comments_log.append(comment)
                        
                self.event_requests[req.request_id] = req
                if req.request_id > max_req_id:
                    max_req_id = req.request_id
            except (KeyError, TypeError, ValueError) as e:
                 print(f"Warning: Skipping malformed request data. Error: {e}")
        self.next_request_id = max_req_id + 1
        print("Data loaded.")


    def _save_all_data(self):
        """Serializes and saves all clients and requests back to JSON."""
        
        # --- 1. Serialize Clients ---
        clients_data = []
        for client in self.clients.values():
            clients_data.append({
                'name': client.name,
                'record_number': client.record_number,
                'event_history_ids': client.event_history_ids
            })
        storage.save_data(CLIENTS_FILE, clients_data)

        # --- 2. Serialize Event Requests ---
        requests_data = []
        for req in self.event_requests.values():
            # Serialize comments
            comments_list = []
            for comment in req.comments_log:
                comments_list.append({
                    'user_username': comment.user['username'],
                    'message': comment.message,
                    'timestamp': comment.timestamp.isoformat() # Store as string
                })
            
            # Serialize request
            req_dict = {
                'request_id': req.request_id,
                'status': req.status,
                'event_type': req.event_type,
                'date': req.date,
                'preferences': req.preferences,
                'client_expected_budget': req.client_expected_budget,
                'fm_estimated_cost': req.fm_estimated_cost,
                
                # Store references as simple, lookup-able strings
                'initiated_by_username': req.initiated_by['username'],
                'owner_username': req.owner['username'],
                'client_record_number': req.client.record_number if req.client else None,
                
                'comments_log': comments_list
            }
            requests_data.append(req_dict)
        storage.save_data(REQUESTS_FILE, requests_data)
        # print("System data saved.") # Optional: for debugging


    # --- User Management ---
    
    def add_user(self):
        """Adds a user via users.py (which saves to users.json)."""
        return users.register_user()

    def find_user(self, username):
        """Finds a user from users.json."""
        return users.find_user(username)
            
    def find_user_by_role(self, role):
        """Finds the first user of a role from users.json."""
        all_users = users.load_data(users.USERS_FILE)
        for user in all_users:
            if user["role"] == role:
                return user
        return None

    # --- Client Management (In-Memory) ---

    def add_client(self, client):
        """
        [CHANGED]
        Adds a client to the in-memory dictionary.
        Does NOT save; 'create_client' delegate handles saving.
        """
        client_id_str = f"c{self.next_client_id}"
        self.next_client_id += 1
        
        client.record_number = client_id_str
        self.clients[client_id_str] = client
        return client

    def find_client_by_name(self, client_name):
        """Finds the first client matching a name (case-insensitive)."""
        for client in self.clients.values():
            if client.name.lower() == client_name.lower():
                return client
        return None

    def find_client_by_record_number(self, record_number):
        """Finds a client by their unique record_number."""
        return self.clients.get(record_number)
        
    # --- Request Management (In-Memory) ---
    
    def add_request(self, request):
        """
        [CHANGED]
        Adds a request to the in-memory dictionary.
        Does NOT save; delegate methods handle saving.
        """
        request_id = self.next_request_id
        self.next_request_id += 1
        
        request.request_id = request_id
        self.event_requests[request_id] = request
        
        # Link to client's history if client exists (for drafts)
        if request.client:
            request.client.event_history_ids.append(request.request_id)
        
        # Note: We don't save here. We save at the end of the
        # workflow method (e.g., create_draft_request)

    def find_request_by_id(self, request_id):
        """Finds an event request by its unique ID."""
        return self.event_requests.get(request_id)
        
    # --- Authentication ---
    
    def login(self, username):
        """Logs in a user from users.json."""
        user = self.find_user(username)
        if user:
            self.current_user = user
            # print(f"User '{username}' logged in. Role: '{user['role']}'")
        else:
            raise ValueError(f"User '{username}' not found.")
            
    def logout(self):
        self.current_user = None

    # --- Workflow Delegate Methods (Client) ---
    
    def search_client_by_name(self, client_name):
        """
        [CHANGED]
        Searches for an existing client by name.
        Authorization is now handled directly in this method.
        """
        # 1. Authorization Check
        # Roles previously defined in client_workflow
        allowed_roles = ["CS", "SCS", "FM", "AM", "Marketing"] 
        if not self.current_user or self.current_user['role'] not in allowed_roles:
            raise PermissionError("You do not have permission to search client records.")
            
        # 2. Logic (call the internal search method)
        # This is a read-only operation, no save needed.
        return self.find_client_by_name(client_name)
        
    def create_client(self, client_name):
        """
        [CHANGED]
        Creates a new client directly and saves the new state.
        No longer delegates to client_workflow.
        """
        # 1. Authorization Check
        allowed_roles = ["CS", "SCS"]
        if not self.current_user or self.current_user['role'] not in allowed_roles:
            raise PermissionError("Only Customer Service officers can create new clients.")

        # 2. Prevent Duplication
        existing_client = self.find_client_by_name(client_name)
        if existing_client:
            raise ValueError(f"Client with name '{client_name}' already exists.")
            
        # 3. Create and add the client (using the internal method)
        new_client = models.Client(name=client_name)
        self.add_client(new_client) # This adds to self.clients
        
        print(f"New client created: {new_client.name} (ID: {new_client.record_number})")
        
        # 4. Save the new state
        self._save_all_data() # Save changes
        
        # 5. Return the new client
        return new_client

    # --- Workflow Delegate Methods (Event) ---
    
    def create_draft_request(self):
        """
        [CHANGED]
        Delegates creation, then saves the new state.
        """
        new_request = event_workflow.create_draft_request(
            system=self,
            current_user=self.current_user
        )
        self._save_all_data() # Save new draft
        return new_request
        
    def update_draft_request(self, request_id, client_record_number=None, event_type=None, date=None, preferences=None, client_expected_budget=None):
        """
        [CHANGED]
        Delegates update, then saves the modified state.
        """
        request = self.find_request_by_id(request_id)
        if not request:
            raise ValueError(f"Request ID {request_id} not found.")
            
        client = None
        if client_record_number:
            client = self.find_client_by_record_number(client_record_number)
            if not client:
                raise ValueError(f"Client ID {client_record_number} not found.")

        updated_request = event_workflow.update_draft_request(
            system=self,
            current_user=self.current_user,
            request=request,
            client=client,
            event_type=event_type,
            date=date,
            preferences=preferences,
            client_expected_budget=client_expected_budget # NEW
        )
        self._save_all_data() # Save changes
        return updated_request
        
    def initiate_event_request(self, request_id):
        """
        [CHANGED]
        Delegates submission, then saves the state change.
        """
        request = self.find_request_by_id(request_id)
        if not request:
            raise ValueError(f"Request ID {request_id} not found.")

        submitted_request = event_workflow.initiate_event_request(
            system=self,
            current_user=self.current_user,
            request=request
        )
        self._save_all_data() # Save changes (status, owner)
        return submitted_request
    
    def scs_review_request(self, request_id, is_approved, comments=""):
        """
        [CHANGED]
        Delegates review, then saves the state change.
        """
        request = self.find_request_by_id(request_id)
        if not request:
            raise ValueError(f"Request ID {request_id} not found.")
            
        reviewed_request = event_workflow.scs_review(
            system=self,
            current_user=self.current_user,
            request=request,
            is_approved=is_approved,
            comments=comments
        )
        self._save_all_data() # Save changes (status, owner, comments)
        return reviewed_request
        
    def fm_review_request(self, request_id, is_approved, comments="", estimated_cost=None):
        """
        [CHANGED]
        Delegates review, then saves the state change.
        """
        request = self.find_request_by_id(request_id)
        if not request:
            raise ValueError(f"Request ID {request_id} not found.")
            
        reviewed_request = event_workflow.fm_review(
            system=self,
            current_user=self.current_user,
            request=request,
            is_approved=is_approved,
            comments=comments,
            estimated_cost=estimated_cost # NEW
        )
        self._save_all_data() # Save changes
        return reviewed_request

    def am_decide_request(self, request_id, is_approved, comments=""):
        """
        [CHANGED]
        Delegates decision, then saves the state change.
        """
        request = self.find_request_by_id(request_id)
        if not request:
            raise ValueError(f"Request ID {request_id} not found.")
            
        decided_request = event_workflow.am_decide(
            system=self,
            current_user=self.current_user,
            request=request,
            is_approved=is_approved,
            comments=comments
        )
        self._save_all_data() # Save changes
        return decided_request

