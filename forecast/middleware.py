"""
Custom middleware for the forecast app
Handles request/response processing and custom functionality
"""

import logging
from django.http import HttpResponseServerError
from django.template import loader
from django.conf import settings

logger = logging.getLogger(__name__)


def notification_context(request):
    """
    Context processor to add unread notification count to all templates
    """
    if request.user.is_authenticated:
        from .models import Notification
        unread_count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
        return {'unread_notifications_count': unread_count}
    return {'unread_notifications_count': 0}


class ErrorLoggingMiddleware:
    """
    Middleware to log errors and exceptions
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        return response
    
    def process_exception(self, request, exception):
        """Log all exceptions"""
        logger.error(
            f'Exception occurred: {exception}',
            exc_info=True,
            extra={
                'request': request,
                'user': request.user if hasattr(request, 'user') else 'Anonymous'
            }
        )
        
        # Return None to let Django handle the exception normally
        return None


class SecurityHeadersMiddleware:
    """
    Add security headers to all responses
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Only add Strict-Transport-Security in production
        if not settings.DEBUG:
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return response


class UserActivityMiddleware:
    """
    Track user activity for analytics
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Log user activity (can be extended to save to database)
        if request.user.is_authenticated:
            logger.info(f'User {request.user.username} accessed {request.path}')
        
        response = self.get_response(request)
        return response
