"""
Custom validators for Ward Resident System
"""
import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

def validate_nida_number(value):
    """Validate Tanzanian NIDA number format"""
    if not re.match(r'^\d{20}$', value):
        raise ValidationError(
            _('NIDA number must be exactly 20 digits'),
            code='invalid_nida'
        )

def validate_phone_number(value):
    """Validate Tanzanian phone number format"""
    # Remove spaces and special characters
    cleaned = re.sub(r'[\s\-\(\)]', '', value)
    
    # Check for valid Tanzanian phone number patterns
    patterns = [
        r'^(\+255|0)(6|7)\d{8}$',  # Mobile numbers
        r'^(\+255|0)(2[2-9])\d{7}$',  # Landline numbers
    ]
    
    if not any(re.match(pattern, cleaned) for pattern in patterns):
        raise ValidationError(
            _('Enter a valid Tanzanian phone number'),
            code='invalid_phone'
        )

def validate_file_size(value):
    """Validate uploaded file size (max 5MB)"""
    filesize = value.size
    if filesize > 5242880:  # 5MB
        raise ValidationError(
            _('File size cannot exceed 5MB'),
            code='file_too_large'
        )

def validate_image_file(value):
    """Validate uploaded image file"""
    validate_file_size(value)
    
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif']
    file_extension = value.name.lower().split('.')[-1]
    
    if f'.{file_extension}' not in allowed_extensions:
        raise ValidationError(
            _('Only JPG, JPEG, PNG, and GIF files are allowed'),
            code='invalid_image_format'
        )
