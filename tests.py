"""
test_sep_team_based.py
Tests for team-based SEP system (task_manager + hr_manager + role-based CLI)
"""

import os
import unittest
import tempfile
import shutil

import task_manager as tm
import hr_manager as hr
import file_utils as f


class TestSEP(unittest.TestCase):

    def setUp(self):
        # Setup isolated temp directory
        self.tempdir = tempfile.mkdtemp()
        self.cwd = os.getcwd()
        os.chdir(self.tempdir)

        # Redirect storage files
        tm.TASKS_FILE = "tasks.txt"
        tm.SUBTEAMS_FILE = "subteams.txt"
        tm.EMPLOYEES_FILE = "employees.txt"

        hr.STAFF_REQ_FILE = "staff_requests.txt"

        f.ensure_files([tm.TASKS_FILE, tm.SUBTEAMS_FILE, tm.EMPLOYEES_FILE,
                        hr.STAFF_REQ_FILE])        

        # Seed base data
        tm.add_subteam("Filming", "Tobias")
        tm.add_subteam("Decoration", "Anna")
        tm.add_employee("Tobias", "subteam", "Filming")
        tm.add_employee("Anna", "subteam", "Decoration")
        tm.add_employee("Mikael", "manager", "")
        tm.add_employee("Sara", "hr", "")

    def tearDown(self):
        os.chdir(self.cwd)
        shutil.rmtree(self.tempdir)

    # ------------------------------------------------------------
    # Subteam / Employee Validations
    # ------------------------------------------------------------

    def test_add_duplicate_subteam_fails(self):
        with self.assertRaises(ValueError):
            tm.add_subteam("Filming", "SomeoneElse")

    def test_add_employee_duplicate_fails(self):
        with self.assertRaises(ValueError):
            tm.add_employee("Tobias", "subteam", "Filming")

    def test_validate_nonexistent_subteam_fails(self):
        with self.assertRaises(ValueError):
            tm.validate_subteam("Nonexistent")

    # ------------------------------------------------------------
    # Task creation & updates
    # ------------------------------------------------------------

    def test_add_task_and_update_plan(self):
        tid = tm.add_task("E100", "Record keynote", "Filming")
        task = tm.get_task(tid)
        self.assertEqual(task["assigned_team"], "Filming")

        tm.update_task_plan(tid, "Use drone camera", "Drone, battery", "500", "Need permit")
        updated = tm.get_task(tid)
        self.assertIn("drone", updated["plan"].lower())
        self.assertEqual(updated["budget_request"], "500")

    def test_cannot_assign_to_nonexistent_team(self):
        with self.assertRaises(ValueError):
            tm.add_task("E100", "Fake Task", "InvalidTeam")

    def test_change_status(self):
        tid = tm.add_task("E1", "Setup stage", "Decoration")
        tm.change_task_status(tid, "in_progress")
        task = tm.get_task(tid)
        self.assertEqual(task["status"], "in_progress")

    # ------------------------------------------------------------
    # Role-based filtering
    # ------------------------------------------------------------

    def test_manager_sees_all_tasks(self):
        tm.add_task("E1", "Film intro", "Filming")
        tm.add_task("E2", "Decorate hall", "Decoration")

        manager_view = tm.list_tasks_for_user("Mikael", "manager")
        self.assertEqual(len(manager_view), 2)

    def test_subteam_sees_only_their_team(self):
        tm.add_task("E1", "Film intro", "Filming")
        tm.add_task("E2", "Decorate hall", "Decoration")
        tm.add_task("E2", "Decorate entrance", "Decoration")

        filming_view = tm.list_tasks_for_user("Tobias", "subteam")
        decor_view = tm.list_tasks_for_user("Anna", "subteam")

        self.assertTrue(all(t["assigned_team"] == "Filming" for t in filming_view))
        self.assertTrue(all(t["assigned_team"] == "Decoration" for t in decor_view))
        self.assertNotEqual(len(filming_view), len(decor_view))

    def test_invalid_user_gets_no_tasks(self):
        result = tm.list_tasks_for_user("Ghost", "subteam")
        self.assertEqual(result, [])

    # ------------------------------------------------------------
    # HR workflow
    # ------------------------------------------------------------

    def test_hr_submit_review_and_publish(self):
        rid = hr.submit_staff_request("Production", "Camera Operator", "Shortage", "Mikael")
        req = hr.list_staff_requests()[0]
        self.assertEqual(req["role"], "Camera Operator")

        hr.review_request(rid, True, "Approved")
        updated = hr.list_staff_requests()[0]
        self.assertEqual(updated["status"], "approved")

    def test_hr_invalid_department_rejected(self):
        with self.assertRaises(ValueError):
            hr.submit_staff_request("FakeDept", "Stagehand", "Need staff", "Mikael")


if __name__ == "__main__":
    unittest.main()
