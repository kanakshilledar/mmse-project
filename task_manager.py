"""
task_manager.py
SEP Task Management (team-based assignment)

Data files and schema:
- tasks.txt        id|event_id|title|assigned_team|status|plan|resources|budget_request|comments
- subteams.txt     id|name|lead
- employees.txt    id|name|role|subteam
"""

import os
from file_utils import read_lines, write_lines, next_id
from constants import TASKS_FILE, SUBTEAMS_FILE, EMPLOYEES_FILE, TaskStatus


#Subteam management
def list_subteams():
    lines = read_lines(SUBTEAMS_FILE)
    teams = []
    for l in lines:
        tid, name, lead = l.split("|")
        teams.append({"id": tid, "name": name, "lead": lead})
    return teams

def add_subteam(name, lead):
    if not name or not lead:
        raise ValueError("Subteam name and lead required.")
    lines = read_lines(SUBTEAMS_FILE)
    if any(name.lower() == l.split("|")[1].lower() for l in lines):
        raise ValueError("Subteam already exists.")
    nid = next_id(lines)
    lines.append("|".join([nid, name, lead]))
    write_lines(SUBTEAMS_FILE, lines)
    return nid

def list_employees():
    lines = read_lines(EMPLOYEES_FILE)
    emps = []
    for l in lines:
        parts = l.split("|")
        if len(parts) < 4:  # backward compatibility
            parts += [""]
        eid, name, role, subteam = parts[:4]
        emps.append({"id": eid, "name": name, "role": role, "subteam": subteam})
    return emps

def add_employee(name, role, subteam):
    if not name or not role:
        raise ValueError("Employee name and role required.")
    if subteam:
        validate_subteam(subteam)
    lines = read_lines(EMPLOYEES_FILE)
    if any(name.lower() == l.split("|")[1].lower() for l in lines):
        raise ValueError(f"Employee '{name}' already exists.")
    nid = next_id(lines)
    lines.append("|".join([nid, name, role, subteam]))
    write_lines(EMPLOYEES_FILE, lines)
    return nid

def validate_subteam(name):
    teams = list_subteams()
    if not any(t["name"].lower() == name.lower() for t in teams):
        raise ValueError(f"Subteam '{name}' not found.")
    return True


#task management
def list_tasks():
    lines = read_lines(TASKS_FILE)
    tasks = []
    for l in lines:
        parts = l.split("|")
        if len(parts) < 9: 
            continue
        task = dict(
            id=parts[0], event_id=parts[1], title=parts[2],
            assigned_team=parts[3], status=parts[4], plan=parts[5],
            resources=parts[6], budget_request=parts[7], comments=parts[8]
        )
        tasks.append(task)
    return tasks

def add_task(event_id, title, assigned_team):
    if not title.strip():
        raise ValueError("Task title required.")
    validate_subteam(assigned_team)
    lines = read_lines(TASKS_FILE)
    nid = next_id(lines)
    line = "|".join([nid, event_id, title, assigned_team, TaskStatus.PENDING, "", "", "", ""])
    lines.append(line)
    write_lines(TASKS_FILE, lines)
    return nid

def get_task(task_id):
    for t in list_tasks():
        if t["id"] == str(task_id):
            return t
    return None

def update_task_plan(task_id, plan_text, resources_text="", budget_request="", comments=""):
    if not plan_text:
        raise ValueError("Plan text cannot be empty.")
    if budget_request and not budget_request.replace(".", "").isdigit():
        raise ValueError("Budget must be numeric.")
    task = get_task(task_id)
    if not task:
        raise ValueError("Task not found.")

    lines = read_lines(TASKS_FILE)
    new_lines = []
    for l in lines:
        parts = l.split("|")
        if parts[0] == str(task_id):
            parts[5] = plan_text.replace("|", "/")
            parts[6] = resources_text.replace("|", "/")
            parts[7] = budget_request
            parts[8] = comments.replace("|", "/")
        new_lines.append("|".join(parts))
    write_lines(TASKS_FILE, new_lines)
    return True

def change_task_status(task_id, status):
    if not TaskStatus.is_valid(status):
        raise ValueError("Invalid status.")
    task = get_task(task_id)
    if not task:
        raise ValueError("Task not found.")

    lines = read_lines(TASKS_FILE)
    new_lines = []
    for l in lines:
        parts = l.split("|")
        if parts[0] == str(task_id):
            parts[4] = status
        new_lines.append("|".join(parts))
    write_lines(TASKS_FILE, new_lines)
    return True

def list_tasks_for_user(user_name, role):
    all_tasks = list_tasks()
    employees = list_employees()
    user = next((e for e in employees if e["name"].lower() == user_name.lower()), None)
    if not user:
        return []

    if role in ("manager", "admin"):
        return all_tasks
    if role == "subteam":
        team = user.get("subteam", "")
        return [t for t in all_tasks if t["assigned_team"].lower() == team.lower()]
    return []
