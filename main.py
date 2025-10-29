from storage import ensure_file, USERS_FILE, REQUESTS_FILE, ensure_files
from users import register_user, login_user
from finance import finance_menu

from constants import STAFF_REQ_FILE, EMPLOYEES_FILE, TASKS_FILE
from sep_cli import menu_hr, menu_manager, menu_subteam,cs_menu
from system import SEP_System
def main():
    print("=== SEP Management CLI ===")
    ensure_file(USERS_FILE)
    ensure_file(REQUESTS_FILE)
    ensure_files([STAFF_REQ_FILE, EMPLOYEES_FILE, TASKS_FILE])
    system = SEP_System()
    while True:
        print("\n1. Register\n2. Login\n3. Exit")
        choice = input("Choose an option: ").strip()
        if choice == "1":
            register_user()
        elif choice == "2":
            user = login_user()  
            role = user["role"] 
            if user:
                if role == "FM":
                    print("Finance menu selected.")
                    finance_menu(user) 
                elif role in ["PM", "SM"]:
                    print("Manager menu selected.")
                    menu_manager(user)  
                elif role == "HR":
                    print("HR menu selected.")
                    menu_hr(user)  # Call the function for HR
                elif role in ["LEAD", "MEMBER"]:
                    print("Staff menu selected.")
                    menu_subteam(user)  # Call the function for staff
                elif role in ["CS","SCS"]:
                    print("Customer service menu selected.")
                    cs_menu(system,user)
                else:
                    print("Unknown role!")

        elif choice == "3":
            print("Exiting program.")
            break
        else:
            print("Invalid option.")

if __name__ == "__main__":
    main()
