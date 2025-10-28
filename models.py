import datetime

class User:
    """
    A simple class to hold user data.
    """
    def __init__(self, username, role):
        self.username = username
        self.role = role # e.g., "CS", "SCS", "FM", "AM"

    def __repr__(self):
        return f"User(username='{self.username}', role='{self.role}')"

class Comment:
    """
    NEW: A structured class to hold comment data.
    This replaces the simple string in EventRequest.comments_log.
    """
    def __init__(self, user, message):
        self.user = user # The User object who made the comment
        self.message = message
        self.timestamp = datetime.datetime.now()

    def __repr__(self):
        # A short representation for debugging
        return f"Comment(user='{self.user.username}', time='{self.timestamp.strftime('%Y-%m-%d')}')"

class Client:
    """
    Represents a client record.
    """
    def __init__(self, name):
        self.record_number = None # Will be set by the system
        self.name = name
        
        # REFACTORED: This now stores request IDs, not objects.
        # This prevents a circular dependency.
        self.event_history_ids = [] # This will be a List[int]
        
    def __repr__(self):
        return f"Client(id={self.record_number}, name='{self.name}')"

class EventRequest:
    """
    Represents a single event request.
    """
    
    def __init__(self, initiated_by, client=None, event_type=None, date=None, preferences=None):
        self.request_id = None # Will be set by the system (int)
        
        # --- Data fields ---
        self.client = client # Client object
        self.event_type = event_type
        self.date = date
        self.preferences = preferences
        self.initiated_by = initiated_by # User object
        
        # --- State Management ---
        self.status = "Draft" 
        self.owner = initiated_by # User object
        
        # REFACTORED: This is now a list of structured Comment objects.
        self.comments_log = [] # This will be a List[Comment]
        
    def __repr__(self):
        owner_name = self.owner.username if self.owner else "None"
        client_name = self.client.name if self.client else "N/A"
        return f"EventRequest(id={self.request_id}, client='{client_name}', status='{self.status}')"

    def add_comment(self, user, message):
        """
        NEW: A helper method to add a structured comment.
        """
        if not message: # Don't add empty comments
            return
        comment = Comment(user=user, message=message)
        self.comments_log.append(comment)
