# event_workflow.py
# REFACTORED:
# 1. `update_draft_request` now accepts `client_expected_budget`.
# 2. `fm_review` now accepts `estimated_cost` and saves it.
# 3. FIXED: Changed object access (e.g., .username) to
#    dictionary access (e.g., ['username']) to work with file-based users.

import models
import datetime

from auth import requires_role # <-- Import our decorator

def _find_user_or_raise(system, role):
    """Helper to find a user or raise an error."""
    # This now correctly returns a user dictionary
    user = system.find_user_by_role(role)
    if not user:
        raise EnvironmentError(f"System Error: No user found for role '{role}'.")
    return user

@requires_role(allowed_roles="CS", error_message="Only Customer Service (CS) users can create drafts.")
def create_draft_request(system, current_user):
    """
    Creates a new, blank draft request.
    """
    # Role check is handled by decorator!
    new_request = models.EventRequest(initiated_by=current_user)
    system.add_request(new_request)
    
    # --- FIX 1 ---
    # Was: current_user.username
    # print(f"New draft request (ID: {new_request.request_id}) created by '{current_user['username']}'.")
    return new_request

@requires_role(allowed_roles="CS", error_message="Only Customer Service (CS) users can update drafts.")
def update_draft_request(system, current_user, request, client=None, event_type=None, date=None, preferences=None, client_expected_budget=None):
    """
    Updates fields on an existing draft request.
    """
    # Role check is handled by decorator!
        
    # This comparison should be fine, as both request.owner and current_user
    # are now dictionaries.
    if request.owner != current_user or request.status != "Draft":
        raise PermissionError("You cannot edit this request.")
        
    if client:
        request.client = client
    if event_type:
        request.event_type = event_type
    if date:
        request.date = date
    if preferences:
        request.preferences = preferences
    if client_expected_budget is not None:
        request.client_expected_budget = client_expected_budget
        
    # print(f"Draft request (ID: {request.request_id}) updated.")
    return request

@requires_role(allowed_roles="CS", error_message="Only Customer Service (CS) users can submit requests.")
def initiate_event_request(system, current_user, request):
    """
    Use Case: Submit a completed draft for approval.
    Workflow: CS -> SCS
    """
    # Role check is handled by decorator!
    if request.owner != current_user or request.status != "Draft":
        raise PermissionError("This request cannot be submitted.")

    if not request.client or not request.event_type or not request.date:
        raise ValueError("Cannot submit incomplete draft. Client, Event Type, and Date are required.")

    scs_officer = _find_user_or_raise(system, "SCS")
        
    request.status = "Pending SCS Review"
    request.owner = scs_officer
    
    # --- FIX 2 ---
    # Was: scs_officer.username
    # print(f"Event request (ID: {request.request_id}) submitted to '{scs_officer['username']}'.")
    return request

@requires_role(allowed_roles="SCS", error_message="Only SCS users can review.")
def scs_review(system, current_user, request, is_approved, comments):
    """
    Use Case: Request Review (SCS) / Request Forwarding
    Workflow: SCS -> FM (if approved) or SCS -> Closed (if rejected)
    """
    # Role check is handled by decorator!
    
    if request.owner != current_user:
        raise PermissionError("You are not the owner of this request.")
    
    request.add_comment(user=current_user, message=comments)
        
    if is_approved:
        fm_manager = _find_user_or_raise(system, "FM")
        request.status = "Pending FM Review"
        request.owner = fm_manager
        # print(f"Request {request.request_id} approved by SCS, sent to FM.")
    else:
        request.status = "Closed - Rejected"
        request.owner = current_user
        # print(f"Request {request.request_id} rejected by SCS and marked as closed.")

@requires_role(allowed_roles="FM", error_message="Only Financial Managers (FM) can review.")
def fm_review(system, current_user, request, is_approved, comments, estimated_cost=None):
    """
    Use Case: Budget Evaluation
    Workflow: FM -> AM (if approved) or FM -> SCS (if rejected)
    """
    # Role check is handled by decorator!
        
    if request.owner != current_user:
        raise PermissionError("You are not the owner of this request.")
        
    request.add_comment(user=current_user, message=comments)

    if estimated_cost is not None:
        request.fm_estimated_cost = estimated_cost
        # print(f"Estimated cost {estimated_cost} saved for Request {request.request_id}.")
        
    if is_approved:
        am_manager = _find_user_or_raise(system, "AM")
        request.status = "Pending AM Review"
        request.owner = am_manager
        # print(f"Request {request.request_id} approved by FM, sent to AM.")
    else:
        scs_officer = _find_user_or_raise(system, "SCS")
        request.status = "Rejected by FM"
        request.owner = scs_officer
        # print(f"Request {request.request_id} rejected by FM, sent back to SCS.")
    
@requires_role(allowed_roles="AM", error_message="Only Administration Managers (AM) can decide.")
def am_decide(system, current_user, request, is_approved, comments):
    """
    Workflow: AM -> SCS (for finalization or to handle rejection)
    """
    # Role check is handled by decorator!
        
    if request.owner != current_user:
        raise PermissionError("You are not the owner of this request.")
        
    scs_officer = _find_user_or_raise(system, "SCS")
    
    request.add_comment(user=current_user, message=comments)
        
    if is_approved:
        request.status = "Approved - Pending Finalization"
        request.owner = scs_officer
        # print(f"Request {request.request_id} APPROVED by AM, sent to SCS for finalization.")
    else:
        request.status = "REJECTED by AM"
        request.owner = scs_officer
        # print(f"Request {request.request_id} REJECTED by AM, sent back to SCS.")
