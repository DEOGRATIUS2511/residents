#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ward_system.settings')
django.setup()

from accounts.models import User
from letters.models import LetterType
from residents.models import Household, Resident
from communications.models import Announcement

def create_initial_data():
    # Create superuser
    if not User.objects.filter(username='admin').exists():
        admin_user = User.objects.create_user(
            username='admin',
            email='admin@ward.com',
            password='admin123',
            role='admin',
            is_staff=True,
            is_superuser=True
        )
        print("Created admin user: admin/admin123")
    
    # Create letter types
    letter_types = [
        {
            'name': 'Introduction Letter',
            'description': 'Letter of introduction for residents',
            'template_content': 'This is to certify that {full_name} is a registered resident...'
        },
        {
            'name': 'Residence Certificate',
            'description': 'Certificate of residence',
            'template_content': 'This certifies that {full_name} resides at {address}...'
        },
        {
            'name': 'Good Conduct Letter',
            'description': 'Letter of good conduct',
            'template_content': 'This is to certify that {full_name} is of good conduct...'
        }
    ]
    
    for letter_data in letter_types:
        if not LetterType.objects.filter(name=letter_data['name']).exists():
            LetterType.objects.create(**letter_data)
            print(f"Created letter type: {letter_data['name']}")
    
    # Create sample household
    if not Household.objects.filter(household_number='HH001').exists():
        household = Household.objects.create(
            household_number='HH001',
            street_name='Main Street',
            house_number='123',
            ward='Sample Ward'
        )
        print("Created sample household: HH001")
    
    # Create sample announcement
    if not Announcement.objects.exists():
        admin_user = User.objects.get(username='admin')
        Announcement.objects.create(
            title='Welcome to Ward Management System',
            content='This is a digital platform for efficient ward administration. Residents can now request letters online and track their status.',
            priority='high',
            created_by=admin_user
        )
        print("Created sample announcement")
    
    print("Initial data creation completed!")

if __name__ == '__main__':
    create_initial_data()
