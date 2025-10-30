"""
sep_cli.py
CLI for SEP
"""

from finance import create_financial_request, view_my_requests
from task_manager import (
    list_subteams, list_employees, add_task, print_task_details,
    list_tasks_for_user, update_task_plan, change_task_status
)
from hr_manager import submit_staff_request, list_staff_requests, review_request
from users import change_password

import customer_service
import clients
import event_requests


# ─────────────────────────────────────────────
# MANAGER MENU (PM / SM)
# ─────────────────────────────────────────────
def menu_manager(user):
    while True:
        print("\n=== MANAGER MENU ===")
        print("1) View All Tasks")
        print("2) Create Task")
        print("3) Change Task Status")
        print("4) Submit Staff Request")
        print("5) View My Staff Requests")
        print("6) Create Financial Request")
        print("7) View My Financial Requests")
        print("8) Change Password")
        print("0) Logout")
        c = input("Choice: ").strip()

        try:
            if c == "1":
                tasks = list_tasks_for_user(user["username"], "PM")
                for t in tasks:
                    print_task_details(t)

            elif c == "2":
                event = input("Event ID: ")
                title = input("Task Title: ")
                print("Available subteams:")
                for s_ in list_subteams():
                    print(f" - {s_['name']} (Lead: {s_['lead']})")

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
                role_req = input("Role required: ")
                reason = input("Reason: ")
                submit_staff_request(dept, role_req, reason, user["username"])
                print("Staff request submitted.")

            elif c == "5":
                for r in list_staff_requests():
                    if r["requested_by"] == user:
                        print(f"[{r['id']}] {r['department']} -> {r['role_required']} ({r['status']})")

            elif c == "6":
                create_financial_request(user)

            elif c == "7":
                view_my_requests(user)

            elif c == "8":
                change_password(user)

            elif c == "0":
                break

        except Exception as e:
            print("Error:", e)


# ─────────────────────────────────────────────
# SUBTEAM MENU
# ─────────────────────────────────────────────
def menu_subteam(user):
    while True:
        print("\n=== SUBTEAM MENU ===")
        print("1) View My Team’s Tasks")
        print("2) Update Task Plan")
        print("3) Mark Task Complete")
        print("4) Change Password")
        print("0) Logout")
        c = input("Choice: ").strip()

        try:
            if c == "1":
                tasks = list_tasks_for_user(user["username"], "LEAD")
                for t in tasks:
                    print_task_details(t)

            elif c == "2":
                tid = input("Task ID: ")
                plan = input("Plan: ")
                resources = input("Resources: ")
                budget = int(input("Budget: "))
                comments = input("Comments: ")
                update_task_plan(tid, plan, resources, budget, comments)
                print("Plan updated.")

            elif c == "3":
                tid = input("Task ID: ")
                change_task_status(tid, "completed")
                print("Task marked complete.")

            elif c == "4":
                change_password(user)

            elif c == "0":
                break

        except Exception as e:
            print("Error:", e)


# ─────────────────────────────────────────────
# HR MENU
# ─────────────────────────────────────────────
def menu_hr(user):
    while True:
        print("\n=== HR MENU ===")
        print("1) View Staff Requests")
        print("2) Review Request")
        print("3) List employees")
        print("4) Change Password")
        print("0) Logout")
        c = input("Choice: ").strip()

        try:
            if c == "1":
                for r in list_staff_requests():
                    print(f"[{r['id']}] {r['department']} -> {r['role_required']} ({r['status']})")

            elif c == "2":
                rid = int(input("Request ID: "))
                approve = input("Approve (y/n)? ").lower() == "y"
                comment = input("HR Comment: ")
                review_request(rid, approve, comment)
                print("Request reviewed.")

            elif c == "3":
                print(list_employees())

            elif c == "4":
                change_password(user)

            elif c == "0":
                break

        except Exception as e:
            print("Error:", e)


# ─────────────────────────────────────────────
# CUSTOMER SERVICE (CS)
# ─────────────────────────────────────────────
def cs_menu(user):
    print(f"\n--- Welcome, {user['username']} (CS) ---")

    while True:
        print("\nCS Menu:")
        print("1) Create Client")
        print("2) Search Client")
        print("3) Create Event Draft")
        print("4) Update My Drafts")
        print("5) Submit Draft to SCS")
        print("0) Logout")

        c = input("Choice: ").strip()

        try:
            if c == "1":
                name = customer_service._get_input("Client name")
                clients.create_client(name)

            elif c == "2":
                name = customer_service._get_input("Client name")
                client = clients.find_client_by_name(name)
                print(client or "Not found.")

            elif c == "3":
                customer_service.create_draft(user)

            elif c == "4":
                customer_service.update_draft(user)

            elif c == "5":
                customer_service.submit_draft(user)

            elif c == "0":
                break

        except Exception as e:
            print("Error:", e)


# ─────────────────────────────────────────────
# SENIOR CS (SCS)
# ─────────────────────────────────────────────
def scs_menu(user):
    while True:
        print("\n=== SCS MENU ===")
        print("1) View Pending Requests")
        print("2) Review Request")
        print("0) Logout")

        c = input("Choice: ").strip()
        try:
            if c == "1":
                requests = event_requests.get_scs_queue(user)
                if not requests:
                    print("No requests.")
                else:
                    print("\n--- PENDING_SCS ---")
                    for r in requests:
                        print(f"ID: {r['id']} | Amount: {r['amount']} | Reason: {r['reason']}")
            
            elif c == "2":
                rid = input("Request ID: ").strip()
                req = event_requests.find_request_by_id(rid)
                if not req:
                    print("Not found.")
                    continue

                approve = input("Approve? (y/n): ").lower() == "y"
                note = input("Comment: ")

                event_requests.scs_review(rid, user, approve, note)
                print("Reviewed.")

            elif c == "0":
                break

            else:
                print("Invalid choice.")

        except Exception as e:
            print("Error:", e)



# ─────────────────────────────────────────────
# ADMIN MANAGER (AM)
# ─────────────────────────────────────────────
def am_menu(user):
    print(f"\n--- Welcome, {user['username']} (AM) ---")

    while True:
        print("\nAM Menu:")
        print("1) Final decision → (approve → SCS / reject → SCS)")
        print("0) Logout")

        c = input("Choice: ").strip()

        try:
            if c == "1":
                customer_service.am_review(user)

            elif c == "0":
                break

        except Exception as e:
            print("Error:", e)
