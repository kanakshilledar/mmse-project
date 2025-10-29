"""
constants.py
Shared constants for the SEP Internal System.
"""

# File names
STAFF_REQ_FILE = "staff_requests.txt"
EMPLOYEES_FILE = "employees.txt"
TASKS_FILE = "tasks.txt"
SUBTEAMS_FILE = "subteams.txt"

# Departments
DEPARTMENTS = ["Production", "Services", "Administration", "Financial"]

# Task statuses
class TaskStatus:
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NEEDS_BUDGET = "needs_budget"
    
    @classmethod
    def all(cls):
        return [cls.PENDING, cls.IN_PROGRESS, cls.COMPLETED, cls.CANCELLED, cls.NEEDS_BUDGET]
    
    @classmethod
    def is_valid(cls, status):
        return status in cls.all()


# Staff request statuses
class RequestStatus:
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    
    @classmethod
    def all(cls):
        return [cls.PENDING, cls.APPROVED, cls.REJECTED]


