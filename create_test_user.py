#!/usr/bin/env python
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ClinicNet0.settings')
django.setup()

from django.contrib.auth.models import User
from ClinicNet0.models import UserProfile

def create_test_users():
    """Create test users for clinic and pharmacy access"""
    
    # Create clinic user
    clinic_user, created = User.objects.get_or_create(
        username='clinic_user',
        defaults={
            'email': 'clinic@test.com',
            'first_name': 'Clinic',
            'last_name': 'Staff',
            'is_staff': True,
            'is_superuser': False,
        }
    )
    
    if created:
        clinic_user.set_password('clinic123')
        clinic_user.save()
        print(f"Created clinic user: {clinic_user.username}")
    else:
        print(f"Clinic user already exists: {clinic_user.username}")
    
    # Create pharmacy user
    pharmacy_user, created = User.objects.get_or_create(
        username='pharmacy_user',
        defaults={
            'email': 'pharmacy@test.com',
            'first_name': 'Pharmacy',
            'last_name': 'Staff',
            'is_staff': True,
            'is_superuser': False,
        }
    )
    
    if created:
        pharmacy_user.set_password('pharmacy123')
        pharmacy_user.save()
        print(f"Created pharmacy user: {pharmacy_user.username}")
    else:
        print(f"Pharmacy user already exists: {pharmacy_user.username}")
    
    # Create admin user
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@test.com',
            'first_name': 'Admin',
            'last_name': 'User',
            'is_staff': True,
            'is_superuser': True,
        }
    )
    
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        print(f"Created admin user: {admin_user.username}")
    else:
        print(f"Admin user already exists: {admin_user.username}")
    
    print("\nTest Users Created:")
    print("===================")
    print("Clinic User:")
    print("  Username: clinic_user")
    print("  Password: clinic123")
    print("  Access: Clinic Management System")
    print()
    print("Pharmacy User:")
    print("  Username: pharmacy_user")
    print("  Password: pharmacy123")
    print("  Access: Pharmacy Management System")
    print()
    print("Admin User:")
    print("  Username: admin")
    print("  Password: admin123")
    print("  Access: Both systems + Django Admin")
    print()
    print("Note: User profiles will be created automatically when users first log in.")

if __name__ == '__main__':
    create_test_users() 