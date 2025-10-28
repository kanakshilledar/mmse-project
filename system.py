# system.py
# The main application file. Holds the central system and data.

import models
import event_workflow # Import the logic functions
import client_workflow
class SEP_System:
    """
    The main system class.
    - Holds all in-memory data (users, requests)
    - Manages authentication (login/logout)
    - Delegates business logic to workflow modules.
    
    REFACTORED: This class now uses dictionaries for data storage
    to allow for fast, O(1) lookups by ID or username.
    """
    def __init__(self):
        # REFACTORED: Data structures are now dictionaries (hash maps).
        # This provides fast lookups by a unique key.
        self.users = {}          # key: username, value: User object
        self.clients = {}        # key: record_number, value: Client object
        self.event_requests = {} # key: request_id, value: EventRequest object
        
        # REFACTORED: Added robust counters for unique ID generation.
        self.next_client_id = 1
        self.next_request_id = 1
        
        self.current_user = None

    # --- Authentication ---
    
    def login(self, username):
        """Logs in a user by their username."""
        # REFACTORED: Fast O(1) lookup instead of a list loop
        user = self.users.get(username)
        if user:
            self.current_user = user
            print(f"User '{username}' logged in. Role: '{user.role}'")
        else:
            raise ValueError(f"User '{username}' not found.")
            
    def logout(self):
        """Logs out the current user."""
        self.current_user = None

    # --- User Management ---
    
    def add_user(self, user):
        """Adds a new user to the system."""
        # REFACTORED: Adds to a dictionary using username as the key
        if user.username in self.users:
            raise ValueError(f"User '{user.username}' already exists.")
        self.users[user.username] = user

    def find_user(self, username):
        """Finds a user by their username."""
        # REFACTORED: Fast O(1) lookup
        return self.users.get(username)
        
    def find_user_by_role(self, role):
        """Finds the *first* user with a specific role."""
        # REFACTORED: Iterates over dictionary values
        for user in self.users.values():
            if user.role == role:
                return user # Returns the first user with that role
        return None

    # --- Client Management ---

    def add_client(self, client):
        """Adds a new client, assigning a unique record number."""
        # REFACTORED: Uses the ID counter
        record_number = f"c{self.next_client_id}"
        self.next_client_id += 1
        
        client.record_number = record_number
        self.clients[record_number] = client
        return client
        
    def find_client_by_record_number(self, record_number):
        """Finds a client by their unique record number."""
        # REFACTORED: Fast O(1) lookup
        return self.clients.get(record_number)

    def find_client_by_name(self, client_name):
        """Finds the *first* client by their name (case-insensitive)."""
        # REFACTORED: Iterates over dictionary values
        for client in self.clients.values():
            if client.name.lower() == client_name.lower():
                return client
        return None

    # --- Event Request Management ---

    def add_request(self, request):
        """Adds a new event request, assigning a unique ID."""
        # REFACTORED: Uses the ID counter
        request_id = self.next_request_id
        self.next_request_id += 1
        
        request.request_id = request_id
        self.event_requests[request_id] = request
        
        # This logic is still correct and handles the "missing relationship"
        # of a draft request not having a client.
        if request.client:
            request.client.event_history.append(request)
        return request

    def find_request_by_id(self, request_id):
        """Finds an event request by its unique ID."""
        # REFACTORED: Fast O(1) lookup
        return self.event_requests.get(request_id)

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
        
    def update_draft_request(self, request_id, client_record_number=None, event_type=None, date=None, preferences=None):
        """Delegates updating a draft."""
        
        # REFACTORED: Lookups are now fast O(1) operations
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
            preferences=preferences
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
        """Delegates the SCS review."""
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

    def fm_review_request(self, request_id, is_approved, comments=""):
        """Delegates the FM review."""
        request = self.find_request_by_id(request_id)
        if not request:
            raise ValueError(f"Request ID {request_id} not found.")
            
        return event_workflow.fm_review(
            system=self,
            current_user=self.current_user,
            request=request,
            is_approved=is_approved,
            comments=comments
        )

    def am_decide_request(self, request_id, is_approved, comments=""):
        """Delegates the AM decision."""
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