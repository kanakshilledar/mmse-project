from storage import load_data, save_data, ensure_files
from constants import TASKS_FILE, EMPLOYEES_FILE, TaskStatus

# Ensure files exist at startup
ensure_files(TASKS_FILE, EMPLOYEES_FILE)


# ---------- Subteam Management ----------

def list_subteams():
    employees = load_data(EMPLOYEES_FILE)
    teams = []
    for e in employees:
        if e["subteam"] != "" and e["subteam"] not in teams :
            teams.append(e["subteam"])
    return teams

def validate_subteam(name):
    teams = list_subteams()
    if not any(t.lower() == name.lower() for t in teams):
        raise ValueError(f"Subteam '{name}' not found.")
    return True


# ---------- Employee Management ----------

def list_employees():
    return load_data(EMPLOYEES_FILE)

def add_employee(name, role, subteam=""):
    if not name or not role:
        raise ValueError("Employee name and role required.")

    emps = load_data(EMPLOYEES_FILE)
    if any(name.lower() == e["name"].lower() for e in emps):
        raise ValueError(f"Employee '{name}' already exists.")

    eid = len(emps) + 1
    emps.append({"id": eid, "name": name, "role": role, "subteam": subteam})
    save_data(EMPLOYEES_FILE, emps)
    return eid


# ---------- Task Management ----------

def list_tasks():
    return load_data(TASKS_FILE)

def add_task(event_id, title, assigned_team):
    if not title.strip():
        raise ValueError("Task title required.")
    validate_subteam(assigned_team)

    tasks = load_data(TASKS_FILE)
    tid = len(tasks) + 1
    task = {
        "id": tid,
        "event_id": event_id,
        "title": title,
        "assigned_team": assigned_team,
        "status": TaskStatus.PENDING,
        "plan": "",
        "resources": "",
        "budget_request": 0,
        "comments": ""
    }
    tasks.append(task)
    save_data(TASKS_FILE, tasks)
    return tid

def get_task(task_id):
    tasks = list_tasks()
    return next((t for t in tasks if t["id"] == task_id or str(t["id"]) == str(task_id)), None)

def update_task_plan(task_id, plan_text, resources_text="", budget_request=0, comments=""):
    if not plan_text:
        raise ValueError("Plan text cannot be empty.")
    if budget_request and not isinstance(budget_request, (int, float)):
        raise ValueError("Budget must be numeric.")

    tasks = load_data(TASKS_FILE)
    found = False
    for task in tasks:
        if task["id"] == task_id or str(task["id"]) == str(task_id):
            task["plan"] = plan_text
            task["resources"] = resources_text
            task["budget_request"] = budget_request
            task["comments"] = comments
            found = True
            break
    if not found:
        raise ValueError("Task not found")
    save_data(TASKS_FILE, tasks)
    return True

def change_task_status(task_id, status):
    if not TaskStatus.is_valid(status):
        raise ValueError("Invalid status.")

    tasks = load_data(TASKS_FILE)
    found = False
    for task in tasks:
        if task["id"] == task_id or str(task["id"]) == str(task_id):
            task["status"] = status
            found = True
            break
    if not found:
        raise ValueError("Task not found")
    save_data(TASKS_FILE, tasks)
    return True

def list_tasks_for_user(user_name, role):
    all_tasks = list_tasks()
    employees = list_employees()
    user = next((e for e in employees if e["name"].lower() == user_name.lower()), None)
    if not user:
        return []

    if role in ("PM", "SM", "ADMIN"):
        return all_tasks
    if role in ["LEAD", "MEMBER"]:
        team = user.get("subteam", "")
        return [t for t in all_tasks if t["assigned_team"].lower() == team.lower()]
    return []
