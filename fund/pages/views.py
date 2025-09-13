from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden
from django.utils import timezone
from django.db.models import Sum, Avg
from django.db import models
from django.urls import reverse
from .models import Project, Tag
from django.core.exceptions import ValidationError
from django import forms
from django.core.paginator import Paginator
from django.db.models import Sum, Count, Q
from django.db.models.functions import Coalesce
from decimal import Decimal
# from .services import get_user_user, is_user_logged_in
from pages.session_utils import update_project_statuses
  


# Make sure all your models are imported
from .models import CustomUser, ActivationToken, Project, Donation, PasswordResetToken, Comment, Rating, ProjectPicture, ReportedProject, ReportedComment
from .forms import CustomUserCreationForm, UserProfileEditForm, ProjectCreationForm, AdminAuthenticationForm, UserAuthenticationForm
from .tokens import TokenService
from .session_utils import set_admin_session, set_user_session, clear_admin_session, clear_user_session, get_admin_user, get_user_user, is_admin_logged_in, is_user_logged_in




# Helper function to check if user is admin
def is_admin(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            
            # Send only activation link
            TokenService.send_activation_email(user, request)
            
            messages.success(request, 'Registration successful! Check your email for the activation link.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'auth/register.html', {'form': form})

def activate_account(request, token):
    """Activate account using token link"""
    user, error_message = TokenService.validate_activation_token(token)
    
    if error_message:
        messages.error(request, error_message)
        return redirect('register')
    
    user.is_active = True
    user.save()
    
    # Delete the used token
    ActivationToken.objects.filter(user=user).delete()
    
    messages.success(request, 'Your account has been activated successfully! You can now login.')
    return redirect('login')


def admin_login_view(request):
    # If already logged in as admin, redirect to custom admin dashboard
    if is_admin_logged_in(request):
        return redirect('admin_dashboard')

    if request.method == 'POST':
        form = AdminAuthenticationForm(request, data=request.POST)

        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            # Use only our custom AdminAuthenticationBackend
            user = authenticate(
                request,
                username=email,
                password=password,
                backend='pages.authentication_backends.AdminAuthenticationBackend'
            )

            if user is not None:
                if user.is_active and (user.is_staff or user.is_superuser):
                    # Store in custom admin session (separate from request.user)
                    set_admin_session(request, user)
                    messages.success(request, f'Welcome back, {user.first_name}! (Admin)')
                    return redirect('admin_dashboard')
                else:
                    messages.error(request, 'Your account is not authorized for admin access.')
            else:
                messages.error(request, 'Invalid email or password for admin access.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AdminAuthenticationForm()

    return render(request, 'auth/admin_login.html', {'form': form})


def admin_logout_view(request):
    # Clear only the custom admin session
    clear_admin_session(request)
    messages.success(request, 'You have been logged out from admin successfully.')
    return redirect('admin_login')


def user_login_view(request):
    # If user is already logged in, redirect to profile
    if is_user_logged_in(request):
        return redirect('profile')
    
    # Check for social auth errors
    if request.GET.get('error') == 'access_denied':
        messages.error(request, 'Facebook login was cancelled.')
    
    if request.method == 'POST':
        form = UserAuthenticationForm(request, data=request.POST)
        
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            # Authenticate using user backend
            user = authenticate(
                request, 
                username=email, 
                password=password,
                backend='pages.authentication_backends.UserAuthenticationBackend'
            )
            
            if user is not None:
                if user.is_active and not user.is_staff and not user.is_superuser:
                    # Set user session WITHOUT affecting admin session
                    set_user_session(request, user)
                    messages.success(request, f'Welcome back, {user.first_name}!')
                    return redirect('profile')
                else:
                    messages.error(request, 'Your account is not active. Please check your email for activation link.')
            else:
                messages.error(request, 'Invalid email or password.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserAuthenticationForm()
    
    return render(request, 'auth/login.html', {'form': form})

def user_logout_view(request):
    clear_user_session(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

def logout_all_view(request):
    clear_admin_session(request)
    clear_user_session(request)
    messages.success(request, 'You have been logged out from all sessions successfully.')
    return redirect('home')

def admin_dashboard(request):
    # Only allow admin users to access this view
    admin_user = get_admin_user(request)
    if not admin_user or not (admin_user.is_staff or admin_user.is_superuser):
        messages.error(request, "You don't have permission to access this page.")
        return redirect('admin_login')
    
    # Admin dashboard logic
    total_projects = Project.objects.count()
    total_users = CustomUser.objects.count()
    total_donations = Donation.objects.aggregate(total=Sum('amount'))['total'] or 0
    recent_projects = Project.objects.order_by('-created_at')[:5]
    
    context = {
        'total_projects': total_projects,
        'total_users': total_users,
        'total_donations': total_donations,
        'recent_projects': recent_projects,
    }
    return render(request, 'admin/dashboard.html', context)


def project_create_view(request):
    # Only allow regular users to create projects
    user_user = get_user_user(request)
    if not user_user:
        messages.error(request, 'Please log in as a regular user to create projects.')
        return redirect('login')
    
    if request.method == 'POST':
        form = ProjectCreationForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                project = form.save(commit=False)
                project.creator = user_user
                
                # Set initial status based on start date
                now = timezone.now()
                if project.start_date > now:
                    project.status = 'active'  # Projects starting in future are still 'active'
                else:
                    project.status = 'active'
                
                # Save the project (this will trigger model validation)
                project.save()
                
                # Save many-to-many relationships (existing tags)
                form.save_m2m()
                
                # Handle new tags
                new_tags = form.cleaned_data.get('new_tags', [])
                for tag_name in new_tags:
                    tag, created = Tag.objects.get_or_create(name=tag_name.lower())
                    project.tags.add(tag)
                
                # Handle multiple images if provided
                additional_images = request.FILES.getlist('additional_images')
                if additional_images:
                    for i, image in enumerate(additional_images):
                        # Set first additional image as primary if no main image was uploaded
                        is_primary = (i == 0 and not project.image)
                        ProjectPicture.objects.create(
                            project=project, 
                            image=image, 
                            is_primary=is_primary
                        )
                
                messages.success(request, 'Project created successfully!')
                return redirect('my_projects')
                
            except ValidationError as e:
                # Handle model validation errors
                for error in e.messages:
                    messages.error(request, error)
            except Exception as e:
                messages.error(request, f'Error creating project: {str(e)}')
        else:
            # Display form errors
            for field, errors in form.errors.items():
                for error in errors:
                    if field == '__all__':
                        messages.error(request, error)
                    else:
                        messages.error(request, f"{field}: {error}")
    else:
        form = ProjectCreationForm()
    
    return render(request, 'auth/project_create.html', {'form': form})

def project_list_view(request):
    """View to show all projects with filtering and sorting options"""
    # Update all project statuses first
    update_project_statuses()
    
    # Then proceed with the rest of the view logic
    projects = Project.objects.all()
    
    # Get filter parameters from request
    category = request.GET.get('category')
    status = request.GET.get('status')
    sort = request.GET.get('sort', 'newest')
    search = request.GET.get('search')
    tag_search = request.GET.get('tag')
    
    # Apply filters
    if category:
        projects = projects.filter(category=category)
    if status:
        projects = projects.filter(status=status)
    
    # Apply search by name, description, OR tags
    if search:
        projects = projects.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search) |
            Q(tags__name__icontains=search)
        ).distinct()
    
    # Apply tag-specific search (if provided)
    if tag_search:
        projects = projects.filter(tags__name__icontains=tag_search).distinct()
    
    # Apply sorting
    if sort == 'newest':
        projects = projects.order_by('-created_at')
    elif sort == 'oldest':
        projects = projects.order_by('created_at')
    elif sort == 'highest_funded':
        projects = projects.annotate(
            total_donations=Coalesce(Sum('donations__amount'), Decimal('0.00'))
        ).order_by('-total_donations')
    elif sort == 'most_popular':
        projects = projects.annotate(
            donation_count=Count('donations')
        ).order_by('-donation_count')
    elif sort == 'ending_soon':
        # Only show active projects for ending soon
        projects = projects.filter(status='active').order_by('end_date')
    
    # Get all unique tags for the tag cloud
    all_tags = Tag.objects.annotate(project_count=Count('project')).order_by('-project_count')[:20]
    
    # Pagination
    paginator = Paginator(projects, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'categories': Project.CATEGORY_CHOICES,
        'status_choices': Project.STATUS_CHOICES,
        'current_category': category,
        'current_status': status,
        'current_sort': sort,
        'search_query': search,
        'tag_query': tag_search,
        'all_tags': all_tags,
        'total_projects': projects.count(),
    }
    return render(request, 'auth/project_list.html', context)


def profile_view(request):
    # Only allow regular users to access profile
    user_user = get_user_user(request)
    if not user_user:
        messages.error(request, 'Please log in as a regular user to access your profile.')
        return redirect('login')
    
    user_projects = Project.objects.filter(creator=user_user).order_by('-created_at')
    user_donations = Donation.objects.filter(user=user_user).select_related('project').order_by('-donated_at')
    
    context = {
        'user': user_user,
        'user_projects': user_projects,
        'user_donations': user_donations,
        'projects_count': user_projects.count(),
        'donations_count': user_donations.count(),
        'total_donated': user_donations.aggregate(total=models.Sum('amount'))['total'] or 0,
    }
    return render(request, 'auth/profile.html', context)


def edit_profile_view(request):
    user_user = get_user_user(request)
    if not user_user:
        messages.error(request, 'Please log in as a regular user to edit your profile.')
        return redirect('login')
    
    if request.method == 'POST':
        form = UserProfileEditForm(request.POST, request.FILES, instance=user_user)
        if form.is_valid():
            user = form.save(commit=False)
            # Ensure email remains unchanged (extra security)
            user.email = user_user.email
            user.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserProfileEditForm(instance=user_user)
    
    return render(request, 'auth/edit_profile.html', {'form': form})


def delete_account_view(request):
    user_user = get_user_user(request)
    if not user_user:
        messages.error(request, 'Please log in as a regular user to delete your account.')
        return redirect('login')
    
    if request.method == 'POST':
        password = request.POST.get('password')
        
        if password:
            # Password verification step
            if user_user.check_password(password):
                user_user.delete()
                clear_user_session(request)
                messages.success(request, 'Your account has been deleted successfully.')
                return redirect('home')
            else:
                messages.error(request, 'Incorrect password. Account deletion failed.')
                return render(request, 'auth/delete_account.html', {'show_password_field': True})
        else:
            # First step - show password field
            return render(request, 'auth/delete_account.html', {'show_password_field': True})
    
    # Initial GET request
    return render(request, 'auth/delete_account.html', {'show_password_field': False})


def my_projects_view(request):
    user_user = get_user_user(request)
    if not user_user:
        messages.error(request, 'Please log in as a regular user to view your projects.')
        return redirect('login')
    
    user_projects = Project.objects.filter(creator=user_user).order_by('-created_at')
    return render(request, 'auth/my_projects.html', {'projects': user_projects})

def my_donations_view(request):
    user_user = get_user_user(request)
    if not user_user:
        messages.error(request, 'Please log in as a regular user to view your donations.')
        return redirect('login')
    
    user_donations = Donation.objects.filter(user=user_user).select_related('project').order_by('-donated_at')
    return render(request, 'auth/my_donations.html', {'donations': user_donations})


def home_view(request):
    # Get highest five rated running projects
    top_rated_projects = Project.objects.filter(
        status='active',
        end_date__gte=timezone.now()
    ).annotate(
        avg_rating=Avg('ratings__value')
    ).order_by('-avg_rating')[:5]
    
    # Get latest 5 projects
    latest_projects = Project.objects.filter(
        status='active'
    ).order_by('-created_at')[:5]
    
    # Get latest 5 featured projects
    featured_projects = Project.objects.filter(
        status='active',
        is_featured=True
    ).order_by('-created_at')[:5]
    
    # Get all categories for the dropdown
    categories = Project.CATEGORY_CHOICES
    
    context = {
        'top_rated_projects': top_rated_projects,
        'latest_projects': latest_projects,
        'featured_projects': featured_projects,
        'categories': categories,
    }
    
    return render(request, 'pages/home.html', context)

def category_projects(request, category_key):
    projects = Project.objects.filter(category=category_key, status="active").order_by("-created_at")

    category_name = dict(Project.CATEGORY_CHOICES).get(category_key, category_key)

    return render(request, "pages/category_projects.html", {
        "projects": projects,
        "category_name": category_name,
    })




def password_reset_request(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = CustomUser.objects.get(email=email)
            TokenService.send_password_reset_email(user, request)
            messages.success(request, 'Password reset instructions have been sent to your email.')
            return redirect('login')
        except CustomUser.DoesNotExist:
            messages.error(request, 'No account found with that email address.')
    
    return render(request, 'auth/password_reset_request.html')

def password_reset_confirm(request, token):  # token will be a UUID object
    user, error_message = TokenService.validate_password_reset_token(token)
    
    if error_message:
        messages.error(request, error_message)
        return redirect('password_reset_request')
    
    if request.method == 'POST':
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        if password == password_confirm:
            user.set_password(password)
            user.save()
            
            # Delete the used token
            PasswordResetToken.objects.filter(user=user).delete()
            
            messages.success(request, 'Your password has been reset successfully. You can now login.')
            return redirect('login')
        else:
            messages.error(request, 'Passwords do not match.')
    
    return render(request, 'auth/password_reset_confirm.html', {'token': token})


def change_password_view(request):
    user_user = get_user_user(request)
    if not user_user:
        messages.error(request, 'Please log in as a regular user to change your password.')
        return redirect('login')
    
    if request.method == 'POST':
        form = PasswordChangeForm(user_user, request.POST)
        if form.is_valid():
            user = form.save()
            # Update session to prevent logout - you might need to update your session here
            # update_session_auth_hash(request, user)  # This is for Django's auth, you might need custom handling
            messages.success(request, 'Your password has been changed successfully!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeForm(user_user)
    
    return render(request, 'auth/change_password.html', {'form': form})


def project_detail_view(request, project_id):
    """View for individual project details with reply functionality"""
    project = get_object_or_404(Project, id=project_id)
    
    user_user = get_user_user(request)
    user_logged_in = is_user_logged_in(request)
    
    # Only restrict access to canceled projects for non-creators/non-admins
    if (project.status == 'canceled' and 
        not (user_user and user_user == project.creator) and 
        not is_admin_logged_in(request)):
        messages.error(request, 'You do not have permission to view this canceled project.')
        return redirect('project_list')
    
    # Check if project has ended (for everyone, including creator)
    project_ended = project.status == 'completed' or project.end_date < timezone.now()
    is_creator = user_user and user_user.id == project.creator.id
    
    # Get all donations and comments
    all_donations = Donation.objects.filter(project=project).select_related('user').order_by('-donated_at')
    all_comments = Comment.objects.filter(project=project, parent__isnull=True).select_related('user').prefetch_related('replies__user').order_by('-created_at')
    ratings = Rating.objects.filter(project=project)
    
    # Check if user wants to show all items
    show_all_donations = request.GET.get('show_donations') == 'all'
    show_all_comments = request.GET.get('show_comments') == 'all'
    
    # Get limited or all items based on user selection
    donations = all_donations[:5] if not show_all_donations else all_donations
    comments = all_comments[:5] if not show_all_comments else all_comments
    
    # Calculate average rating
    average_rating = ratings.aggregate(avg=Avg('value'))['avg'] or 0
    
    # Get similar projects
    similar_projects = Project.objects.filter(
        status='active',
        tags__in=project.tags.all()
    ).exclude(id=project.id).distinct()[:4]
    
    # Get user's rating if logged in
    user_rating = None
    if user_user:
        user_rating = Rating.objects.filter(project=project, user=user_user).first()
    
    # Check if current user can delete the project
    can_delete = False
    if user_user and hasattr(user_user, 'id') and user_user.id == project.creator.id:
        can_delete = project.can_cancel()
    
    # Add reporting information to each comment and its replies
    comments_with_reports = []
    for comment in comments:
        # Check if current user has reported this comment
        user_reported_comment = False
        if user_user:
            user_reported_comment = ReportedComment.objects.filter(
                user=user_user, 
                comment=comment
            ).exists()
        
        # Process replies for this comment
        replies_with_reports = []
        for reply in comment.replies.all():
            user_reported_reply = False
            if user_user:
                user_reported_reply = ReportedComment.objects.filter(
                    user=user_user, 
                    comment=reply
                ).exists()
            
            # Add the reported status to the reply object
            reply.user_reported = user_reported_reply
            replies_with_reports.append(reply)
        
        comments_with_reports.append({
            'comment': comment,
            'user_reported': user_reported_comment,
            'report_count': ReportedComment.objects.filter(comment=comment).count(),
            'replies': replies_with_reports
        })
    
    # Handle form submissions
    if request.method == 'POST' and user_user:
        form_type = request.POST.get('form_type')
        
        # Comment submission
        if form_type == 'comment':
            content = request.POST.get('content')
            parent_id = request.POST.get('parent_id')
            
            if content:
                if parent_id:  # This is a reply
                    try:
                        parent_comment = Comment.objects.get(id=parent_id)
                        Comment.objects.create(
                            user=user_user,
                            project=project,
                            content=content,
                            parent=parent_comment
                        )
                        messages.success(request, 'Your reply has been added!')
                    except Comment.DoesNotExist:
                        messages.error(request, 'Invalid comment to reply to.')
                else:  # This is a top-level comment
                    Comment.objects.create(
                        user=user_user,
                        project=project,
                        content=content
                    )
                    messages.success(request, 'Your comment has been added!')
                
                # Redirect to show all comments after adding a new one
                return redirect(f'{reverse("project_detail", args=[project.id])}?show_comments=all')
        
        # Rating submission
        elif form_type == 'rating':
            rating_value = request.POST.get('rating_value')
            if rating_value:
                try:
                    rating_value = int(rating_value)
                    if 1 <= rating_value <= 5:
                        rating, created = Rating.objects.update_or_create(
                            user=user_user,
                            project=project,
                            defaults={'value': rating_value}
                        )
                        messages.success(request, 'Your rating has been submitted!')
                        return redirect('project_detail', project_id=project.id)
                    else:
                        messages.error(request, 'Rating must be between 1 and 5.')
                except ValueError:
                    messages.error(request, 'Invalid rating value.')
        
        # Project reporting
        elif 'report_project' in request.POST:
            reason = request.POST.get('reason')
            if reason:
                # Check if user already reported this project
                if not ReportedProject.objects.filter(user=user_user, project=project).exists():
                    ReportedProject.objects.create(
                        user=user_user,
                        project=project,
                        reason=reason
                    )
                    messages.success(request, 'Thank you for reporting this project.')
                    
                    # Check if project has 2 or more reports and delete it
                    report_count = ReportedProject.objects.filter(project=project).count()
                    if report_count >= 2:
                        project.delete()
                        messages.warning(request, 'Project has been removed due to multiple reports.')
                        return redirect('project_list')
                else:
                    messages.error(request, 'You have already reported this project.')
                return redirect('project_detail', project_id=project.id)
    
    context = {
        'project': project,
        'donations': donations,
        'all_donations_count': all_donations.count(),
        'show_all_donations': show_all_donations,
        'comments_with_reports': comments_with_reports,
        'all_comments_count': all_comments.count(),
        'show_all_comments': show_all_comments,
        'average_rating': round(average_rating, 1),
        'similar_projects': similar_projects,
        'user_rating': user_rating,
        'can_delete': can_delete,
        'user_user': user_user,
        'user_logged_in': user_logged_in,
        'ratings_count': ratings.count(),
        # Add this variable for donation form logic - hide for everyone when ended
        'project_ended': project_ended,
    }
    
    return render(request, 'auth/project_detail.html', context)

    
def report_comment_view(request, comment_id):
    """View to report a comment"""
    comment = get_object_or_404(Comment, id=comment_id)
    user_user = get_user_user(request)
    
    if not user_user:
        messages.error(request, 'Please log in to report comments.')
        return redirect('login')
    
    if request.method == 'POST':
        reason = request.POST.get('reason')
        if reason:
            # Check if user already reported this comment
            if not ReportedComment.objects.filter(user=user_user, comment=comment).exists():
                ReportedComment.objects.create(
                    user=user_user,
                    comment=comment,
                    reason=reason
                )
                messages.success(request, 'Thank you for reporting this comment.')
                
                # Check if comment has 2 or more reports and delete it
                report_count = ReportedComment.objects.filter(comment=comment).count()
                if report_count >= 2:
                    comment.delete()
                    messages.warning(request, 'Comment has been removed due to multiple reports.')
            else:
                messages.error(request, 'You have already reported this comment.')
        else:
            messages.error(request, 'Please provide a reason for reporting.')
    
    # Redirect back to the project detail page
    return redirect('project_detail', project_id=comment.project.id)


def donate_view(request, project_id):
    """Simple donation view - you can expand this later"""
    project = get_object_or_404(Project, id=project_id)
    user_user = get_user_user(request)
    
    if not user_user:
        messages.error(request, 'Please log in to make a donation.')
        return redirect('login')
    
    if request.method == 'POST':
        amount = request.POST.get('amount')
        if amount:
            try:
                amount = float(amount)
                if amount > 0:
                    # Create donation
                    donation = Donation.objects.create(
                        user=user_user,
                        project=project,
                        amount=amount
                    )
                    messages.success(request, f'Thank you for your donation of {amount} EGP!')
                    return redirect('project_detail', project_id=project.id)
            except ValueError:
                messages.error(request, 'Please enter a valid amount.')
    
    messages.error(request, 'Invalid donation request.')
    return redirect('project_detail', project_id=project.id)

def delete_project_view(request, project_id):
    """Delete a project if donations are less than 25%"""
    project = get_object_or_404(Project, id=project_id)
    user_user = get_user_user(request)
    
    # Check if user is the creator and can cancel
    if not user_user or user_user != project.creator:
        messages.error(request, 'You are not authorized to delete this project.')
        return redirect('project_detail', project_id=project_id)
    
    if not project.can_cancel():
        messages.error(request, 'Cannot delete project. Donations have exceeded 25% of the target amount.')
        return redirect('project_detail', project_id=project_id)
    
    if request.method == 'POST':
        project_title = project.title
        project.delete()
        messages.success(request, f'Project "{project_title}" has been deleted successfully.')
        return redirect('my_projects')
    
    # If not POST, show confirmation page
    return render(request, 'auth/delete_project_confirm.html', {'project': project})


def public_profile_view(request, user_id):
    """View for public user profiles (without personal information)"""
    profile_user = get_object_or_404(CustomUser, id=user_id)
    
    # Only show basic information and projects
    user_projects = Project.objects.filter(creator=profile_user, status='active').order_by('-created_at')
    
    context = {
        'profile_user': profile_user,
        'user_projects': user_projects,
        'projects_count': user_projects.count(),
    }
    return render(request, 'auth/public_profile.html', context)

def auth_page(request):
    """Combined login and registration page"""
    # Redirect authenticated users
    if request.user.is_authenticated:
        return redirect('home')
    
    # You can pass the form if you want to use Django's form validation
    # form = CustomUserCreationForm()
    
    return render(request, 'auth.html')  #, {'form': form})