from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('activate/<uuid:token>/', views.activate_account, name='activate'),
    path('login/', views.user_login_view, name='login'),
    path('logout/', views.user_logout_view, name='logout'),
    path('logout/all/', views.logout_all_view, name='logout_all'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    path('my-projects/', views.my_projects_view, name='my_projects'),
    path('my-donations/', views.my_donations_view, name='my_donations'),
    path('project/create/', views.project_create_view, name='project_create'),
    path('projects/', views.project_list_view, name='project_list'),
    
    # Password management URLs - using UUID pattern to match TokenService
    path('password-reset/', views.password_reset_request, name='password_reset_request'),
    path('password-reset-confirm/<uuid:token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('change-password/', views.change_password_view, name='change_password'),
    
    # Account management URLs
    path('delete-account/', views.delete_account_view, name='delete_account'),
    
    # Admin URLs
    path('admin/login/', views.admin_login_view, name='admin_login'),
    path('admin/logout/', views.admin_logout_view, name='admin_logout'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('project/<int:project_id>/', views.project_detail_view, name='project_detail'),
    path('project/<int:project_id>/donate/', views.donate_view, name='donate'),
    path('project/delete/<int:project_id>/', views.delete_project_view, name='delete_project'),
    path('profile/<int:user_id>/', views.public_profile_view, name='public_profile'),
    path('comment/<int:comment_id>/report/', views.report_comment_view, name='report_comment'),

    path('user/<int:user_id>/', views.public_profile_view, name='public_profile'),
    
    
    
]