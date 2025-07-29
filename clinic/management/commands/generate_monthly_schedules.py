from django.core.management.base import BaseCommand
from django.utils import timezone
from clinic.models import Doctor, RecurringSchedule, DoctorSchedule
from datetime import date, timedelta
import calendar

class Command(BaseCommand):
    help = 'Generate monthly schedules for all doctors based on their recurring patterns'

    def add_arguments(self, parser):
        parser.add_argument(
            '--year',
            type=int,
            help='Year to generate schedules for (default: next month)',
        )
        parser.add_argument(
            '--month',
            type=int,
            help='Month to generate schedules for (default: next month)',
        )
        parser.add_argument(
            '--doctor',
            type=int,
            help='Generate schedules for specific doctor ID only',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force regeneration even if schedules already exist',
        )

    def handle(self, *args, **options):
        # Determine the target month
        today = date.today()
        if options['year'] and options['month']:
            target_year = options['year']
            target_month = options['month']
        else:
            # Default to next month
            if today.month == 12:
                target_year = today.year + 1
                target_month = 1
            else:
                target_year = today.year
                target_month = today.month + 1

        self.stdout.write(f'Generating schedules for {target_year}-{target_month:02d}')

        # Get doctors to process
        if options['doctor']:
            try:
                doctors = [Doctor.objects.get(id=options['doctor'])]
                self.stdout.write(f'Processing doctor ID: {options["doctor"]}')
            except Doctor.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Doctor with ID {options["doctor"]} not found'))
                return
        else:
            doctors = Doctor.objects.all()
            self.stdout.write(f'Processing {doctors.count()} doctors')

        total_schedules_created = 0
        total_doctors_processed = 0

        for doctor in doctors:
            doctor_display_name = doctor.name if doctor.name.startswith('Dr.') else f'Dr. {doctor.name}'
            self.stdout.write(f'Processing {doctor_display_name}...')
            
            # Get active recurring schedules for this doctor
            recurring_schedules = RecurringSchedule.objects.filter(
                doctor=doctor,
                is_active=True
            )
            
            if not recurring_schedules.exists():
                self.stdout.write(f'  No active recurring schedules found for {doctor_display_name}')
                continue

            doctor_schedules_created = 0
            
            for recurring_schedule in recurring_schedules:
                schedules_created = recurring_schedule.generate_schedules_for_month(target_year, target_month)
                doctor_schedules_created += schedules_created
                
                if schedules_created > 0:
                    self.stdout.write(f'  Created {schedules_created} schedules for {recurring_schedule.get_day_of_week_display()} ({recurring_schedule.start_time}-{recurring_schedule.end_time})')
                else:
                    self.stdout.write(f'  No new schedules created for {recurring_schedule.get_day_of_week_display()} (may already exist)')

            total_schedules_created += doctor_schedules_created
            total_doctors_processed += 1
            
            if doctor_schedules_created > 0:
                self.stdout.write(f'  Total schedules created for {doctor_display_name}: {doctor_schedules_created}')
            else:
                self.stdout.write(f'  No new schedules created for {doctor_display_name}')

        self.stdout.write(
            self.style.SUCCESS(
                f'\nSummary: Generated {total_schedules_created} schedules for {total_doctors_processed} doctors in {target_year}-{target_month:02d}'
            )
        )

        # Show some statistics
        start_date = date(target_year, target_month, 1)
        if target_month == 12:
            end_date = date(target_year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(target_year, target_month + 1, 1) - timedelta(days=1)

        total_schedules_in_month = DoctorSchedule.objects.filter(
            date__gte=start_date,
            date__lte=end_date
        ).count()

        self.stdout.write(f'Total schedules in {target_year}-{target_month:02d}: {total_schedules_in_month}') 