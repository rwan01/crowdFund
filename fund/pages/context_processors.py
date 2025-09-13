# In context_processors.py
from .session_utils import is_user_logged_in, is_admin_logged_in

def auth_status(request):
    return {
        'user_logged_in': is_user_logged_in(request),
        'admin_logged_in': is_admin_logged_in(request),
    }