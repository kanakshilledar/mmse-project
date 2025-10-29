"""
sep_cli.py
CLI for SEP
"""

from finance import create_financial_request, view_my_requests
from task_manager import (list_subteams, list_employees, add_task, print_task_details,
                          list_tasks_for_user, update_task_plan, change_task_status)
from hr_manager import submit_staff_request, list_staff_requests, review_request
from users import change_password
import event_workflow,client_workflow
import customer_service
import clients
import event_requests
import cs_manager
# Role based menus
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
                if not tasks:
                    print("No tasks available.")
                else:
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
                    if r['requested_by'] == user:
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
                if not tasks:
                    print("No tasks assigned to your team.")
                else:
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


def cs_menu(system,user):
    """
    Main menu loop for Customer Service users.
    """
    print(f"\n--- Welcome, {user['username']} (Customer Service) ---")
    
    while True:
        print("\nCustomer Service Menu:")
        print("1. Create New Client")
        print("2. Search for Client")
        print("3. Create New Event Draft")
        print("4. View & Update My Drafts")
        print("5. Submit Draft for Review")
        print("0. Logout")
        
        choice = input("Enter your choice: ").strip()
        
        try:
            if choice == '1':
                # --- Create Client ---
                client_name = customer_service._get_input("Enter new client's name")
                if client_name:
                    clients.create_client(client_name)
                
            elif choice == '2':
                # --- Search Client ---
                client_name = customer_service._get_input("Enter client's name to search")
                if client_name:
                    client = clients.find_client_by_name(client_name)
                    if client:
                        print("\n--- Client Found ---")
                        print(f"  Name: {client['name']}")
                        print(f"  ID: {client['record_number']}")
                        print(f"  Event History IDs: {client['event_history_ids']}")
                    else:
                        print("No client found with that name.")
            
            elif choice == '3':
                # --- Create Draft ---
                cs_manager._handle_create_request(system, user)
                print("New blank draft created.")
                
            # elif choice == '4':
            #     # --- Update Draft ---
            #     customer_service._update_draft(system, user)
                
            # elif choice == '5':
            #     # --- Submit Draft ---
            #     customer_service._view_my_drafts(system, user)
            #     req_id_str = customer_service._get_input("Enter the ID of the draft you want to SUBMIT (or leave blank to cancel)")
            #     if req_id_str:
            #         request_id = int(req_id_str)
            #         request = system.find_request_by_id(request_id)
                    
            #         if (not request or 
            #             request.status != "Draft" or 
            #             request.owner['username'] != user['username']):
            #             print("Error: Request not found or you are not the owner of this draft.")
            #         else:
            #             event_requests.initiate_event_request(system, user, request)
            #             print(f"Draft {request_id} submitted for review!")
                
            elif choice == '0':
                # --- Logout ---
                print(f"Logging out {user['username']}...")
                break
                
            else:
                print("Invalid choice, please try again.")
        
        except (ValueError, PermissionError) as e:
            print(f"\nError: {e}\n")
        except Exception as e:
            # Catch unexpected errors
            print(f"\nAn unexpected error occurred: {e}\n")
