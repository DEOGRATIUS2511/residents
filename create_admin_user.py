#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ward_system.settings')
django.setup()

from accounts.models import User

def create_admin_user():
    # Create an admin user
    if not User.objects.filter(username='admin').exists():
        user = User.objects.create_user(
            username='admin',
            email='admin@ward.com',
            password='admin123',
            role='admin',
            phone_number='+255700000000',
            nida_number='19800101000000000'
        )
        user.is_staff = True
        user.is_superuser = True
        user.save()
        
        print("Created admin user:")
        print("Username: admin")
        print("Password: admin123")
        print("Role: Admin")
        print("Can approve letter requests and manage system")
    else:
        print("Admin user already exists")

if __name__ == '__main__':
    create_admin_user()
