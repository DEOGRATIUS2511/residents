#!/usr/bin/env python
import os
import sys
import django
from datetime import date

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ward_system.settings')
django.setup()

from accounts.models import User
from residents.models import Resident, Household

def create_test_user():
    # Create a test resident user
    if not User.objects.filter(username='testuser').exists():
        user = User.objects.create_user(
            username='testuser',
            email='test@ward.com',
            password='test123',
            role='resident',
            phone_number='+255123456789',
            nida_number='19900101123456789'
        )
        
        # Create household
        household = Household.objects.create(
            household_number='HH002',
            street_name='Uhuru Street',
            house_number='456',
            ward='Test Ward'
        )
        
        # Create resident profile
        resident = Resident.objects.create(
            user=user,
            household=household,
            first_name='John',
            middle_name='Mwalimu',
            last_name='Doe',
            nida_number='19900101123456789',
            date_of_birth=date(1990, 1, 1),
            gender='M',
            marital_status='single',
            phone_number='+255123456789',
            email='test@ward.com',
            occupation='Teacher',
            education_level='University',
            special_category='none',
            relationship_to_head='Head'
        )
        
        print("Created test user:")
        print("Username: testuser")
        print("Password: test123")
        print("Role: Resident")
        print("Profile: Complete with photo placeholder")
    else:
        print("Test user already exists")

if __name__ == '__main__':
    create_test_user()
