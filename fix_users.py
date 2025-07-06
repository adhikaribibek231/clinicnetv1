#!/usr/bin/env python
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ClinicNet0.settings')
django.setup()

from django.contrib.auth.models import User
from ClinicNet0.models import UserProfile

def fix_users():
    """Fix user authentication by ensuring users exist with correct credentials"""
    
    print("Checking and fixing user accounts...")
    
    # Create or update clinic user
    clinic_user, created = User.objects.get_or_create(
        username='clinic_user',
        defaults={
            'email': 'clinic@test.com',
            'first_name': 'Clinic',
            'last_name': 'Staff',
            'is_staff': True,
            'is_active': True,
            'is_superuser': False,
        }
    )
    
    if created:
        print(f"Created clinic user: {clinic_user.username}")
    else:
        print(f"Clinic user already exists: {clinic_user.username}")
        # Update existing user to ensure correct settings
        clinic_user.is_staff = True
        clinic_user.is_active = True
        clinic_user.save()
        print("Updated clinic user settings")
    
    # Set password for clinic user
    clinic_user.set_password('clinic123')
    clinic_user.save()
    print("Set password for clinic user")
    
    # Create or update pharmacy user
    pharmacy_user, created = User.objects.get_or_create(
        username='pharmacy_user',
        defaults={
            'email': 'pharmacy@test.com',
            'first_name': 'Pharmacy',
            'last_name': 'Staff',
            'is_staff': True,
            'is_active': True,
            'is_superuser': False,
        }
    )
    
    if created:
        print(f"Created pharmacy user: {pharmacy_user.username}")
    else:
        print(f"Pharmacy user already exists: {pharmacy_user.username}")
        # Update existing user to ensure correct settings
        pharmacy_user.is_staff = True
        pharmacy_user.is_active = True
        pharmacy_user.save()
        print("Updated pharmacy user settings")
    
    # Set password for pharmacy user
    pharmacy_user.set_password('pharmacy123')
    pharmacy_user.save()
    print("Set password for pharmacy user")
    
    # Create or update admin user
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@test.com',
            'first_name': 'Admin',
            'last_name': 'User',
            'is_staff': True,
            'is_active': True,
            'is_superuser': True,
        }
    )
    
    if created:
        print(f"Created admin user: {admin_user.username}")
    else:
        print(f"Admin user already exists: {admin_user.username}")
        # Update existing user to ensure correct settings
        admin_user.is_staff = True
        admin_user.is_active = True
        admin_user.is_superuser = True
        admin_user.save()
        print("Updated admin user settings")
    
    # Set password for admin user
    admin_user.set_password('admin123')
    admin_user.save()
    print("Set password for admin user")
    
    # Test authentication for clinic user
    from django.contrib.auth import authenticate
    test_user = authenticate(username='clinic_user', password='clinic123')
    if test_user and test_user.is_active and test_user.is_staff:
        print("✅ Clinic user authentication test PASSED")
    else:
        print("❌ Clinic user authentication test FAILED")
        print(f"User exists: {test_user is not None}")
        if test_user:
            print(f"User active: {test_user.is_active}")
            print(f"User staff: {test_user.is_staff}")
    
    # Test authentication for pharmacy user
    test_user2 = authenticate(username='pharmacy_user', password='pharmacy123')
    if test_user2 and test_user2.is_active and test_user2.is_staff:
        print("✅ Pharmacy user authentication test PASSED")
    else:
        print("❌ Pharmacy user authentication test FAILED")
    
    print("\n" + "="*50)
    print("USER ACCOUNTS READY FOR TESTING")
    print("="*50)
    print("Clinic User:")
    print("  Username: clinic_user")
    print("  Password: clinic123")
    print("  Status: Active & Staff")
    print()
    print("Pharmacy User:")
    print("  Username: pharmacy_user")
    print("  Password: pharmacy123")
    print("  Status: Active & Staff")
    print()
    print("Admin User:")
    print("  Username: admin")
    print("  Password: admin123")
    print("  Status: Active, Staff & Superuser")
    print()
    print("Try logging in now with clinic_user / clinic123")

if __name__ == '__main__':
    fix_users() 