# event_workflow.py
# Contains all logic for the event request workflow.
# REFACTORED:
# 1. Now uses request.add_comment() to log structured comments.
# 2. Added a _find_user_or_raise helper to reduce code duplication.

import models # We import the data classes

def _find_user_or_raise(system, role):
    """A private helper to find a user or raise an error."""
    user = system.find_user_by_role(role)
    if not user:
        raise EnvironmentError(f"System Error: No {role} user found.")
    return user

def create_draft_request(system, current_user):
    """
    Creates a new, blank draft request.
    """
    # 1. Authorization Check
    if not current_user or current_user.role != "CS":
        raise PermissionError("Only Customer Service (CS) users can create drafts.")

    # 2. Create the blank request object
    new_request = models.EventRequest(initiated_by=current_user)

    # 3. Save the request (Data is stored in-memory in the system)
    system.add_request(new_request)
    
    print(f"New draft request (ID: {new_request.request_id}) created by '{current_user.username}'.")
    return new_request

def update_draft_request(system, current_user, request, client=None, event_type=None, date=None, preferences=None):
    """
    Updates fields on an existing draft request.
    """
    # 1. Authorization Check
    if not current_user or current_user.role != "CS":
        raise PermissionError("Only Customer Service (CS) users can update drafts.")
        
    if request.owner != current_user or request.status != "Draft":
        raise PermissionError("You cannot edit this request.")
        
    # 2. Update fields
    if client:
        request.client = client
    if event_type:
        request.event_type = event_type
    if date:
        request.date = date
    if preferences:
        request.preferences = preferences
        
    print(f"Draft request (ID: {request.request_id}) updated.")
    return request


def initiate_event_request(system, current_user, request):
    """
    Use Case: Submit a completed draft for approval.
    Workflow: CS -> SCS
    """
    
    # 1. Authorization Check
    if not current_user or current_user.role != "CS":
        raise PermissionError("Only Customer Service (CS) users can submit requests.")
    if request.owner != current_user or request.status != "Draft":
        raise PermissionError("This request cannot be submitted.")

    # 2. Validation Check (Ensure form is not partial)
    if not request.client or not request.event_type or not request.date:
        raise ValueError("Cannot submit incomplete draft. Client, Event Type, and Date are required.")

    # 3. Find the next person in the workflow (SCS)
    scs_officer = _find_user_or_raise(system, "SCS")
        
    # 4. Set the new state of the request
    request.status = "Pending SCS Review"
    request.owner = scs_officer
    
    print(f"Event request (ID: {request.request_id}) submitted to '{scs_officer.username}'.")
    return request

def scs_review(system, current_user, request, is_approved, comments):
    """
    Use Case: Request Review (SCS)
    Workflow: SCS -> FM (if approved) or SCS -> CS (if rejected)
    """
    # 1. Authorization Check
    if not current_user or current_user.role != "SCS":
        raise PermissionError("Only SCS users can review.")
    
    if request.owner != current_user:
        raise PermissionError("You are not the owner of this request.")
    
    # 2. REFACTORED: Add structured comment
    request.add_comment(user=current_user, message=comments)
        
    # 3. Process Logic
    if is_approved:
        fm_manager = _find_user_or_raise(system, "FM")
        request.status = "Pending FM Review"
        request.owner = fm_manager
        print(f"Request {request.request_id} approved by SCS, sent to FM.")
    else:
        # Workflow sends it back to Customer Service (the original creator)
        cs_initiator = request.initiated_by
        request.status = "Rejected by SCS"
        request.owner = cs_initiator
        print(f"Request {request.request_id} rejected by SCS, sent back to CS.")

def fm_review(system, current_user, request, is_approved, comments):
    """
    Workflow: FM -> AM (if approved) or FM -> SCS (if rejected)
    """
    # 1. Authorization Check
    if not current_user or current_user.role != "FM":
        raise PermissionError("Only Financial Managers (FM) can review.")
        
    if request.owner != current_user:
        raise PermissionError("You are not the owner of this request.")
        
    # 2. REFACTORED: Add structured comment
    request.add_comment(user=current_user, message=comments)
        
    # 3. Process Logic
    if is_approved:
        am_manager = _find_user_or_raise(system, "AM")
        request.status = "Pending AM Review"
        request.owner = am_manager
        print(f"Request {request.request_id} approved by FM, sent to AM.")
    else:
        scs_officer = _find_user_or_raise(system, "SCS")
        request.status = "Rejected by FM"
        request.owner = scs_officer
        print(f"Request {request.request_id} rejected by FM, sent back to SCS.")

def am_decide(system, current_user, request, is_approved, comments):
    """
    Workflow: AM -> SCS (for finalization or to handle rejection)
    """
    # 1. Authorization Check
    if not current_user or current_user.role != "AM":
        raise PermissionError("Only Administration Managers (AM) can decide.")
        
    if request.owner != current_user:
        raise PermissionError("You are not the owner of this request.")
        
    # 2. REFACTORED: Add structured comment
    request.add_comment(user=current_user, message=comments)

    # Find the SCS officer to report back to
    scs_officer = _find_user_or_raise(system, "SCS")
    
    # 3. Process Logic
    if is_approved:
        request.status = "Approved - Pending Finalization"
        request.owner = scs_officer
        print(f"Request {request.request_id} APPROVED by AM, sent to SCS for finalization.")
    else:
        request.status = "REJECTED by AM"
        request.owner = scs_officer
        print(f"Request {request.request_id} REJECTED by AM, sent back to SCS.")
