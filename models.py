# This implementation follows the Test-Driven Development (TDD)
# and other guidelines from the project presentation.


class User:
    """
    A simple class to hold user data.
    In a real system, this would be more complex.
    """
    def __init__(self, username, role):
        self.username = username
        self.role = role # e.g., "CS", "SCS", "FM", "AM" [cite: 17]

    def __repr__(self):
        return f"User(username='{self.username}', role='{self.role}')"

class Client:
    """
    NEW: Represents a client record.
   
    """
    def __init__(self, name):
        self.record_number = None # Will be set by the system
        self.name = name
        self.event_history = [] # A list of event requests
        
    def __repr__(self):
        return f"Client(id={self.record_number}, name='{self.name}')"
class EventRequest:
    """
    Represents a single event request.
    UPDATED: Now supports partial creation and "Draft" status.
    """
    
    # --- THIS METHOD IS UPDATED ---
    def __init__(self, initiated_by, client=None, event_type=None, date=None, preferences=None):
        self.request_id = None 
        
        # --- Data fields ---
        self.client = client
        self.event_type = event_type
        self.date = date
        self.preferences = preferences
        self.initiated_by = initiated_by
        
        # --- State Management ---
        # A new request starts as a "Draft" owned by the creator
        self.status = "Draft" 
        self.owner = initiated_by 
        
    def __repr__(self):
        owner_name = self.owner.username if self.owner else "None"
        return f"EventRequest(id={self.request_id}, client='{self.client.name if self.client else 'N/A'}', status='{self.status}')"