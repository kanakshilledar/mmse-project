# tests.py
# UPDATED: Added a new test for Client Management.

from system import SEP_System
from models import User
def test_full_event_workflow():
    """
    Test for Use Case: Full Event Workflow
    CS -> SCS -> FM -> AM -> SCS
    """
    print("\nRunning test: test_full_event_workflow...")

    # 1. Setup System and Users
    system = SEP_System()
    system.add_user(User(username="sarah", role="CS"))   # Customer Service
    system.add_user(User(username="janet", role="SCS"))  # Senior Customer Service
    system.add_user(User(username="alice", role="FM"))   # Financial Manager
    system.add_user(User(username="mike", role="AM"))    # Administration Manager

    # 2. CS: Log in and create the client
    system.login("sarah")
    new_client = system.create_client("Test Client for Event")
    print("PASSED: Client created.")

    # 3. CS: Initiate the request
    system.initiate_event_request(
        client_record_number=new_client.record_number,
        event_type="Workshop",
        date="2025-12-01",
        preferences="Decorations"
    )
    
    # 4. Assert: Request is with SCS
    new_request = system.event_requests[0]
    assert new_request.status == "Pending SCS Review"
    assert new_request.owner.username == "janet" 
    print("PASSED: Event initiation (Owner: SCS).")

    # 5. SCS: Log in and approve
    system.login("janet")
    system.scs_review_request(request_id=1, is_approved=True)

    # 6. Assert: Request is with FM
    assert new_request.status == "Pending FM Review"
    assert new_request.owner.username == "alice"
    print("PASSED: SCS approval (Owner: FM).")
    
    # 7. FM: Log in and approve
    system.login("alice")
    system.fm_review_request(request_id=1, is_approved=True)
    
    # 8. Assert: Request is with AM
    assert new_request.status == "Pending AM Review"
    assert new_request.owner.username == "mike"
    print("PASSED: FM approval (Owner: AM).")
    
    # 9. AM: Log in and approve
    system.login("mike")
    system.am_decide_request(request_id=1, is_approved=True)
    
    # 10. Assert: Request is back with SCS for finalization
    assert new_request.status == "Approved - Pending Finalization"
    assert new_request.owner.username == "janet"
    print("PASSED: AM approval (Owner: SCS).")
    
    print("Test finished successfully.")
    
def test_client_management_workflow():
    """
    Test for Use Case: Client Record Management
    """
    print("\nRunning test: test_client_management_workflow...")
    
    # 1. Setup
    system = SEP_System()
    system.add_user(User(username="sarah", role="CS"))
    system.add_user(User(username="alice", role="FM")) # FM can search, not create
    
    # 2. Test: Search for non-existent client
    system.login("sarah")
    client = system.search_client_by_name("College of Music")
    assert client is None
    print("PASSED: Search for non-existent client returned None.")
    
    # 3. Test: Create a new client
    new_client = system.create_client("College of Music")
    assert new_client is not None
    assert new_client.record_number == "c1"
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
        # If this line is reached, the test failed
        assert False, "Test FAILED. Duplicate client was created."
    except ValueError as e:
        assert str(e) == "Client with name 'College of Music' already exists."
        print("PASSED: Duplication successfully prevented.")

    # 6. Test: Authorization (FM cannot create)
    system.login("alice") # FM can search[cite: 368], but not create
    try:
        system.create_client("New Client Inc.")
        assert False, "Test FAILED. FM was able to create a client."
    except PermissionError as e:
        assert str(e) == "Only Customer Service officers can create new clients."
        print("PASSED: Authorization check for client creation successful.")
        
    print("Test finished successfully.")


# --- Run the tests ---

if __name__ == "__main__":
    # You can now run the full workflow test
    # test_full_event_workflow()
    test_client_management_workflow()