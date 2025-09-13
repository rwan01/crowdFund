from django.contrib.auth import get_user_model
from django.utils import timezone
from pages.models import Project

def set_admin_session(request, user):
    """Set admin session without affecting user session"""
    request.session['admin_user_id'] = str(user.id)
    request.session['admin_backend'] = 'pages.authentication_backends.AdminAuthenticationBackend'

def set_user_session(request, user):
    """Set user session without affecting admin session"""
    request.session['user_user_id'] = str(user.id)
    request.session['user_backend'] = 'pages.authentication_backends.UserAuthenticationBackend'

def get_admin_user(request):
    """Get admin user from session"""
    User = get_user_model()
    admin_user_id = request.session.get('admin_user_id')
    if admin_user_id:
        try:
            return User.objects.get(pk=admin_user_id)
        except User.DoesNotExist:
            return None
    return None

def get_user_user(request):
    """Get regular user from session"""
    User = get_user_model()
    user_user_id = request.session.get('user_user_id')
    if user_user_id:
        try:
            return User.objects.get(pk=user_user_id)
        except User.DoesNotExist:
            return None
    return None

def clear_admin_session(request):
    """Clear only admin session"""
    if 'admin_user_id' in request.session:
        del request.session['admin_user_id']
    if 'admin_backend' in request.session:
        del request.session['admin_backend']

def clear_user_session(request):
    """Clear only user session"""
    if 'user_user_id' in request.session:
        del request.session['user_user_id']
    if 'user_backend' in request.session:
        del request.session['user_backend']

def is_admin_logged_in(request):
    """Check if admin is logged in"""
    return get_admin_user(request) is not None

def is_user_logged_in(request):
    """Check if user is logged in"""
    return get_user_user(request) is not None



def update_project_statuses():
    """Update status for all projects based on current time"""
    now = timezone.now()
    
    # Mark projects that have ended as completed
    Project.objects.filter(
        end_date__lt=now, 
        status='active'  # Only update active projects
    ).update(status='completed')
    
    # Mark projects that haven't started yet as active
    Project.objects.filter(
        start_date__gt=now, 
        status__in=['active']
    ).update(status='active')