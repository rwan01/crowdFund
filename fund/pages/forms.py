from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import CustomUser, Project, Tag 
from django.utils import timezone

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email'
        })
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your first name'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your last name'
        })
    )
    mobile_phone = forms.CharField(
        max_length=11,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your mobile phone (01XXXXXXXXX)'
        })
    )
    profile_picture = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control'
        })
    )

    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'mobile_phone', 'password1', 'password2', 'profile_picture')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name not in ['profile_picture']:
                field.widget.attrs['class'] = 'form-control'

class AdminAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter admin email'
        })
    )
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter admin password'
        }),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Admin Email'

    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise ValidationError(
                _("This account is inactive."),
                code='inactive',
            )
        if not user.is_staff and not user.is_superuser:
            raise ValidationError(
                _("You don't have permission to access the admin site."),
                code='no_admin_permission',
            )

class UserAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email'
        })
    )
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password'
        }),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Email'

    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise ValidationError(
                _("This account is inactive."),
                code='inactive',
            )
        if user.is_staff or user.is_superuser:
            raise ValidationError(
                _("Please use the admin login page to access the admin site."),
                code='use_admin_login',
            )

# User Profile Edit Form for regular users
class UserProfileEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'mobile_phone', 
                 'profile_picture', 'birthdate', 'facebook_profile', 'country')
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'readonly': 'readonly',
                'style': 'background-color: #f8f9fa;'  # Visual indicator that it's read-only
            }),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'mobile_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
            'birthdate': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'facebook_profile': forms.URLInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make email field disabled at the form level as well
        self.fields['email'].disabled = True

    def clean_email(self):
        # Always return the existing email value
        return self.instance.email

    def clean_mobile_phone(self):
        mobile_phone = self.cleaned_data.get('mobile_phone')
        if CustomUser.objects.filter(mobile_phone=mobile_phone).exclude(pk=self.instance.pk).exists():
            raise ValidationError("This mobile phone number is already in use.")
        return mobile_phone




# Admin-only form (keep for admin interface)
class CustomUserChangeForm(UserChangeForm):
    password = forms.CharField(
        label=_("Password"),
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'readonly': 'readonly',
            'placeholder': '········'
        }),
        help_text=_("Raw passwords are not stored, so there is no way to see this user's password. "
                   "You can change the password using <a href=\"../password/\">this form</a>."),
    )
    
    class Meta:
        model = CustomUser
        fields = ('email', 'password', 'first_name', 'last_name', 'mobile_phone', 
                 'profile_picture', 'birthdate', 'facebook_profile', 'country',
                 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'mobile_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
            'birthdate': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'facebook_profile': forms.URLInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password'].required = False



# class ProjectCreationForm(forms.ModelForm):
#     new_tags = forms.CharField(
#         required=False,
#         widget=forms.TextInput(attrs={
#             'placeholder': 'Enter new tags separated by commas',
#             'class': 'form-control'
#         }),
#         help_text='Enter new tags separated by commas (e.g., "tech, innovation, startup")'
#     )
    
#     class Meta:
#         model = Project
#         fields = ['title', 'description', 'category', 'target_amount', 
#                  'start_date', 'end_date', 'tags', 'image']
#         widgets = {
#             'tags': forms.SelectMultiple(attrs={'class': 'form-control', 'size': '5'}),
#             'title': forms.TextInput(attrs={'class': 'form-control'}),
#             'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
#             'category': forms.Select(attrs={'class': 'form-control'}),
#             'target_amount': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'step': '0.01'}),
#             'start_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
#             'end_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
#             'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
#         }
    
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['tags'].required = False
#         # Set initial minimum for start date to current time
#         now = timezone.now()
#         self.fields['start_date'].widget.attrs['min'] = now.strftime('%Y-%m-%dT%H:%M')
    
#     def clean(self):
#         cleaned_data = super().clean()
#         start_date = cleaned_data.get('start_date')
#         end_date = cleaned_data.get('end_date')
#         target_amount = cleaned_data.get('target_amount')
        
#         # Validate dates if they are provided
#         if start_date and end_date:
#             if start_date >= end_date:
#                 self.add_error('end_date', "End date must be after start date.")
            
#             if start_date <= timezone.now():
#                 self.add_error('start_date', "Start date must be in the future.")
        
#         # Validate target amount
#         if target_amount and target_amount <= 0:
#             self.add_error('target_amount', "Target amount must be greater than zero.")
        
#         return cleaned_data
    
#     def clean_new_tags(self):
#         new_tags = self.cleaned_data.get('new_tags', '')
#         if new_tags:
#             # Split by commas and remove empty strings
#             tag_names = [name.strip() for name in new_tags.split(',') if name.strip()]
#             # Limit to 10 tags maximum
#             if len(tag_names) > 10:
#                 raise ValidationError("You can add a maximum of 10 new tags.")
#             return tag_names
#         return []
    
#     def save(self, commit=True):
#         project = super().save(commit=False)
        
#         if commit:
#             project.save()
#             self.save_m2m()  # Save many-to-many relationships (tags)
            
#             # Handle new tags
#             new_tags = self.cleaned_data.get('new_tags', [])
#             for tag_name in new_tags:
#                 tag, created = Tag.objects.get_or_create(name=tag_name.lower())  # Normalize to lowercase
#                 project.tags.add(tag)
        
#         return project



class ProjectCreationForm(forms.ModelForm):
    new_tags = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter new tags separated by commas',
            'class': 'form-control'
        }),
        help_text='Enter new tags separated by commas (e.g., "tech, innovation, startup")'
    )
    
    class Meta:
        model = Project
        fields = ['title', 'description', 'category', 'target_amount', 
                 'start_date', 'end_date', 'tags', 'image']
        widgets = {
            'tags': forms.SelectMultiple(attrs={'class': 'form-control', 'size': '5'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'target_amount': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'step': '0.01'}),
            'start_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tags'].required = False
        # Set initial minimum for start date to current time (but don't enforce it)
        now = timezone.now()
        self.fields['start_date'].widget.attrs['min'] = now.strftime('%Y-%m-%dT%H:%M')
    
    def clean_start_date(self):
        start_date = self.cleaned_data.get('start_date')
        if start_date:
            # Make timezone-aware if it's naive
            if start_date.tzinfo is None:
                from django.utils.timezone import make_aware
                start_date = make_aware(start_date)
        return start_date
    
    def clean_end_date(self):
        end_date = self.cleaned_data.get('end_date')
        if end_date:
            # Make timezone-aware if it's naive
            if end_date.tzinfo is None:
                from django.utils.timezone import make_aware
                end_date = make_aware(end_date)
        return end_date
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        target_amount = cleaned_data.get('target_amount')
        
        # Validate dates if they are provided
        if start_date and end_date:
            if start_date >= end_date:
                self.add_error('end_date', "End date must be after start date.")
            
            # REMOVED THE PROBLEMATIC VALIDATION
            # Allow projects to start immediately or in the future
            # if start_date <= timezone.now():
            #     self.add_error('start_date', "Start date must be in the future.")
        
        # Validate target amount
        if target_amount and target_amount <= 0:
            self.add_error('target_amount', "Target amount must be greater than zero.")
        
        return cleaned_data
    
    def clean_new_tags(self):
        new_tags = self.cleaned_data.get('new_tags', '')
        if new_tags:
            # Split by commas and remove empty strings
            tag_names = [name.strip() for name in new_tags.split(',') if name.strip()]
            # Limit to 10 tags maximum
            if len(tag_names) > 10:
                raise ValidationError("You can add a maximum of 10 new tags.")
            return tag_names
        return []
    
    def save(self, commit=True):
        project = super().save(commit=False)
        
        if commit:
            project.save()
            self.save_m2m()  # Save many-to-many relationships (tags)
            
            # Handle new tags
            new_tags = self.cleaned_data.get('new_tags', [])
            for tag_name in new_tags:
                tag, created = Tag.objects.get_or_create(name=tag_name.lower())  # Normalize to lowercase
                project.tags.add(tag)
        
        return project







    

# Password reset form
class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        })
    )

# Password reset confirmation form
class PasswordResetConfirmForm(forms.Form):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter new password'
        }),
        min_length=8,
        help_text="Password must be at least 8 characters long."
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm new password'
        }),
        min_length=8,
        help_text="Enter the same password as above, for verification."
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            raise ValidationError({
                'password_confirm': 'Passwords do not match.'
            })

        return cleaned_data

# Account deletion confirmation form
class AccountDeletionForm(forms.Form):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password to confirm deletion'
        }),
        required=True,
        help_text="Enter your password to confirm account deletion."
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not self.user.check_password(password):
            raise ValidationError('Incorrect password.')
        return password