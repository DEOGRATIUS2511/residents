"""
Custom decorators for Ward Resident System
"""
from functools import wraps
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.shortcuts import redirect
from django.core.cache import cache
from django.http import HttpResponse
import time
import logging

logger = logging.getLogger('ward_system')

def role_required(allowed_roles):
    """Decorator to restrict access based on user roles"""
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, 'Please log in to access this page.')
                return redirect('accounts:login')
            
            if request.user.role not in allowed_roles:
                messages.error(request, 'Access denied. Insufficient permissions.')
                logger.warning(f'Access denied for user {request.user.username} to {request.path}')
                return redirect('home')
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def rate_limit(key_prefix, limit=5, window=300):
    """
    Rate limiting decorator that works with both authenticated and anonymous users.
    
    Args:
        key_prefix (str): Prefix for the cache key
        limit (int): Number of requests allowed within the time window
        window (int): Time window in seconds
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Use user ID if authenticated, otherwise fall back to IP
            if request.user.is_authenticated:
                identifier = f"user:{request.user.id}"
                # Staff users are exempt from rate limiting
                if hasattr(request.user, 'is_staff') and request.user.is_staff:
                    return view_func(request, *args, **kwargs)
            else:
                x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                ip = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR', 'unknown')
                identifier = f"ip:{ip}"
            
            # Create cache key with window information
            window_id = int(time.time() / window)
            cache_key = f"ratelimit:{key_prefix}:{identifier}:{window_id}"
            
            # Get current count and remaining time in the window
            current_count = cache.get(cache_key, 0) + 1
            time_elapsed = int(time.time()) % window
            retry_after = window - time_elapsed
            
            if current_count > limit:
                logger.warning(
                    f'Rate limit exceeded: {identifier} on {request.path} '
                    f'({current_count} > {limit} in {window}s)'
                )
                # Render a nice error page with retry information
                response = render(request, 'errors/429.html', 
                               {'retry_after': retry_after}, 
                               status=429)
                response['Retry-After'] = retry_after
                return response
            
            # Set or update the counter with the remaining window time
            cache.set(cache_key, current_count, window - time_elapsed + 1)
            
            # Add rate limit headers to all responses
            response = view_func(request, *args, **kwargs)
            response['X-RateLimit-Limit'] = str(limit)
            response['X-RateLimit-Remaining'] = str(max(0, limit - current_count))
            response['X-RateLimit-Reset'] = str(int(time.time()) + retry_after)
            
            return response
        return _wrapped_view
    return decorator

def log_activity(activity_type):
    """Decorator to log user activities"""
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            start_time = time.time()
            
            try:
                response = view_func(request, *args, **kwargs)
                
                # Log successful activity
                if request.user.is_authenticated:
                    logger.info(f'Activity: {activity_type} by {request.user.username} '
                              f'({request.user.role}) - Duration: {time.time() - start_time:.2f}s')
                
                return response
                
            except Exception as e:
                # Log failed activity
                if request.user.is_authenticated:
                    logger.error(f'Failed activity: {activity_type} by {request.user.username} '
                               f'({request.user.role}) - Error: {str(e)}')
                raise
                
        return _wrapped_view
    return decorator
