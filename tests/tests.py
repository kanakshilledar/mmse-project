import os
import sys
import tempfile
import shutil

# Add the parent directory to sys.path to import modules from there
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import task_manager as tm
import hr_manager as hr
import storage as s
from system import SEP_System
import users
import storage
def setup():
    """Setup isolated temp directory and seed base data."""
    tempdir = tempfile.mkdtemp()
    cwd = os.getcwd()
    os.chdir(tempdir)

    # Redirect storage files
    tm.TASKS_FILE = "tasks.json"
    tm.EMPLOYEES_FILE = "employees.json"
    hr.STAFF_REQ_FILE = "staff_requests.json"
    users.USERS_FILE = "users.json"

    s.ensure_files([tm.TASKS_FILE, tm.EMPLOYEES_FILE, hr.STAFF_REQ_FILE, users.USERS_FILE])

    # Seed base data
    tm.add_employee("Tobias", "LEAD", "Filming")
    tm.add_employee("Anna", "MEMBER", "Decoration")
    tm.add_employee("Mikael", "PM", "")
    tm.add_employee("Sara", "HR", "")

    return tempdir, cwd


def cleanup(tempdir, cwd):
    """Cleanup temporary files and revert working directory."""
    os.chdir(cwd)
    shutil.rmtree(tempdir)


def test_add_employee_duplicate_fails():
    setup_dir, cwd = setup()
    try:
        try:
            tm.add_employee("Tobias", "Lead", "Filming")
            assert False, "Expected ValueError"
        except ValueError:
            print("test_add_employee_duplicate_fails passed!")
    finally:
        cleanup(setup_dir, cwd)


def test_validate_nonexistent_subteam_fails():
    setup_dir, cwd = setup()
    try:
        try:
            tm.validate_subteam("Nonexistent")
            assert False, "Expected ValueError"
        except ValueError:
            print("test_validate_nonexistent_subteam_fails passed!")
    finally:
        cleanup(setup_dir, cwd)


def test_add_task_and_update_plan():
    setup_dir, cwd = setup()
    try:
        tid = tm.add_task("E100", "Record keynote", "Filming")
        task = tm.get_task(tid)
        assert task["assigned_team"] == "Filming"

        tm.update_task_plan(tid, "Use drone camera", "Drone, battery", 500, "Need permit")
        updated = tm.get_task(tid)
        assert "drone" in updated["plan"].lower()
        assert updated["budget_request"] == 500
        print("test_add_task_and_update_plan passed!")
    finally:
        cleanup(setup_dir, cwd)


def test_cannot_assign_to_nonexistent_team():
    setup_dir, cwd = setup()
    try:
        try:
            tm.add_task("E100", "Fake Task", "InvalidTeam")
            assert False, "Expected ValueError"
        except ValueError:
            print("test_cannot_assign_to_nonexistent_team passed!")
    finally:
        cleanup(setup_dir, cwd)


def test_change_status():
    setup_dir, cwd = setup()
    try:
        tid = tm.add_task("E1", "Setup stage", "Decoration")
        tm.change_task_status(tid, "in_progress")
        task = tm.get_task(tid)
        assert task["status"] == "in_progress"
        print("test_change_status passed!")
    finally:
        cleanup(setup_dir, cwd)


def test_manager_sees_all_tasks():
    setup_dir, cwd = setup()
    try:
        tm.add_task("E1", "Film intro", "Filming")
        tm.add_task("E2", "Decorate hall", "Decoration")

        manager_view = tm.list_tasks_for_user("Mikael", "PM")
        assert len(manager_view) == 2
        print("test_manager_sees_all_tasks passed!")
    finally:
        cleanup(setup_dir, cwd)


def test_subteam_sees_only_their_team():
    setup_dir, cwd = setup()
    try:
        tm.add_task("E1", "Film intro", "Filming")
        tm.add_task("E2", "Decorate hall", "Decoration")
        tm.add_task("E3", "Decorate entrance", "Decoration")

        filming_view = tm.list_tasks_for_user("Tobias", "LEAD")
        decor_view = tm.list_tasks_for_user("Anna", "MEMBER")

        assert all(t["assigned_team"] == "Filming" for t in filming_view)
        assert all(t["assigned_team"] == "Decoration" for t in decor_view)
        assert len(filming_view) == 1
        assert len(decor_view) == 2
        assert len(filming_view) != len(decor_view)
        print("test_subteam_sees_only_their_team passed!")
    finally:
        cleanup(setup_dir, cwd)


def test_invalid_user_gets_no_tasks():
    setup_dir, cwd = setup()
    try:
        result = tm.list_tasks_for_user("Ghost", "MEMBER")
        assert result == []
        print("test_invalid_user_gets_no_tasks passed!")
    finally:
        cleanup(setup_dir, cwd)

def test_hr_submit_review_and_publish():
    setup_dir, cwd = setup()
    try:
        rid = hr.submit_staff_request("Production", "Camera Operator", "Shortage", "Mikael")
        req = hr.list_staff_requests()[0]
        assert req["role_required"] == "Camera Operator"

        hr.review_request(rid, True, "Approved")
        updated = hr.list_staff_requests()[0]
        assert updated["status"] == "approved"
        print("test_hr_submit_review_and_publish passed!")
    finally:
        cleanup(setup_dir, cwd)


def test_hr_invalid_department_rejected():
    setup_dir, cwd = setup()
    try:
        try:
            hr.submit_staff_request("FakeDept", "Stagehand", "Need staff", "Mikael")
            assert False, "Expected ValueError"
        except ValueError:
            print("test_hr_invalid_department_rejected passed!")
    finally:
        cleanup(setup_dir, cwd)
# REFACTORED:
# 1. Tests updated to pass `client_expected_budget` during draft updates.
# 2. `test_full_event_workflow` now passes `estimated_cost`
#    during FM review and asserts it was saved.




def test_draft_handling_and_submission():
    """
    Verifies the "Save and Continue" draft logic.
    """
    # print("\nRunning test: test_draft_handling_and_submission...")
    setup_dir, cwd = setup() # <-- Applied setup
    try:
        # 1. Setup - *** THIS IS THE NEW PATTERN ***
        # We manually create user dictionaries...
        test_users = [
            {"id": 1, "username": "sarah", "password": "pw", "role": "CS", "subteam": "N/A"},
            {"id": 2, "username": "janet", "password": "pw", "role": "SCS", "subteam": "N/A"}
        ]
        # ...and save them to the file.
        seed_users_file(test_users)

        # Now we create the system. It will read from the file we just made.
        system = SEP_System()
        
        # We login as normal.
        system.login("sarah")
        client = system.create_client("Test Client")
        # print("PASSED: Setup complete.")

        # 2. CS creates a blank draft
        draft_request = system.create_draft_request()
        assert draft_request.request_id == 1
        assert draft_request.status == "Draft"
        # Test owner by checking the dictionary's username
        assert draft_request.owner['username'] == "sarah"
        # print("PASSED: Blank draft created.")
        
        # 3. CS updates the draft with partial info
        system.update_draft_request(
            request_id=1,
            client_record_number=client.record_number
        )
        assert draft_request.client.name == "Test Client"
        assert draft_request.status == "Draft"
        # print("PASSED: Draft partially updated.")
        
        # 4. CS tries to submit the incomplete draft
        try:
            system.initiate_event_request(request_id=1)
            assert False, "Test FAILED: Incomplete draft was submitted."
        except ValueError as e:
            assert "Cannot submit incomplete draft" in str(e)
            print("PASSED: Incomplete submission correctly blocked.")
            
        # 5. CS finishes filling out the draft (with new budget field)
        system.update_draft_request(
            request_id=1,
            event_type="Workshop",
            date="2025-12-01",
            client_expected_budget=50000
        )
        assert draft_request.event_type == "Workshop"
        assert draft_request.client_expected_budget == 50000
        # print("PASSED: Draft completed.")
        
        # 6. CS successfully submits the completed draft
        system.initiate_event_request(request_id=1)
        assert draft_request.status == "Pending SCS Review"
        # Test new owner by checking the dictionary's username
        assert draft_request.owner['username'] == "janet"
        # print("PASSED: Completed draft submitted successfully.")
        print("test_draft_handling_and_submission finished successfully.")
    
    finally:
        cleanup(setup_dir, cwd) # <-- Applied cleanup


def test_full_event_workflow():
    """
    Tests the full approval workflow: CS -> SCS -> FM -> AM -> SCS
    """
    # print("\nRunning test: test_full_event_workflow...")
    setup_dir, cwd = setup() # <-- Applied setup
    try:
        # 1. Setup
        test_users = [
            {"id": 1, "username": "sarah", "password": "pw", "role": "CS", "subteam": "N/A"},
            {"id": 2, "username": "janet", "password": "pw", "role": "SCS", "subteam": "N/A"},
            {"id": 3, "username": "alice", "password": "pw", "role": "FM", "subteam": "N/A"},
            {"id": 4, "username": "mike", "password": "pw", "role": "AM", "subteam": "N/A"}
        ]
        seed_users_file(test_users)
        
        system = SEP_System()
        system.login("sarah")
        client = system.create_client("Test Client for Event")

        # 2. CS: Create, Update, and Submit Request
        draft = system.create_draft_request()
        system.update_draft_request(
            request_id=draft.request_id,
            client_record_number=client.record_number,
            event_type="Workshop",
            date="2025-12-01",
            preferences="Decorations",
            client_expected_budget=100000 # NEW
        )
        system.initiate_event_request(request_id=draft.request_id)
        new_request = system.find_request_by_id(draft.request_id)
        # print("PASSED: Event initiation (Owner: SCS).")

        # 3. SCS: Approve with a comment
        system.login("janet")
        scs_comment = "Looks good. Sending to finance."
        system.scs_review_request(request_id=1, is_approved=True, comments=scs_comment)

        # 4. Assert: Request moved to FM and comment was saved
        assert new_request.status == "Pending FM Review"
        assert new_request.owner['username'] == "alice"
        assert len(new_request.comments_log) == 1
        assert new_request.comments_log[0].user['username'] == "janet"
        assert new_request.comments_log[0].message == scs_comment
        # print("PASSED: SCS approval (Owner: FM). Comment saved.")
        
        # 5. FM: Approve (with new estimated cost)
        system.login("alice")
        system.fm_review_request(
            request_id=1, 
            is_approved=True, 
            comments="Budget approved.",
            estimated_cost=95000 # NEW
        )
        
        # 6. Assert: Request is with AM
        assert new_request.status == "Pending AM Review"
        assert new_request.owner['username'] == "mike"
        assert len(new_request.comments_log) == 2
        assert new_request.comments_log[1].user['username'] == "alice"
        assert new_request.fm_estimated_cost == 95000 # NEW ASSERTION
        # print("PASSED: FM approval (Owner: AM). Cost saved.")
        
        # 7. AM: Approve
        system.login("mike")
        system.am_decide_request(request_id=1, is_approved=True, comments="Final approval from admin.")
        
        # 8. Assert: Request is back with SCS
        assert new_request.status == "Approved - Pending Finalization"
        assert new_request.owner['username'] == "janet"
        assert len(new_request.comments_log) == 3
        assert new_request.comments_log[2].user['username'] == "mike"
        # print("PASSED: AM approval (Owner: SCS).")
        
        print("test_full_event_workflow finished successfully.")
        
    finally:
        cleanup(setup_dir, cwd) # <-- Applied cleanup


def test_scs_rejection_workflow():
    """
    UPDATED: Verifies the SCS rejection path (SCS -> Closed)
    """
    # print("\nRunning test: test_scs_rejection_workflow...")
    setup_dir, cwd = setup() # <-- Applied setup
    try:
        # 1. Setup
        test_users = [
            {"id": 1, "username": "sarah", "password": "pw", "role": "CS", "subteam": "N/A"},
            {"id": 2, "username": "janet", "password": "pw", "role": "SCS", "subteam": "N/A"}
        ]
        seed_users_file(test_users)

        system = SEP_System()
        system.login("sarah")
        client = system.create_client("Test Client")
        
        # 2. CS: Create and submit
        draft = system.create_draft_request()
        system.update_draft_request(
            draft.request_id, 
            client.record_number, 
            "Conference", 
            "2026-01-01",
            client_expected_budget=1000 # NEW
        )
        system.initiate_event_request(draft.request_id)
        
        request = system.find_request_by_id(draft.request_id)
        assert request.owner['username'] == "janet"
        # print("PASSED: Request submitted to SCS.")
        
        # 3. SCS: Log in and REJECT
        system.login("janet")
        rejection_comment = "Client budget is too low. Marked as closed."
        system.scs_review_request(request_id=1, is_approved=False, comments=rejection_comment)
        
        # 4. Assert: Request is marked as closed and owned by SCS
        assert request.status == "Closed - Rejected"
        assert request.owner['username'] == "janet"
        
        assert len(request.comments_log) == 1
        assert request.comments_log[0].user['username'] == "janet"
        assert request.comments_log[0].message == rejection_comment
        # print("PASSED: Request rejected and marked as closed.")
        
        print("test_scs_rejection_workflow finished successfully.")
        
    finally:
        cleanup(setup_dir, cwd) # <-- Applied cleanup


def test_client_management_workflow():
    """
    Test for Use Case: Client Record Management
    """
    # print("\nRunning test: test_client_management_workflow...")
    setup_dir, cwd = setup() # <-- Applied setup
    try:
        # 1. Setup
        test_users = [
            {"id": 1, "username": "sarah", "password": "pw", "role": "CS", "subteam": "N/A"},
            {"id": 2, "username": "alice", "password": "pw", "role": "FM", "subteam": "N/A"}
        ]
        seed_users_file(test_users)
        
        system = SEP_System()
        
        # 2. Test: Search for non-existent client
        system.login("sarah")
        client = system.search_client_by_name("College of Music")
        assert client is None
        # print("PASSED: Search for non-existent client returned None.")
        
        # 3. Test: Create a new client
        new_client = system.create_client("College of Music")
        assert new_client is not None
        assert new_client.record_number == "c1"
        assert len(system.clients) == 1
        # print("PASSED: Client creation successful.")
        
        # 4. Test: Search for existing client
        client = system.search_client_by_name("College of Music")
        assert client is not None
        assert client.name == "College of Music"
        # print("PASSED: Search for existing client successful.")
        
        # 5. Test: Prevent duplication
        try:
            system.create_client("College of Music")
            assert False, "Test FAILED. Duplicate client was created."
        except ValueError as e:
            assert str(e) == "Client with name 'College of Music' already exists."
            # print("PASSED: Duplication successfully prevented.")

        # 6. Test: Authorization (FM cannot create)
        system.login("alice")
        try:
            system.create_client("New Client Inc.")
            assert False, "Test FAILED. FM was able to create a client."
        except PermissionError as e:
            assert str(e) == "Only Customer Service officers can create new clients."
            # print("PASSED: Authorization check for client creation successful.")
                
        print("test_client_management_workflow finished successfully.")
        
    finally:
        cleanup(setup_dir, cwd) # <-- Applied cleanup

def seed_users_file(user_list):
    """
    A helper function to write a list of user dictionaries
    to the 'users.json' file for testing.
    """
    # We use users.save_data to write to the file
    # 'users.USERS_FILE' was set during setup()
    storage.save_data(storage.USERS_FILE, user_list)
    # print(f"Seeded users.json with {len(user_list)} users.")


def main():
    test_add_employee_duplicate_fails()
    test_validate_nonexistent_subteam_fails()
    test_add_task_and_update_plan()
    test_cannot_assign_to_nonexistent_team()
    test_change_status()
    test_manager_sees_all_tasks()
    test_subteam_sees_only_their_team()
    test_invalid_user_gets_no_tasks()
    test_hr_submit_review_and_publish()
    test_hr_invalid_department_rejected()
    test_draft_handling_and_submission()
    test_full_event_workflow()
    test_scs_rejection_workflow()
    test_client_management_workflow()
    print("\nAll tests completed successfully!")


if __name__ == "__main__":
    main()


