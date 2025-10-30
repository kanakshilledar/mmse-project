# # models.py
# # REFACTORED:
# # 1. Added `client_expected_budget` and `fm_estimated_cost` to EventRequest.
# # 2. FIXED: Removed the unused 'User' class.
# # 3. FIXED: Updated 'Comment' and 'EventRequest' classes to use
# #    dictionary access (e.g., user['username']) for user data.

# import datetime


# class Client:
#     """Represents a client record."""
#     def __init__(self, name):
#         self.record_number = None
#         self.name = name
#         self.event_history_ids = [] # Stores EventRequest IDs
        
#     def __repr__(self):
#         return f"Client(id={self.record_number}, name='{self.name}')"

# class Comment:
#     """Represents a single comment in the log."""
#     def __init__(self, user, message):
#         self.user = user # user is now a dictionary
#         self.message = message
#         self.timestamp = datetime.datetime.now()
        
#     def __repr__(self):
#         # --- FIX 1 ---
#         # Was: self.user.username
#         user_name = self.user['username'] if self.user else "System"
#         return f"Comment(user='{user_name}', msg='{self.message[:20]}...')"

# class EventRequest:
#     """
#     Represents a single event request.
#     """
    
#     def __init__(self, initiated_by, client=None, event_type=None, date=None, preferences=None, client_expected_budget=None):
#         self.request_id = None 
        
#         # --- Data fields ---
#         self.client = client
#         self.event_type = event_type
#         self.date = date
#         self.preferences = preferences
#         self.initiated_by = initiated_by # This is a user dictionary
        
#         # --- NEW BUDGET FIELDS ---
#         self.client_expected_budget = client_expected_budget
#         self.fm_estimated_cost = None
        
#         # --- State Management ---
#         self.status = "Draft" 
#         self.owner = initiated_by # This is also a user dictionary
        
#         # --- Log ---
#         self.comments_log = [] # A list of Comment objects
        
#     def add_comment(self, user, message):
#         """Helper to add a structured comment."""
#         if message:
#             # user is passed as a dictionary, which is what
#             # the Comment constructor now expects.
#             comment = Comment(user=user, message=message)
#             self.comments_log.append(comment)
        
#     def __repr__(self):
#         # --- FIX 2 ---
#         # Was: self.owner.username
#         owner_name = self.owner['username'] if self.owner else "None"
#         return f"EventRequest(id={self.request_id}, client='{self.client.name if self.client else 'N/A'}', status='{self.status}', owner='{owner_name}')"
