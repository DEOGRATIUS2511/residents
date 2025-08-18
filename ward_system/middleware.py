"""
Custom middleware for Ward Resident System
"""
import logging
from django.utils import timezone
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponseServerError
from django.template import loader
from django.conf import settings

logger = logging.getLogger('ward_system')

class AuditTrailMiddleware:
    """Log user activities for audit purposes"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Log request details
        if not isinstance(request.user, AnonymousUser) and request.user.is_authenticated:
            logger.info(f"User {request.user.username} ({request.user.role}) accessed {request.path} from {self.get_client_ip(request)}")
        
        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class SecurityHeadersMiddleware:
    """Add security headers to responses"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        return response

class ErrorHandlingMiddleware:
    """Custom error handling for production"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        if not settings.DEBUG:
            logger.error(f"Unhandled exception: {exception}", exc_info=True)
            
            # Return custom error page
            template = loader.get_template('errors/500.html')
            return HttpResponseServerError(template.render({
                'error_message': 'An error occurred. Please try again later.',
                'support_email': getattr(settings, 'SUPPORT_EMAIL', 'support@ward-system.go.tz')
            }))
