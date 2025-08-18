"""
Email utilities for Ward Resident System
"""
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import logging

logger = logging.getLogger('ward_system')

def send_letter_approval_notification(letter_request):
    """Send email notification when letter is approved"""
    try:
        if not letter_request.requested_by.email:
            logger.warning(f'No email address for user {letter_request.requested_by.username}')
            return False
            
        subject = f'Letter Request Approved - {letter_request.letter_type.name}'
        
        context = {
            'resident_name': letter_request.resident.full_name,
            'letter_type': letter_request.letter_type.name,
            'request_date': letter_request.request_date,
            'approval_date': letter_request.approval_date,
            'download_url': f'/letters/generate-pdf/{letter_request.id}/',
        }
        
        message = render_to_string('emails/letter_approved.html', context)
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[letter_request.requested_by.email],
            html_message=message,
            fail_silently=False,
        )
        
        logger.info(f'Approval notification sent to {letter_request.requested_by.email}')
        return True
        
    except Exception as e:
        logger.error(f'Failed to send approval notification: {e}')
        return False

def send_system_alert(subject, message, recipient_list=None):
    """Send system alert to administrators"""
    try:
        if not recipient_list:
            recipient_list = [admin[1] for admin in settings.ADMINS]
            
        if not recipient_list:
            logger.warning('No admin email addresses configured')
            return False
            
        send_mail(
            subject=f'[Ward System Alert] {subject}',
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=False,
        )
        
        logger.info(f'System alert sent: {subject}')
        return True
        
    except Exception as e:
        logger.error(f'Failed to send system alert: {e}')
        return False
