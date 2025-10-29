"""
sep_cli.py
CLI for SEP Internal System
"""

from task_manager import list_subteams, list_employees, add_task, list_tasks_for_user, update_task_plan, change_task_status
from hr_manager import submit_staff_request, list_staff_requests, review_request
from file_utils import read_lines, write_lines, next_id, ensure_files
from constants import STAFF_REQ_FILE, EMPLOYEES_FILE, TASKS_FILE, SUBTEAMS_FILE 

#Helper
def print_task_details(task):
    print(f"\n[{task['id']}] {task['title']}")
    print(f"  Event ID: {task['event_id']}")
    print(f"  Assigned Team: {task['assigned_team']}")
    print(f"  Status: {task['status']}")
    if task.get("plan"):
        print(f"  Plan: {task['plan']}")
    if task.get("resources"):
        print(f"  Resources: {task['resources']}")
    if task.get("budget_request") and task["budget_request"] != "0":
        print(f"  Budget: {task['budget_request']}")
    if task.get("comments"):
        print(f"  Comments: {task['comments']}")


def login():
    employees = list_employees()
    name = input("Enter your name: ").strip()
    role = input("Enter your role (manager/subteam/hr/admin): ").strip().lower()
    match = next((e for e in employees if e["name"].lower() == name.lower() and role in e["role"].lower()), None)
    if not match:
        print("Invalid credentials or role mismatch.")
        return None, None
    print(f"Welcome, {name} ({role.title()}) — Subteam: {match.get('subteam', 'N/A')}")
    return name, role


#Role based menus
def menu_manager(user):
    while True:
        print("\n=== MANAGER MENU ===")
        print("1) View All Tasks")
        print("2) Create Task")
        print("3) Change Task Status")
        print("4) Submit Staff Request")
        print("5) View Staff Requests")
        print("0) Logout")
        c = input("Choice: ").strip()
        try:
            if c == "1":
                tasks = list_tasks_for_user(user, "manager")
                if not tasks:
                    print("No tasks available.")
                else:
                    for t in tasks:
                        print_task_details(t)
            elif c == "2":
                event = input("Event ID: ")
                title = input("Task Title: ")
                print("Available subteams:")
                for s in list_subteams():
                    print(f" - {s['name']} (Lead: {s['lead']})")
                team = input("Assign to subteam: ").strip()
                tid = add_task(event, title, team)
                print(f"Task {tid} created and assigned to {team}.")
            elif c == "3":
                tid = input("Task ID: ")
                st = input("New status: ")
                change_task_status(tid, st)
                print("Status updated.")
            elif c == "4":
                dept = input("Department: ")
                role = input("Role required: ")
                reason = input("Reason: ")
                submit_staff_request(dept, role, reason, user)
                print("Staff request submitted.")
            elif c == "5":
                for r in list_staff_requests():
                    if r['requested_by'] == user:
                        print(f"[{r['id']}] {r['department']} -> {r['role']} ({r['status']})")
            elif c == "0":
                break
        except Exception as e:
            print("Error:", e)


def menu_subteam(user):
    while True:
        print("\n=== SUBTEAM MENU ===")
        print("1) View My Team’s Tasks")
        print("2) Update Task Plan")
        print("3) Mark Task Complete")
        print("0) Logout")
        c = input("Choice: ").strip()
        try:
            if c == "1":
                tasks = list_tasks_for_user(user, "subteam")
                if not tasks:
                    print("No tasks assigned to your team.")
                else:
                    for t in tasks:
                        print_task_details(t)
            elif c == "2":
                tid = input("Task ID: ")
                plan = input("Plan: ")
                resources = input("Resources: ")
                budget = input("Budget: ")
                comments = input("Comments: ")
                update_task_plan(tid, plan, resources, budget, comments)
                print("Plan updated.")
            elif c == "3":
                tid = input("Task ID: ")
                change_task_status(tid, "completed")
                print("Task marked complete.")
            elif c == "0":
                break
        except Exception as e:
            print("Error:", e)


def menu_hr(user):
    while True:
        print("\n=== HR MENU ===")
        print("1) View Staff Requests")
        print("2) Review Request")
        print("0) Logout")
        c = input("Choice: ").strip()
        try:
            if c == "1":
                for r in list_staff_requests():
                    print(f"[{r['id']}] {r['department']} -> {r['role']} ({r['status']})")
            elif c == "2":
                rid = input("Request ID: ")
                approve = input("Approve (y/n)? ").lower() == "y"
                comment = input("Comment: ")
                review_request(rid, approve, comment)
                print("Request reviewed.")
            elif c == "0":
                break
        except Exception as e:
            print("Error:", e)


def main():
    ensure_files([STAFF_REQ_FILE, EMPLOYEES_FILE, TASKS_FILE, SUBTEAMS_FILE])
    user, role = login()
    if not user:
        return
    if role == "manager":
        menu_manager(user)
    elif role == "subteam":
        menu_subteam(user)
    elif role == "hr":
        menu_hr(user)
    else:
        print("No menu defined for this role.")


if __name__ == "__main__":
    main()
