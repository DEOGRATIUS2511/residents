from django.db import models
from django.conf import settings
from residents.models import Household

class Visitor(models.Model):
    VISIT_PURPOSE_CHOICES = (
        ('business', 'Business'),
        ('family', 'Family Visit'),
        ('official', 'Official Business'),
        ('service', 'Service Provider'),
        ('other', 'Other'),
    )

    # Visitor Information
    full_name = models.CharField(max_length=100)
    id_number = models.CharField(max_length=20, help_text="National ID or other identification")
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(help_text="Visitor's home address")
    
    # Visit Details
    household_visited = models.ForeignKey(Household, on_delete=models.CASCADE, related_name='visitors')
    person_visited = models.CharField(max_length=100, help_text="Name of person being visited")
    purpose = models.CharField(max_length=20, choices=VISIT_PURPOSE_CHOICES)
    purpose_details = models.TextField(blank=True, help_text="Additional details about the visit")
    
    # Entry/Exit Information
    entry_time = models.DateTimeField()
    expected_exit_time = models.DateTimeField(null=True, blank=True)
    actual_exit_time = models.DateTimeField(null=True, blank=True)
    
    # Staff Information
    registered_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='registered_visitors')
    
    # Status
    is_active = models.BooleanField(default=True, help_text="Is the visitor currently in the area?")
    notes = models.TextField(blank=True, help_text="Additional notes or observations")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-entry_time']

    def __str__(self):
        return f"{self.full_name} visiting {self.person_visited} at {self.household_visited}"

    @property
    def is_currently_visiting(self):
        return self.is_active and self.actual_exit_time is None

class VisitorLog(models.Model):
    """Track all visitor activities and status changes"""
    visitor = models.ForeignKey(Visitor, on_delete=models.CASCADE, related_name='logs')
    action = models.CharField(max_length=50, help_text="Action taken (entry, exit, status_change, etc.)")
    description = models.TextField()
    performed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.visitor.full_name} - {self.action} at {self.timestamp}"
