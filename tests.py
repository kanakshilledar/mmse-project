# tests.py
# Contains all test cases for the model logic.
# REFACTORED:
# 1. Updated assertions to work with the new Comment object
#    in EventRequest.comments_log.

from system import SEP_System
from models import User

def test_draft_handling_and_submission():
    """
    Verifies the "Save and Continue" draft logic.
    """
    print("\nRunning test: test_draft_handling_and_submission...")
    
    # 1. Setup
    system = SEP_System()
    system.add_user(User(username="sarah", role="CS"))
    system.add_user(User(username="janet", role="SCS"))
    system.login("sarah")
    client = system.create_client("Test Client")
    print("PASSED: Setup complete.")

    # 2. CS creates a blank draft
    draft_request = system.create_draft_request()
    assert draft_request.request_id == 1
    assert draft_request.status == "Draft"
    assert draft_request.owner.username == "sarah"
    print("PASSED: Blank draft created.")
    
    # 3. CS updates the draft with partial info
    system.update_draft_request(
        request_id=1,
        client_record_number=client.record_number
    )
    assert draft_request.client.name == "Test Client"
    assert draft_request.status == "Draft" # Still a draft
    print("PASSED: Draft partially updated.")
    
    # 4. CS tries to submit the incomplete draft
    try:
        system.initiate_event_request(request_id=1)
        assert False, "Test FAILED: Incomplete draft was submitted."
    except ValueError as e:
        assert "Cannot submit incomplete draft" in str(e)
        print("PASSED: Incomplete submission correctly blocked.")
        
    # 5. CS finishes filling out the draft
    system.update_draft_request(
        request_id=1,
        event_type="Workshop",
        date="2025-12-01"
    )
    assert draft_request.event_type == "Workshop"
    print("PASSED: Draft completed.")
    
    # 6. CS successfully submits the completed draft
    system.initiate_event_request(request_id=1)
    assert draft_request.status == "Pending SCS Review"
    assert draft_request.owner.username == "janet"
    print("PASSED: Completed draft submitted successfully.")
    print("Test finished successfully.")


def test_full_event_workflow():
    """
    UPDATED: Assertions for comments now check the Comment object.
    """
    print("\nRunning test: test_full_event_workflow...")

    # 1. Setup
    system = SEP_System()
    system.add_user(User(username="sarah", role="CS"))
    system.add_user(User(username="janet", role="SCS"))
    system.add_user(User(username="alice", role="FM"))
    system.add_user(User(username="mike", role="AM"))
    system.login("sarah")
    client = system.create_client("Test Client for Event")

    # 2. CS: Create, Update, and Submit Request
    draft = system.create_draft_request()
    system.update_draft_request(
        request_id=draft.request_id,
        client_record_number=client.record_number,
        event_type="Workshop",
        date="2025-12-01",
        preferences="Decorations"
    )
    system.initiate_event_request(request_id=draft.request_id)
    new_request = system.find_request_by_id(draft.request_id)
    print("PASSED: Event initiation (Owner: SCS).")

    # 3. SCS: Approve with a comment
    system.login("janet")
    scs_comment = "Looks good. Sending to finance."
    system.scs_review_request(request_id=1, is_approved=True, comments=scs_comment)

    # 4. Assert: Request moved to FM and comment was saved
    assert new_request.status == "Pending FM Review"
    assert new_request.owner.username == "alice"
    
    # --- THIS IS THE FIX ---
    assert len(new_request.comments_log) == 1
    assert new_request.comments_log[0].user.username == "janet"
    assert new_request.comments_log[0].message == scs_comment
    # --- END OF FIX ---
    
    print("PASSED: SCS approval (Owner: FM). Comment saved.")
    
    # 5. FM: Approve
    system.login("alice")
    system.fm_review_request(request_id=1, is_approved=True, comments="Budget approved.")
    
    # 6. Assert: Request is with AM
    assert new_request.status == "Pending AM Review"
    assert new_request.owner.username == "mike"
    assert len(new_request.comments_log) == 2 # Check new comment
    assert new_request.comments_log[1].user.username == "alice"
    print("PASSED: FM approval (Owner: AM).")
    
    # 7. AM: Approve
    system.login("mike")
    system.am_decide_request(request_id=1, is_approved=True, comments="Final approval from admin.")
    
    # 8. Assert: Request is back with SCS
    assert new_request.status == "Approved - Pending Finalization"
    assert new_request.owner.username == "janet"
    assert len(new_request.comments_log) == 3 # Check final comment
    assert new_request.comments_log[2].user.username == "mike"
    print("PASSED: AM approval (Owner: SCS).")
    
    print("Test finished successfully.")


def test_scs_rejection_workflow():
    """
    NEW TEST: Verifies the SCS rejection path (SCS -> CS)
    """
    print("\nRunning test: test_scs_rejection_workflow...")

    # 1. Setup
    system = SEP_System()
    system.add_user(User(username="sarah", role="CS"))
    system.add_user(User(username="janet", role="SCS"))
    system.login("sarah")
    client = system.create_client("Test Client")
    
    # 2. CS: Create and submit
    draft = system.create_draft_request()
    system.update_draft_request(draft.request_id, client.record_number, "Conference", "2026-01-01")
    system.initiate_event_request(draft.request_id)
    
    request = system.find_request_by_id(draft.request_id)
    assert request.owner.username == "janet"
    print("PASSED: Request submitted to SCS.")
    
    # 3. SCS: Log in and REJECT
    system.login("janet")
    rejection_comment = "Client budget is too low. Please follow up."
    system.scs_review_request(request_id=1, is_approved=False, comments=rejection_comment)
    
    # 4. Assert: Request is back with CS (the original creator)
    assert request.status == "Rejected by SCS"
    assert request.owner.username == "sarah" # 'sarah' is the original creator
    
    # --- THIS IS THE FIX ---
    assert len(request.comments_log) == 1
    assert request.comments_log[0].user.username == "janet"
    assert request.comments_log[0].message == rejection_comment
    # --- END OF FIX ---
    
    print("PASSED: Request rejected and sent back to CS with comments.")
    print("Test finished successfully.")


def test_client_management_workflow():
    """
    Test for Use Case: Client Record Management
    """
    print("\nRunning test: test_client_management_workflow...")
    
    # 1. Setup
    system = SEP_System()
    system.add_user(User(username="sarah", role="CS"))
    system.add_user(User(username="alice", role="FM"))
    
    # 2. Test: Search for non-existent client
    system.login("sarah")
    client = system.search_client_by_name("College of Music")
    assert client is None
    print("PASSED: Search for non-existent client returned None.")
    
    # 3. Test: Create a new client
    new_client = system.create_client("College of Music")
    assert new_client is not None
    
    # --- THIS IS THE FIX ---
    # Your system.py assigns a string "c1", not an integer 1
    assert new_client.record_number == "c1"
    # --- END OF FIX ---
    
    assert len(system.clients) == 1
    print("PASSED: Client creation successful.")
    
    # 4. Test: Search for existing client
    client = system.search_client_by_name("College of Music")
    assert client is not None
    assert client.name == "College of Music"
    print("PASSED: Search for existing client successful.")
    
    # 5. Test: Prevent duplication
    try:
        system.create_client("College of Music")
        assert False, "Test FAILED. Duplicate client was created."
    except ValueError as e:
        assert str(e) == "Client with name 'College of Music' already exists."
        print("PASSED: Duplication successfully prevented.")

    # 6. Test: Authorization (FM cannot create)
    system.login("alice")
    try:
        system.create_client("New Client Inc.")
        assert False, "Test FAILED. FM was able to create a client."
    except PermissionError as e:
        assert str(e) == "Only Customer Service officers can create new clients."
        print("PASSED: Authorization check for client creation successful.")
            
    print("Test finished successfully.")


# --- Run the tests ---
if __name__ == "__main__":
    test_draft_handling_and_submission()
    test_full_event_workflow()
    test_scs_rejection_workflow()
    test_client_management_workflow()

