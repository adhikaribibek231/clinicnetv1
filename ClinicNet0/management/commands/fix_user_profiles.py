from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from ClinicNet0.models import UserProfile

class Command(BaseCommand):
    help = 'Fixes the user profiles for clinic_user and pharmacy_user'

    def handle(self, *args, **options):
        # Correct clinic_user
        try:
            clinic_user = User.objects.get(username='clinic_user')
            clinic_profile, created = UserProfile.objects.get_or_create(user=clinic_user)
            if clinic_profile.user_type != 'clinic':
                clinic_profile.user_type = 'clinic'
                clinic_profile.save()
                self.stdout.write(self.style.SUCCESS('Successfully fixed clinic_user profile.'))
            else:
                self.stdout.write(self.style.NOTICE('clinic_user profile is already correct.'))
        except User.DoesNotExist:
            self.stdout.write(self.style.WARNING('clinic_user not found.'))

        # Correct pharmacy_user
        try:
            pharmacy_user = User.objects.get(username='pharmacy_user')
            pharmacy_profile, created = UserProfile.objects.get_or_create(user=pharmacy_user)
            if pharmacy_profile.user_type != 'pharmacy':
                pharmacy_profile.user_type = 'pharmacy'
                pharmacy_profile.save()
                self.stdout.write(self.style.SUCCESS('Successfully fixed pharmacy_user profile.'))
            else:
                self.stdout.write(self.style.NOTICE('pharmacy_user profile is already correct.'))
        except User.DoesNotExist:
            self.stdout.write(self.style.WARNING('pharmacy_user not found.')) 