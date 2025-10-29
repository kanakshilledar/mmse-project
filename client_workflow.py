import models
from auth import requires_role # <-- Import the decorator

@requires_role(
    allowed_roles=["CS", "SCS", "FM", "AM", "Marketing"], 
    error_message="You do not have permission to search client records."
)
def search_client_by_name(system, current_user, client_name):
    """
    Use Case: Search for existing client.
    Authorization is handled by the decorator.
    """
    # Authorization logic is removed!
    return system.find_client_by_name(client_name)

@requires_role(
    allowed_roles=["CS", "SCS"], 
    error_message="Only Customer Service officers can create new clients."
)
def create_client(system, current_user, client_name):
    """
    Use Case: Create new client profile.
    Prevents duplication.
    Authorization is handled by the decorator.
    """
    # Authorization logic is removed!

    # 1. Prevent Duplication (as per use case)
    existing_client = system.find_client_by_name(client_name)
    if existing_client:
        raise ValueError(f"Client with name '{client_name}' already exists.")
        
    # 2. Create and add the client
    new_client = models.Client(name=client_name)
    system.add_client(new_client)
    
    print(f"New client created: {new_client.name} (ID: {new_client.record_number})")
    return new_client