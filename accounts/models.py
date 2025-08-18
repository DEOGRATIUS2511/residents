from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    USER_ROLES = (
        ('admin', 'Local Leader (Admin)'),
        ('resident', 'Resident'),
        ('clerk', 'Data Entry Clerk'),
    )
    
    role = models.CharField(max_length=20, choices=USER_ROLES, default='resident')
    phone_number = models.CharField(max_length=15, blank=True)
    nida_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    profile_photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
