from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import RegexValidator, MinValueValidator
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
import uuid
from datetime import timedelta
from django.utils import timezone
from django.utils.text import slugify
from decimal import Decimal


class CustomUserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""
    
    use_in_migrations = True
    
    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_active', False)  # Users are inactive until email confirmation
        return self._create_user(email, password, **extra_fields)
    
    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)  # Superusers are active immediately
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self._create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    # Remove username field completely
    username = None
    email = models.EmailField(_('email address'), unique=True)
    
    # Additional required fields
    first_name = models.CharField(_('first name'), max_length=30)
    last_name = models.CharField(_('last name'), max_length=30)
    
    # Egyptian phone number validator
    phone_regex = RegexValidator(
        regex=r'^01[0-2,5]{1}[0-9]{8}$',
        message="Phone number must be entered in the format: '01XXXXXXXXX'. 11 digits allowed."
    )
    mobile_phone = models.CharField(
        _('mobile phone'),
        validators=[phone_regex], 
        max_length=11, 
        unique=True
    )
    
    # Optional fields
    profile_picture = models.ImageField(
        _('profile picture'),
        upload_to='profile_pictures/', 
        blank=True, 
        null=True
    )
    birthdate = models.DateField(_('birthdate'), blank=True, null=True)
    facebook_profile = models.URLField(_('facebook profile'), blank=True, null=True)
    country = models.CharField(_('country'), max_length=50, blank=True, null=True)
    
    # Use email as the unique identifier
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'mobile_phone']
    
    objects = CustomUserManager()
    
    def __str__(self):
        return self.email
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
    facebook_id = models.CharField(max_length=100, blank=True, null=True, unique=True)
    
    def save(self, *args, **kwargs):
        # If user signs up with Facebook and doesn't have a username
        if not self.username and self.email:
            self.username = self.email
        super().save(*args, **kwargs)


# Model for tags
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name




# Model for projects
class Project(models.Model):
    # Project status choices
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('canceled', 'Canceled'),
        ('completed', 'Completed'),
    ]
    
    # Static category choices
    CATEGORY_CHOICES = [
        ('technology', 'Technology'),
        ('art', 'Art'),
        ('music', 'Music'),
        ('film', 'Film & Video'),
        ('design', 'Design'),
        ('food', 'Food'),
        ('publishing', 'Publishing'),
        ('games', 'Games'),
        ('fashion', 'Fashion'),
        ('health', 'Health & Fitness'),
        ('education', 'Education'),
        ('environment', 'Environment'),
        ('community', 'Community'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    target_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        validators=[MinValueValidator(1.00)]
    )
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    image = models.ImageField(upload_to='project_images/', blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    is_featured = models.BooleanField(default=False)
    tags = models.ManyToManyField(Tag, blank=True)
    creator = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='projects')
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Calculate current total donations
    def current_donations(self):
        from django.db.models import Sum
        from decimal import Decimal
        return self.donations.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    
    # Calculate donation progress percentage
    def donation_progress(self):
        current = self.current_donations()
        if self.target_amount and current:
            return (current / self.target_amount) * 100
        return 
    
    # Check if project can be canceled (donations < 25% of target)
    def can_cancel(self):
        from decimal import Decimal
        current = self.current_donations()
        # Use Decimal for the multiplication
        return current < (self.target_amount * Decimal('0.25'))
    
    # Check if project is running (current time between start and end time)
    def is_running(self):
        """Check if project is running (current time between start and end time) OR if it hasn't started yet"""
        now = timezone.now()
        return self.status == 'active' and now <= self.end_date
    
    # Calculate average rating
    def average_rating(self):
        from django.db.models import Avg
        return self.ratings.aggregate(avg_rating=Avg('value'))['avg_rating'] or 0
    
    def clean(self):
        # Check if dates are provided before comparing
        if self.start_date is not None and self.end_date is not None:
            if self.end_date <= self.start_date:
                raise ValidationError("End date must be after start date.")
            
            # Check if start date is in the future
            if self.start_date <= timezone.now():
                raise ValidationError("Start date must be in the future.")
        else:
            # If dates are None, we'll let field validation handle the required field error
            pass
        
        if self.target_amount is not None and self.target_amount <= 0:
            raise ValidationError("Target amount must be greater than zero.")
    
    def save(self, *args, **kwargs):
        # Only run full validation if the instance is being created or dates/target are being changed
        if not self.pk or any(field in kwargs.get('update_fields', []) for field in ['start_date', 'end_date', 'target_amount']):
            self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
    
    def get_category_display_name(self):
        """Get the human-readable display name for the category"""
        return dict(self.CATEGORY_CHOICES).get(self.category, self.category)
    
    def days_remaining(self):
        """Calculate days remaining until project ends"""
        if self.end_date and timezone.now() < self.end_date:
            return (self.end_date - timezone.now()).days
        return 0  # Return 0 instead of None for ended projects
        
    def is_funded(self):
        """Check if project has reached its funding goal"""
        return self.current_donations() >= self.target_amount
    @property
    def main_image(self):
        """
        Return the primary project picture if one exists,
        otherwise fallback to the first uploaded picture,
        otherwise fallback to the single 'image' field,
        otherwise None.
        """
        # Prefer primary picture
        primary = self.pictures.filter(is_primary=True).first()
        if primary:
            return primary.image

        # Fallback to any other uploaded picture
        other = self.pictures.first()
        if other:
            return other.image

        # Fallback to the legacy single-image field
        if self.image:
            return self.image

        # No images at all
        return None
    def update_status(self):
        """Update the project status based on current time, but preserve the original logic"""
        now = timezone.now()
        
        # If project is canceled, don't change status
        if self.status == 'canceled':
            return self.status
            
        # If end date has passed, mark as completed
        if now > self.end_date:
            self.status = 'completed'
        # If within the project timeframe, ensure it's active
        elif now >= self.start_date and now <= self.end_date:
            self.status = 'active'
        # If start date is in the future, keep as active (original behavior)
        else:
            self.status = 'active'
            
        return self.status
    
    def get_days_remaining_display(self):
        """Get a user-friendly display of days remaining that works with status updates"""
        now = timezone.now()
        
        if self.status == 'completed':
            return "Ended"
        
        if not self.end_date:
            return "No end date"
        
        if now > self.end_date:
            return "Ended"
        
        days_left = (self.end_date - now).days
        
        if days_left > 7:
            return f"{days_left} days left"
        elif days_left > 1:
            return f"{days_left} days left"
        elif days_left == 1:
            return "Last day!"
        elif days_left == 0:
            # Check if we have hours left
            hours_left = (self.end_date - now).seconds // 3600
            if hours_left > 1:
                return f"{hours_left} hours left"
            elif hours_left == 1:
                return "1 hour left!"
            else:
                return "Ending soon!"
        else:
            return "Ended"
    
    def save(self, *args, **kwargs):
        # Update status before saving
        self.update_status()
        
        # Only run full validation if the instance is being created or dates/target are being changed
        if not self.pk or any(field in kwargs.get('update_fields', []) for field in ['start_date', 'end_date', 'target_amount']):
            self.full_clean()
        super().save(*args, **kwargs)
    @property
    def total_donations_count(self):
        return self.donations.count()


# Model for project images (optional if you want multiple images per project)
class ProjectPicture(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='pictures')
    image = models.ImageField(upload_to='project_pictures/')
    is_primary = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        # If this is set as primary, ensure no other primary exists for this project
        if self.is_primary:
            ProjectPicture.objects.filter(project=self.project, is_primary=True).update(is_primary=False)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Image for {self.project.title}"
    
    class Meta:
        ordering = ['-is_primary', 'uploaded_at']


# Model for donations
class Donation(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='donations')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='donations')
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(1.00)])
    donated_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.email} donated {self.amount} to {self.project.title}"


# Model for comments
class Comment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='comments')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    is_reported = models.BooleanField(default=False)
    
    def is_reply(self):
        return self.parent is not None
    
    def __str__(self):
        return f"Comment by {self.user.email} on {self.project.title}"


# Model for ratings
class Rating(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='ratings')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='ratings')
    value = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1-5 star rating
    rated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'project')  # A user can rate a project only once
    
    def __str__(self):
        return f"{self.user.email} rated {self.project.title} with {self.value} stars"


# Model for reported projects
class ReportedProject(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='reports')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='project_reports')
    reason = models.TextField()
    reported_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'project')  # A user can report a project only once
    
    def __str__(self):
        return f"{self.project.title} reported by {self.user.email}"


# Model for reported comments
class ReportedComment(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='reports')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='comment_reports')
    reason = models.TextField()
    reported_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'comment')  # A user can report a comment only once
    
    def __str__(self):
        return f"Comment reported by {self.user.email}"


# Email activation token model
class ActivationToken(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    activation_code = models.CharField(max_length=6, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(hours=24)
    
    def generate_activation_code(self):
        """Generate a 6-digit activation code"""
        import random
        self.activation_code = str(random.randint(100000, 999999))
        self.save()
        return self.activation_code
    
    def __str__(self):
        return f"Activation token for {self.user.email}"


# Password reset token model
class PasswordResetToken(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(hours=1)
    
    def __str__(self):
        return f"Password reset token for {self.user.email}"