from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    CustomUser, ActivationToken, Tag, 
    Project, ProjectPicture, Donation, Comment,
    Rating, ReportedProject, ReportedComment, PasswordResetToken
)
from .forms import CustomUserCreationForm, CustomUserChangeForm
from django.db.models import Sum



# Custom User Admin
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    
    list_display = ('email', 'first_name', 'last_name', 'mobile_phone', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'country', 'date_joined')
    search_fields = ('email', 'first_name', 'last_name', 'mobile_phone')
    ordering = ('email',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {
            'fields': (
                'first_name', 'last_name', 'mobile_phone', 'profile_picture',
                'birthdate', 'facebook_profile', 'country'
            )
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'first_name', 'last_name', 'mobile_phone',
                'password1', 'password2', 'is_staff', 'is_active'
            )}
        ),
    )


# Activation Token Admin
class ActivationTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'created_at', 'is_expired')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'token')
    readonly_fields = ('token', 'created_at')
    
    def is_expired(self, obj):
        return obj.is_expired()
    is_expired.boolean = True
    is_expired.short_description = 'Expired'


# Password Reset Token Admin
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'created_at', 'is_expired')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'token')
    readonly_fields = ('token', 'created_at')
    
    def is_expired(self, obj):
        return obj.is_expired()
    is_expired.boolean = True
    is_expired.short_description = 'Expired'


# Tag Admin
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'project_count')
    search_fields = ('name',)
    
    def project_count(self, obj):
        return obj.project_set.count()
    project_count.short_description = 'Number of Projects'


# Project Picture Inline
class ProjectPictureInline(admin.TabularInline):
    model = ProjectPicture
    extra = 1
    fields = ('image', 'is_primary')
    readonly_fields = ('preview',)
    
    def preview(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" style="max-height: 100px;" />'
        return "No image"
    preview.allow_tags = True


class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'creator', 'category', 'target_amount',
        'current_donations', 'donation_progress', 'status', 
        'is_featured', 'start_date', 'end_date', 'is_running'
    )
    list_filter = ('status', 'is_featured', 'category', 'start_date', 'end_date')
    search_fields = ('title', 'description', 'creator__email', 'creator__first_name', 'creator__last_name')
    readonly_fields = ('created_at', 'current_donations', 'donation_progress', 'average_rating')
    filter_horizontal = ('tags',)
    inlines = [ProjectPictureInline]
    
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'creator', 'category', 'image')
        }),
        ('Financial Info', {
            'fields': ('target_amount', 'current_donations', 'donation_progress')
        }),
        ('Campaign Settings', {
            'fields': ('start_date', 'end_date', 'status', 'is_featured', 'tags')
        }),
        ('Ratings', {
            'fields': ('average_rating',)
        }),
        ('Metadata', {
            'fields': ('created_at',)
        }),
    )
    
    def current_donations(self, obj):
        return obj.current_donations()
    current_donations.short_description = 'Current Donations'
    
def donation_progress(self, obj):
    # Add these checks at the beginning
    if obj.target_amount is None:
        return "0%"
    
    total_donations = obj.donations.aggregate(total=Sum('amount'))['total']
    if total_donations is None:
        total_donations = 0
    
    # Your existing calculation code here, but with safety
    try:
        progress = (total_donations / obj.target_amount) * 100
        return f"{progress:.1f}%"
    except ZeroDivisionError:
        return "0%"


# Donation Admin
class DonationAdmin(admin.ModelAdmin):
    list_display = ('user', 'project', 'amount', 'donated_at')
    list_filter = ('donated_at', 'project')
    search_fields = (
        'user__email', 'user__first_name', 'user__last_name',
        'project__title'
    )
    readonly_fields = ('donated_at',)
    date_hierarchy = 'donated_at'


# Comment Admin
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'project', 'short_content', 'created_at', 'is_reported', 'is_reply')
    list_filter = ('created_at', 'is_reported', 'project')
    search_fields = (
        'user__email', 'user__first_name', 'user__last_name',
        'project__title', 'content'
    )
    readonly_fields = ('created_at',)
    
    def short_content(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    short_content.short_description = 'Content'
    
    def is_reply(self, obj):
        return obj.is_reply()
    is_reply.boolean = True
    is_reply.short_description = 'Is Reply'


# Rating Admin
class RatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'project', 'value', 'rated_at')
    list_filter = ('value', 'rated_at')
    search_fields = (
        'user__email', 'user__first_name', 'user__last_name',
        'project__title'
    )
    readonly_fields = ('rated_at',)


# Reported Project Admin
class ReportedProjectAdmin(admin.ModelAdmin):
    list_display = ('project', 'user', 'short_reason', 'reported_at')
    list_filter = ('reported_at',)
    search_fields = (
        'project__title', 'user__email', 'user__first_name', 
        'user__last_name', 'reason'
    )
    readonly_fields = ('reported_at',)
    
    def short_reason(self, obj):
        return obj.reason[:50] + '...' if len(obj.reason) > 50 else obj.reason
    short_reason.short_description = 'Reason'


# Reported Comment Admin
class ReportedCommentAdmin(admin.ModelAdmin):
    list_display = ('comment', 'user', 'short_reason', 'reported_at')
    list_filter = ('reported_at',)
    search_fields = (
        'comment__content', 'user__email', 'user__first_name', 
        'user__last_name', 'reason'
    )
    readonly_fields = ('reported_at',)
    
    def short_reason(self, obj):
        return obj.reason[:50] + '...' if len(obj.reason) > 50 else obj.reason
    short_reason.short_description = 'Reason'


# Register all models
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(ActivationToken, ActivationTokenAdmin)
admin.site.register(PasswordResetToken, PasswordResetTokenAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(ProjectPicture)
admin.site.register(Donation, DonationAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Rating, RatingAdmin)
admin.site.register(ReportedProject, ReportedProjectAdmin)
admin.site.register(ReportedComment, ReportedCommentAdmin)

# Optional: Customize admin site header and title
admin.site.site_header = 'Crowd-Funding Platform Administration'
admin.site.site_title = 'Crowd-Funding Admin'
admin.site.index_title = 'Welcome to Crowd-Funding Platform Admin'