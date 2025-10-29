# auth.py
# NEW FILE: Contains reusable decorators for authentication.
# FIXED: Now uses dictionary access (e.g., current_user['role'])
#        to work with the new file-based user system.

from functools import wraps

def requires_role(allowed_roles, error_message):
    """
    Decorator factory that checks if a user has one of the allowed roles.
    """
    if not isinstance(allowed_roles, list):
        allowed_roles = [allowed_roles] # Allow passing a single string

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            
            # --- This is the authorization logic ---
            current_user = kwargs.get('current_user')
            if not current_user and len(args) > 1:
                current_user = args[1] # Assumes (system, current_user, ...)
            
            # --- FIX IS HERE ---
            # Changed 'current_user.role' to 'current_user['role']'
            if not current_user or current_user['role'] not in allowed_roles:
                raise PermissionError(error_message)
            # --- End of authorization logic ---
            
            # If authorized, run the original function
            return func(*args, **kwargs)
        return wrapper
    return decorator
