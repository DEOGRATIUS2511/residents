from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.conf import settings
from utils.validators import validate_nida_number, validate_phone_number

class Household(models.Model):
    household_number = models.CharField(max_length=50, unique=True)
    street_name = models.CharField(max_length=100)
    house_number = models.CharField(max_length=20)
    ward = models.CharField(max_length=100, default='Ward Office')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Household {self.household_number} - {self.street_name}"

class Resident(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )
    
    MARITAL_STATUS_CHOICES = (
        ('single', 'Single'),
        ('married', 'Married'),
        ('divorced', 'Divorced'),
        ('widowed', 'Widowed'),
    )
    
    SPECIAL_CATEGORY_CHOICES = (
        ('none', 'None'),
        ('disability', 'Person with Disability'),
        ('elderly', 'Elderly'),
        ('orphan', 'Orphan'),
        ('vulnerable', 'Vulnerable Person'),
    )

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name='residents')
    
    # Personal Information
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50)
    nida_number = models.CharField(max_length=20, unique=True, validators=[validate_nida_number])
    date_of_birth = models.DateField()
    place_of_birth = models.CharField(max_length=100, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    marital_status = models.CharField(max_length=20, choices=MARITAL_STATUS_CHOICES)
    tribe = models.CharField(max_length=50, blank=True)
    religion = models.CharField(max_length=50, blank=True)
    
    # Contact Information
    phone_number = models.CharField(max_length=15, blank=True, validators=[validate_phone_number])
    email = models.EmailField(blank=True)
    
    # Additional Information
    occupation = models.CharField(max_length=100, blank=True)
    education_level = models.CharField(max_length=50, blank=True)
    special_category = models.CharField(max_length=20, choices=SPECIAL_CATEGORY_CHOICES, default='none')
    
    # Relationship to household head
    relationship_to_head = models.CharField(max_length=50, default='Head')
    
    # Photo
    photo = models.ImageField(upload_to='resident_photos/', null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    registration_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.nida_number}"

    @property
    def full_name(self):
        middle = f" {self.middle_name}" if self.middle_name else ""
        return f"{self.first_name}{middle} {self.last_name}"

    @property
    def age(self):
        from datetime import date
        today = date.today()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
