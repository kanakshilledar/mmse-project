from storage import ensure_file, USERS_FILE, REQUESTS_FILE
from users import register_user, login_user
from finance import finance_menu

def main():
    print("=== SEP Management CLI ===")
    ensure_file(USERS_FILE)
    ensure_file(REQUESTS_FILE)

    while True:
        print("\n1. Register\n2. Login\n3. Exit")
        choice = input("Choose an option: ").strip()
        if choice == "1":
            register_user()
        elif choice == "2":
            user = login_user()
            if user:
                finance_menu(user)
        elif choice == "3":
            print("Exiting program.")
            break
        else:
            print("Invalid option.")

if __name__ == "__main__":
    main()
