# client_workflow.py
# NEW FILE: Contains all logic for client management.

import models

def search_client_by_name(system, current_user, client_name):
    """
    Use Case: Search for existing client.
    Checks authorization for searching.
    """
    # Authorization: Many roles can search
    allowed_roles = ["CS", "SCS", "FM", "AM", "Marketing"] 
    if current_user.role not in allowed_roles:
        raise PermissionError("You do not have permission to search client records.")
        
    return system.find_client_by_name(client_name)

def create_client(system, current_user, client_name):
    """
    Use Case: Create new client profile.
    Prevents duplication.
    """
    # [cite_start]Authorization: Based on the slide [cite: 89] and prompt.
    allowed_roles = ["CS", "SCS"]
    if current_user.role not in allowed_roles:
        raise PermissionError("Only Customer Service officers can create new clients.")

    # 1. Prevent Duplication (as per use case)
    existing_client = system.find_client_by_name(client_name)
    if existing_client:
        raise ValueError(f"Client with name '{client_name}' already exists.")
        
    # 2. Create and add the client
    new_client = models.Client(name=client_name)
    system.add_client(new_client)
    
    print(f"New client created: {new_client.name} (ID: {new_client.record_number})")
    return new_client