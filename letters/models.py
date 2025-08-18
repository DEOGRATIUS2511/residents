from django.db import models
from django.conf import settings
from residents.models import Resident

class LetterType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    template_content = models.TextField(help_text="Template with placeholders like {full_name}, {nida_number}, etc.")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class LetterRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    )

    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    )

    # Request Information
    resident = models.ForeignKey(Resident, on_delete=models.CASCADE, related_name='letter_requests')
    letter_type = models.ForeignKey(LetterType, on_delete=models.CASCADE)
    
    # Request Details
    purpose = models.TextField(help_text="Why do you need this letter?")
    additional_info = models.TextField(blank=True, help_text="Any additional information")
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    
    # Status and Workflow
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='requested_letters')
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_letters')
    
    # Timestamps
    request_date = models.DateTimeField(auto_now_add=True)
    approval_date = models.DateTimeField(null=True, blank=True)
    completion_date = models.DateTimeField(null=True, blank=True)
    
    # Admin Notes
    admin_notes = models.TextField(blank=True, help_text="Notes from admin/leader")
    rejection_reason = models.TextField(blank=True)
    
    # Generated Letter
    generated_letter_path = models.FileField(upload_to='generated_letters/', null=True, blank=True)
    
    class Meta:
        ordering = ['-request_date']

    def __str__(self):
        return f"{self.letter_type.name} - {self.resident.full_name} ({self.status})"

class GeneratedLetter(models.Model):
    letter_request = models.OneToOneField(LetterRequest, on_delete=models.CASCADE)
    content = models.TextField()
    pdf_file = models.FileField(upload_to='letters_pdf/')
    generated_at = models.DateTimeField(auto_now_add=True)
    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"Letter for {self.letter_request.resident.full_name} - {self.generated_at.date()}"
