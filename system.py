# system.py
# REFACTORED:
# 1. `update_draft_request` delegate now passes `client_expected_budget`.
# 2. `fm_review_request` delegate now passes `estimated_cost`.
# 3. User management (add, find, login) now delegates to the 'users.py' module
#    to use file-based storage instead of in-memory.

import models
import event_workflow
import client_workflow
import users  # This module handles file-based user storage

class SEP_System:
    """
    The main system class.
    - Holds all in-memory data (users, requests)
    - Manages authentication (login/logout)
    - Delegates business logic to workflow modules.
    
    REFACTORED:
    - Data lists (`clients`, `event_requests`) are now
      dictionaries for fast O(1) lookups by ID.
    - User data is now managed by the 'users' module.
    """
    def __init__(self):
        # self.users = {}  <-- This is no longer the source of truth
        self.clients = {}
        self.event_requests = {}
        
        # ID Counters
        self.next_client_id = 1
        self.next_request_id = 1
        
        self.current_user = None

    # --- User Management ---
    
    def add_user(self):
        """
        [CHANGED]
        Adds a user to the system by calling the interactive registration
        function from users.py.
        """
        # The original signature (self, user) was from the in-memory
        # object design. This new version calls the file-based,
        # interactive function you provided in users.py.
        return users.register_user()

    def find_user(self, username):
        """
        [CHANGED]
        Finds a user by their username by calling users.py.
        """
        # Was: return self.users.get(username)
        return users.find_user(username)
            
    def find_user_by_role(self, role):
        """
        [CHANGED]
        Finds the *first* user with a specific role by loading
        all users from the 'users' module storage.
        """
        # This must now load all users, since self.users is not used.
        all_users = users.load_data(users.USERS_FILE)
        for user in all_users:
            if user["role"] == role:
                return user
        return None

    # --- Client Management ---

    def add_client(self, client):
        """Adds a new client with a unique ID."""
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
        
    # --- Request Management ---
    
    def add_request(self, request):
        """Adds a new event request with a unique ID."""
        request_id = self.next_request_id
        self.next_request_id += 1
        
        request.request_id = request_id
        self.event_requests[request_id] = request
        
        # Link to client's history if client exists (for drafts)
        if request.client:
            request.client.event_history_ids.append(request.request_id)

    def find_request_by_id(self, request_id):
        """Finds an event request by its unique ID."""
        return self.event_requests.get(request_id)
        
    # --- Authentication ---
    
    def login(self, username):
        """
        [CHANGED]
        Logs in a user. Uses find_user (which now checks files)
        and handles the user as a dictionary, not an object.
        
        NOTE: This login does not check passwords. Your 'users.login_user()'
        is a better function for interactive login. This method is
        used by your automated tests.
        """
        user = self.find_user(username)
        if user:
            self.current_user = user
            # Access user data as a dictionary
            # print(f"User '{username}' logged in. Role: '{user['role']}'")
        else:
            raise ValueError(f"User '{username}' not found.")
            
    def logout(self):
        self.current_user = None

    # --- Workflow Delegate Methods (Client) ---
    
    def search_client_by_name(self, client_name):
        """Delegates searching to the client_workflow."""
        return client_workflow.search_client_by_name(
            system=self,
            current_user=self.current_user,
            client_name=client_name
        )
        
    def create_client(self, client_name):
        """Delegates creation to the client_workflow."""
        return client_workflow.create_client(
            system=self,
            current_user=self.current_user,
            client_name=client_name
        )

    # --- Workflow Delegate Methods (Event) ---
    
    def create_draft_request(self):
        """Delegates creating a blank draft."""
        return event_workflow.create_draft_request(
            system=self,
            current_user=self.current_user
        )
        
    def update_draft_request(self, request_id, client_record_number=None, event_type=None, date=None, preferences=None, client_expected_budget=None):
        """Delegates updating a draft."""
        request = self.find_request_by_id(request_id)
        if not request:
            raise ValueError(f"Request ID {request_id} not found.")
            
        client = None
        if client_record_number:
            client = self.find_client_by_record_number(client_record_number)
            if not client:
                raise ValueError(f"Client ID {client_record_number} not found.")

        return event_workflow.update_draft_request(
            system=self,
            current_user=self.current_user,
            request=request,
            client=client,
            event_type=event_type,
            date=date,
            preferences=preferences,
            client_expected_budget=client_expected_budget # NEW
        ) 
        
    def initiate_event_request(self, request_id):
        """Delegates submitting a draft."""
        request = self.find_request_by_id(request_id)
        if not request:
            raise ValueError(f"Request ID {request_id} not found.")

        return event_workflow.initiate_event_request(
            system=self,
            current_user=self.current_user,
            request=request
        )
    
    def scs_review_request(self, request_id, is_approved, comments=""):
        """Delegates the SCS review to the event_workflow module."""
        request = self.find_request_by_id(request_id)
        if not request:
            raise ValueError(f"Request ID {request_id} not found.")
            
        return event_workflow.scs_review(
            system=self,
            current_user=self.current_user,
            request=request,
            is_approved=is_approved,
            comments=comments
        )
        
    def fm_review_request(self, request_id, is_approved, comments="", estimated_cost=None):
        """Delegates the FM review to the event_workflow module."""
        request = self.find_request_by_id(request_id)
        if not request:
            raise ValueError(f"Request ID {request_id} not found.")
            
        return event_workflow.fm_review(
            system=self,
            current_user=self.current_user,
            request=request,
            is_approved=is_approved,
            comments=comments,
            estimated_cost=estimated_cost # NEW
        )

    def am_decide_request(self, request_id, is_approved, comments=""):
        """Delegates the AM decision to the event_workflow module."""
        request = self.find_request_by_id(request_id)
        if not request:
            raise ValueError(f"Request ID {request_id} not found.")
            
        return event_workflow.am_decide(
            system=self,
            current_user=self.current_user,
            request=request,
            is_approved=is_approved,
            comments=comments
        )