from django.core.management.base import BaseCommand
from django.utils import timezone
from clinic.models import Service, Doctor, DoctorSchedule
from datetime import datetime, timedelta, date
import random

class Command(BaseCommand):
    help = 'Setup default services, doctors, and schedules for the clinic booking system'

    def handle(self, *args, **options):
        self.stdout.write('Setting up default clinic data...')
        
        # Create Services
        services_data = [
            {
                'name': 'General Checkup',
                'description': 'Comprehensive health assessment including vital signs, physical examination, and basic health screening.',
                'duration_minutes': 30,
                'price': 1500.00
            },
            {
                'name': 'Consultation',
                'description': 'Specialist consultation for specific health concerns and treatment planning.',
                'duration_minutes': 45,
                'price': 2000.00
            },
            {
                'name': 'Emergency Care',
                'description': 'Urgent medical care for acute conditions and injuries.',
                'duration_minutes': 60,
                'price': 3000.00
            },
            {
                'name': 'Laboratory Tests',
                'description': 'Blood tests, urine analysis, and other diagnostic procedures.',
                'duration_minutes': 20,
                'price': 800.00
            },
            {
                'name': 'Vaccination',
                'description': 'Immunization services including flu shots and travel vaccines.',
                'duration_minutes': 15,
                'price': 500.00
            },
            {
                'name': 'Dental Checkup',
                'description': 'Oral health examination, cleaning, and dental care consultation.',
                'duration_minutes': 40,
                'price': 1200.00
            },
            {
                'name': 'Physiotherapy',
                'description': 'Physical therapy sessions for rehabilitation and pain management.',
                'duration_minutes': 60,
                'price': 2500.00
            },
            {
                'name': 'Mental Health Consultation',
                'description': 'Psychiatric evaluation and counseling services.',
                'duration_minutes': 60,
                'price': 3000.00
            }
        ]
        
        services = []
        for service_data in services_data:
            service, created = Service.objects.get_or_create(
                name=service_data['name'],
                defaults=service_data
            )
            services.append(service)
            if created:
                self.stdout.write(f'Created service: {service.name} - NPR {service.price}')
            else:
                self.stdout.write(f'Service already exists: {service.name}')
        
        # Create Doctors
        doctors_data = [
            {
                'name': 'Dr. Ram Bahadur Thapa',
                'mobile': 9841234567,
                'special': 'General Medicine'
            },
            {
                'name': 'Dr. Sita Devi Shrestha',
                'mobile': 9842345678,
                'special': 'Cardiology'
            },
            {
                'name': 'Dr. Krishna Kumar Tamang',
                'mobile': 9843456789,
                'special': 'Orthopedics'
            },
            {
                'name': 'Dr. Maya Gurung',
                'mobile': 9844567890,
                'special': 'Pediatrics'
            },
            {
                'name': 'Dr. Rajesh Kumar Yadav',
                'mobile': 9845678901,
                'special': 'Dermatology'
            },
            {
                'name': 'Dr. Anjali Sharma',
                'mobile': 9846789012,
                'special': 'Gynecology'
            },
            {
                'name': 'Dr. Bikash Thapa',
                'mobile': 9847890123,
                'special': 'Dental Surgery'
            },
            {
                'name': 'Dr. Priya Karki',
                'mobile': 9848901234,
                'special': 'Psychiatry'
            },
            {
                'name': 'Dr. Santosh Rai',
                'mobile': 9849012345,
                'special': 'Physiotherapy'
            },
            {
                'name': 'Dr. Deepa Basnet',
                'mobile': 9840123456,
                'special': 'Emergency Medicine'
            }
        ]
        
        doctors = []
        for doctor_data in doctors_data:
            doctor, created = Doctor.objects.get_or_create(
                name=doctor_data['name'],
                defaults=doctor_data
            )
            doctors.append(doctor)
            if created:
                self.stdout.write(f'Created doctor: {doctor.name} - {doctor.special}')
            else:
                self.stdout.write(f'Doctor already exists: {doctor.name}')
        
        # Create Doctor Schedules for the next 30 days
        today = date.today()
        
        # Define working hours
        morning_start = datetime.strptime('09:00', '%H:%M').time()
        morning_end = datetime.strptime('12:00', '%H:%M').time()
        afternoon_start = datetime.strptime('14:00', '%H:%M').time()
        afternoon_end = datetime.strptime('17:00', '%H:%M').time()
        
        # Create schedules for each doctor
        schedules_created = 0
        for doctor in doctors:
            # Each doctor works 5 days a week (Monday to Friday)
            for i in range(30):  # Next 30 days
                schedule_date = today + timedelta(days=i)
                
                # Skip weekends (Saturday = 5, Sunday = 6)
                if schedule_date.weekday() >= 5:
                    continue
                
                # Randomly assign services to doctors based on their specialization
                available_services = self.get_services_for_specialization(doctor.special, services)
                
                if not available_services:
                    continue
                
                # Create morning schedule
                service = random.choice(available_services)
                morning_schedule, created = DoctorSchedule.objects.get_or_create(
                    doctor=doctor,
                    service=service,
                    date=schedule_date,
                    start_time=morning_start,
                    end_time=morning_end,
                    defaults={'is_available': True}
                )
                if created:
                    schedules_created += 1
                
                # Create afternoon schedule (different service)
                service = random.choice(available_services)
                afternoon_schedule, created = DoctorSchedule.objects.get_or_create(
                    doctor=doctor,
                    service=service,
                    date=schedule_date,
                    start_time=afternoon_start,
                    end_time=afternoon_end,
                    defaults={'is_available': True}
                )
                if created:
                    schedules_created += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully setup default data:\n'
                f'- {len(services)} services created\n'
                f'- {len(doctors)} doctors created\n'
                f'- {schedules_created} schedules created'
            )
        )
        
        self.stdout.write('\nDefault services with prices (NPR):')
        for service in services:
            self.stdout.write(f'  • {service.name}: NPR {service.price:,.2f}')
        
        self.stdout.write('\nDoctors and their specializations:')
        for doctor in doctors:
            self.stdout.write(f'  • {doctor.name} - {doctor.special}')
    
    def get_services_for_specialization(self, specialization, services):
        """Return appropriate services for each doctor specialization"""
        service_mapping = {
            'General Medicine': ['General Checkup', 'Consultation', 'Laboratory Tests', 'Vaccination'],
            'Cardiology': ['Consultation', 'Laboratory Tests'],
            'Orthopedics': ['Consultation', 'Physiotherapy'],
            'Pediatrics': ['General Checkup', 'Consultation', 'Vaccination'],
            'Dermatology': ['Consultation', 'Laboratory Tests'],
            'Gynecology': ['Consultation', 'Laboratory Tests'],
            'Dental Surgery': ['Dental Checkup', 'Consultation'],
            'Psychiatry': ['Mental Health Consultation', 'Consultation'],
            'Physiotherapy': ['Physiotherapy', 'Consultation'],
            'Emergency Medicine': ['Emergency Care', 'General Checkup']
        }
        
        allowed_service_names = service_mapping.get(specialization, ['General Checkup', 'Consultation'])
        return [service for service in services if service.name in allowed_service_names] 