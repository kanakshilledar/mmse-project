
SEP CLI - Task Distribution & Staff Recruitment
===============================================

Files created:
 - task_manager.py       : module with task CRUD and subteam/employee helpers
 - hr_manager.py         : module for staff requests and job ads
 - sep_cli.py            : integrative CLI that uses the two modules
 - Data files (created at runtime in the same directory):
    - tasks.txt
    - subteams.txt
    - employees.txt
    - staff_requests.txt
    - job_ads.txt

How to run:
 1. Download the three .py files to the same directory.
 2. Run: python sep_cli.py
 3. Use menu options to create tasks, submit recruitment requests, and act as HR.

Notes:
 - Storage is plain text pipe-separated files (|) suitable for a homework/demo prototype.
 - The CLI is intentionally simple to cover the user stories for Task Distribution and Staff Recruitment.
