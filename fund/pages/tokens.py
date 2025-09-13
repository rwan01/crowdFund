import uuid
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from .models import CustomUser, ActivationToken, PasswordResetToken


class TokenService:
    """Service class for token generation and validation"""
    
    @staticmethod
    def generate_activation_token(user):
        """Generate and return an activation token for a user"""
        # Delete any existing tokens for this user
        ActivationToken.objects.filter(user=user).delete()
        
        # Create new token
        token = ActivationToken.objects.create(user=user)
        return token
    
    @staticmethod
    def generate_password_reset_token(user):
        """Generate and return a password reset token for a user"""
        # Delete any existing tokens for this user
        PasswordResetToken.objects.filter(user=user).delete()
        
        # Create new token
        token = PasswordResetToken.objects.create(user=user)
        return token
    
    @staticmethod
    def validate_activation_token(token_value):
        """Validate an activation token and return the user if valid"""
        try:
            token = ActivationToken.objects.get(token=token_value)
            
            if token.is_expired():
                token.delete()
                return None, "Activation link has expired. Please register again."
            
            user = token.user
            token.delete()  # Delete the used token
            return user, None
            
        except ActivationToken.DoesNotExist:
            return None, "Invalid activation link."
    
    @staticmethod
    def validate_password_reset_token(token_value):
        """Validate a password reset token and return the user if valid"""
        try:
            token = PasswordResetToken.objects.get(token=token_value)
            
            if token.is_expired():
                token.delete()
                return None, "Password reset link has expired. Please request a new one."
            
            user = token.user
            return user, None
            
        except PasswordResetToken.DoesNotExist:
            return None, "Invalid password reset link."
    
    @staticmethod
    def send_activation_email(user, request):
        """Send activation email to user"""
        token = TokenService.generate_activation_token(user)
        
        subject = 'Activate Your Crowd-Funding Account'
        html_message = render_to_string('auth/activation_email.html', {
            'user': user,
            'token': token.token,
            'domain': request.get_host(),
            'protocol': 'https' if request.is_secure() else 'http'
        })
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=html_message,
            fail_silently=False,
        )
    
    @staticmethod
    def send_password_reset_email(user, request):
        """Send password reset email to user"""
        token = TokenService.generate_password_reset_token(user)
        
        subject = 'Reset Your Password'
        html_message = render_to_string('auth/password_reset_email.html', {
            'user': user,
            'token': token.token,
            'domain': request.get_host(),
            'protocol': 'https' if request.is_secure() else 'http'
        })
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=html_message,
            fail_silently=False,
        )
    
    @staticmethod
    def cleanup_expired_tokens():
        """Clean up expired tokens from the database"""
        # Delete expired activation tokens
        activation_tokens = ActivationToken.objects.all()
        for token in activation_tokens:
            if token.is_expired():
                token.delete()
        
        # Delete expired password reset tokens
        password_tokens = PasswordResetToken.objects.all()
        for token in password_tokens:
            if token.is_expired():
                token.delete()
    
    @staticmethod
    def delete_user_tokens(user):
        """Delete all tokens for a specific user"""
        ActivationToken.objects.filter(user=user).delete()
        PasswordResetToken.objects.filter(user=user).delete()


class TokenMiddleware:
    """Middleware to automatically clean up expired tokens"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Clean up tokens once when the server starts
        TokenService.cleanup_expired_tokens()
    
    def __call__(self, request):
        # Clean up expired tokens periodically (e.g., every 100 requests)
        if not hasattr(request, 'cleanup_tokens_counter'):
            request.cleanup_tokens_counter = 0
        
        request.cleanup_tokens_counter += 1
        
        if request.cleanup_tokens_counter % 100 == 0:
            TokenService.cleanup_expired_tokens()
        
        response = self.get_response(request)
        return response


# Command to clean up tokens manually
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Clean up expired activation and password reset tokens'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Delete all tokens, not just expired ones',
        )
    
    def handle(self, *args, **options):
        delete_all = options['all']
        
        if delete_all:
            # Delete all tokens
            ActivationToken.objects.all().delete()
            PasswordResetToken.objects.all().delete()
            self.stdout.write(
                self.style.SUCCESS('Successfully deleted all tokens')
            )
        else:
            # Delete only expired tokens
            expired_activation_count = 0
            expired_password_count = 0
            
            activation_tokens = ActivationToken.objects.all()
            for token in activation_tokens:
                if token.is_expired():
                    token.delete()
                    expired_activation_count += 1
            
            password_tokens = PasswordResetToken.objects.all()
            for token in password_tokens:
                if token.is_expired():
                    token.delete()
                    expired_password_count += 1
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully cleaned up {expired_activation_count} expired activation tokens '
                    f'and {expired_password_count} expired password reset tokens'
                )
            )