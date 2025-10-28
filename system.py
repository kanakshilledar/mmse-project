# system.py
# The main application file. Holds the central system and data.

import models
import event_workflow # Import the logic functions
import client_workflow
class SEP_System:
    """
    The main system class.
    - Holds all in-memory data (users, requests) [cite: 86]
    - Manages authentication (login/logout) [cite: 88]
    - Delegates business logic to workflow modules.
    """
    def __init__(self):
        self.users = []
        self.event_requests = []
        self.clients = [] # NEW list to store clients
        self.current_user = None

    # --- System Utility Methods ---
    
    def add_user(self, user):
        self.users.append(user)

    def add_request(self, request):
        request.request_id = len(self.event_requests) + 1
        self.event_requests.append(request)
        # Also link it to the client
        request.client.event_history.append(request)

    def find_user(self, username):
        for user in self.users:
            if user.username == username:
                return user
        return None
        
    def find_user_by_role(self, role):
        for user in self.users:
            if user.role == role:
                return user # Returns the first user with that role
        return None

    def find_request_by_id(self, request_id):
        for req in self.event_requests:
            if req.request_id == request_id:
                return req
        return None
# --- System Utility Methods (Clients) - NEW ---
    def add_client(self, client):
        client.record_number = f"c{len(self.clients) + 1}" # e.g., "c1", "c2"
        self.clients.append(client)
        
    def find_client_by_name(self, client_name):
        for client in self.clients:
            if client.name.lower() == client_name.lower():
                return client
        return None

    def find_client_by_record_number(self, record_number):
        for client in self.clients:
            if client.record_number == record_number:
                return client
        return None
    def login(self, username):
        user = self.find_user(username)
        if user:
            self.current_user = user
            print(f"User '{username}' logged in. Role: '{user.role}'")
        else:
            raise ValueError(f"User '{username}' not found.")
            
    def logout(self):
        self.current_user = None

# --- Workflow Delegate Methods (Client) - NEW ---
    
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
    # --- Workflow "Delegate" Methods ---
    # These functions call the imported logic
    
    def initiate_event_request(self, client_record_number, event_type, date, preferences):
        """
        Delegates to the event_workflow.
        UPDATED: Takes client_record_number.
        """
        return event_workflow.initiate_event_request(
            system=self,
            current_user=self.current_user,
            client_record_number=client_record_number, # Pass the ID
            event_type=event_type,
            date=date,
            preferences=preferences
        )
    
    def scs_review_request(self, request_id, is_approved, comments=""):
        """
        Delegates the SCS review to the event_workflow module.
        """
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
        """
        Delegates the FM review to the event_workflow module.
        """
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
        """
        Delegates the AM decision to the event_workflow module.
        """
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