# client_workflow.py
# REFACTORED: Removed decorators and added explicit authorization
# checks back into each function.
# FIXED: Changed object access (.role) to dictionary access (['role'])
#        to work with file-based user dictionaries.

import models

def search_client_by_name(system, current_user, client_name):
    """
    Use Case: Search for existing client.
    Checks authorization for searching.
    """
    # 1. Authorization Check
    allowed_roles = ["CS", "SCS", "FM", "AM", "Marketing"] 
    # --- FIX 1 ---
    # Was: current_user.role
    if not current_user or current_user['role'] not in allowed_roles:
        raise PermissionError("You do not have permission to search client records.")
    
    # 2. Logic
    return system.find_client_by_name(client_name)

def create_client(system, current_user, client_name):
    """
    Use Case: Create new client profile.
    Prevents duplication.
    """
    # 1. Authorization Check
    allowed_roles = ["CS", "SCS"]
    # --- FIX 2 ---
    # Was: current_user.role
    if not current_user or current_user['role'] not in allowed_roles:
        raise PermissionError("Only Customer Service officers can create new clients.")

    # 2. Prevent Duplication (as per use case)
    existing_client = system.find_client_by_name(client_name)
    if existing_client:
        raise ValueError(f"Client with name '{client_name}' already exists.")
        
    # 3. Create and add the client
    new_client = models.Client(name=client_name)
    system.add_client(new_client)
    
    # print(f"New client created: {new_client.name} (ID: {new_client.record_number})")
    return new_client
