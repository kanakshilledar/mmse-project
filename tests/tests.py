import os
import sys
import tempfile
import shutil

# Add the parent directory to sys.path to import modules from there
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import task_manager as tm
import hr_manager as hr
import storage as s


def setup():
    """Setup isolated temp directory and seed base data."""
    tempdir = tempfile.mkdtemp()
    cwd = os.getcwd()
    os.chdir(tempdir)

    # Redirect storage files
    tm.TASKS_FILE = "tasks.json"
    tm.EMPLOYEES_FILE = "employees.json"
    hr.STAFF_REQ_FILE = "staff_requests.json"

    s.ensure_files([tm.TASKS_FILE, tm.EMPLOYEES_FILE, hr.STAFF_REQ_FILE])

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

    print("\nAll tests completed successfully!")


if __name__ == "__main__":
    main()
