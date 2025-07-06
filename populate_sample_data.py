#!/usr/bin/env python
"""
Management script to populate the database with sample data for testing and demonstration.
Run this script to add sample doctors, patients, services, and appointments.
"""

import os
import sys
import django
from datetime import datetime, timedelta, date
import random
import uuid

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ClinicNet0.settings')
django.setup()

from clinic.models import Doctor, Patient, Service, DoctorSchedule, PublicAppointment
from django.utils import timezone

def create_sample_services():
    """Create sample medical services"""
    services_data = [
        {
            'name': 'General Consultation',
            'description': 'Basic health checkup and consultation',
            'duration_minutes': 30,
            'price': 500.00
        },
        {
            'name': 'Cardiology Consultation',
            'description': 'Heart and cardiovascular system examination',
            'duration_minutes': 45,
            'price': 1500.00
        },
        {
            'name': 'Dermatology Consultation',
            'description': 'Skin, hair, and nail examination',
            'duration_minutes': 30,
            'price': 800.00
        },
        {
            'name': 'Orthopedic Consultation',
            'description': 'Bone and joint examination',
            'duration_minutes': 45,
            'price': 1200.00
        },
        {
            'name': 'Pediatric Consultation',
            'description': 'Child health and development checkup',
            'duration_minutes': 30,
            'price': 600.00
        },
        {
            'name': 'Gynecology Consultation',
            'description': 'Women\'s health examination',
            'duration_minutes': 45,
            'price': 1000.00
        },
        {
            'name': 'Neurology Consultation',
            'description': 'Brain and nervous system examination',
            'duration_minutes': 60,
            'price': 2000.00
        },
        {
            'name': 'ENT Consultation',
            'description': 'Ear, nose, and throat examination',
            'duration_minutes': 30,
            'price': 700.00
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
            print(f"Created service: {service.name}")
        else:
            print(f"Service already exists: {service.name}")
    
    return services

def create_sample_doctors():
    """Create sample doctors with complete information"""
    doctors_data = [
        {
            'name': 'Dr. Rajesh Kumar',
            'mobile': '9841234567',
            'special': 'Cardiology',
            'email': 'rajesh.kumar@clinicnet.com',
            'qualification': 'MBBS, MD (Cardiology)',
            'experience': 15,
            'consultation_fee': 1500.00
        },
        {
            'name': 'Dr. Priya Sharma',
            'mobile': '9852345678',
            'special': 'Dermatology',
            'email': 'priya.sharma@clinicnet.com',
            'qualification': 'MBBS, MD (Dermatology)',
            'experience': 12,
            'consultation_fee': 800.00
        },
        {
            'name': 'Dr. Amit Patel',
            'mobile': '9863456789',
            'special': 'Orthopedics',
            'email': 'amit.patel@clinicnet.com',
            'qualification': 'MBBS, MS (Orthopedics)',
            'experience': 18,
            'consultation_fee': 1200.00
        },
        {
            'name': 'Dr. Sunita Devi',
            'mobile': '9874567890',
            'special': 'Pediatrics',
            'email': 'sunita.devi@clinicnet.com',
            'qualification': 'MBBS, MD (Pediatrics)',
            'experience': 10,
            'consultation_fee': 600.00
        },
        {
            'name': 'Dr. Ramesh Singh',
            'mobile': '9885678901',
            'special': 'General Medicine',
            'email': 'ramesh.singh@clinicnet.com',
            'qualification': 'MBBS, MD (General Medicine)',
            'experience': 20,
            'consultation_fee': 500.00
        },
        {
            'name': 'Dr. Meera Joshi',
            'mobile': '9896789012',
            'special': 'Gynecology',
            'email': 'meera.joshi@clinicnet.com',
            'qualification': 'MBBS, MS (Gynecology)',
            'experience': 14,
            'consultation_fee': 1000.00
        },
        {
            'name': 'Dr. Vikram Malhotra',
            'mobile': '9807890123',
            'special': 'Neurology',
            'email': 'vikram.malhotra@clinicnet.com',
            'qualification': 'MBBS, MD (Neurology)',
            'experience': 16,
            'consultation_fee': 2000.00
        },
        {
            'name': 'Dr. Anjali Gupta',
            'mobile': '9818901234',
            'special': 'ENT',
            'email': 'anjali.gupta@clinicnet.com',
            'qualification': 'MBBS, MS (ENT)',
            'experience': 11,
            'consultation_fee': 700.00
        }
    ]
    
    doctors = []
    for doctor_data in doctors_data:
        doctor, created = Doctor.objects.get_or_create(
            mobile=doctor_data['mobile'],
            defaults=doctor_data
        )
        doctors.append(doctor)
        if created:
            print(f"Created doctor: {doctor.name} - {doctor.special}")
        else:
            print(f"Doctor already exists: {doctor.name}")
    
    return doctors

def create_sample_patients():
    """Create sample patients with complete information"""
    patients_data = [
        {
            'name': 'Arjun Thapa',
            'gender': 'Male',
            'mobile': '9841111111',
            'age': 35,
            'address': 'Baneshwor, Kathmandu',
            'email': 'arjun.thapa@email.com',
            'blood_group': 'A+',
            'emergency_contact': '9842222222',
            'medical_history': 'Hypertension, Diabetes'
        },
        {
            'name': 'Sita Tamang',
            'gender': 'Female',
            'mobile': '9843333333',
            'age': 28,
            'address': 'Lalitpur, Nepal',
            'email': 'sita.tamang@email.com',
            'blood_group': 'B+',
            'emergency_contact': '9844444444',
            'medical_history': 'Asthma'
        },
        {
            'name': 'Bikash Gurung',
            'gender': 'Male',
            'mobile': '9845555555',
            'age': 42,
            'address': 'Pokhara, Nepal',
            'email': 'bikash.gurung@email.com',
            'blood_group': 'O+',
            'emergency_contact': '9846666666',
            'medical_history': 'None'
        },
        {
            'name': 'Puja Rai',
            'gender': 'Female',
            'mobile': '9847777777',
            'age': 25,
            'address': 'Bhaktapur, Nepal',
            'email': 'puja.rai@email.com',
            'blood_group': 'AB+',
            'emergency_contact': '9848888888',
            'medical_history': 'Allergies'
        },
        {
            'name': 'Nepal Magar',
            'gender': 'Male',
            'mobile': '9849999999',
            'age': 50,
            'address': 'Dharan, Nepal',
            'email': 'nepal.magar@email.com',
            'blood_group': 'A-',
            'emergency_contact': '9840000000',
            'medical_history': 'Heart disease, High cholesterol'
        },
        {
            'name': 'Rita Limbu',
            'gender': 'Female',
            'mobile': '9841111222',
            'age': 32,
            'address': 'Biratnagar, Nepal',
            'email': 'rita.limbu@email.com',
            'blood_group': 'B-',
            'emergency_contact': '9842222333',
            'medical_history': 'Migraine'
        },
        {
            'name': 'Krishna Shrestha',
            'gender': 'Male',
            'mobile': '9843333444',
            'age': 38,
            'address': 'Chitwan, Nepal',
            'email': 'krishna.shrestha@email.com',
            'blood_group': 'O-',
            'emergency_contact': '9844444555',
            'medical_history': 'None'
        },
        {
            'name': 'Anita Basnet',
            'gender': 'Female',
            'mobile': '9845555666',
            'age': 29,
            'address': 'Butwal, Nepal',
            'email': 'anita.basnet@email.com',
            'blood_group': 'AB-',
            'emergency_contact': '9846666777',
            'medical_history': 'Thyroid disorder'
        },
        {
            'name': 'Hari Poudel',
            'gender': 'Male',
            'mobile': '9847777888',
            'age': 45,
            'address': 'Nepalgunj, Nepal',
            'email': 'hari.poudel@email.com',
            'blood_group': 'A+',
            'emergency_contact': '9848888999',
            'medical_history': 'Diabetes'
        },
        {
            'name': 'Maya Karki',
            'gender': 'Female',
            'mobile': '9849999000',
            'age': 27,
            'address': 'Dhangadhi, Nepal',
            'email': 'maya.karki@email.com',
            'blood_group': 'B+',
            'emergency_contact': '9840000111',
            'medical_history': 'None'
        }
    ]
    
    patients = []
    for patient_data in patients_data:
        patient, created = Patient.objects.get_or_create(
            mobile=patient_data['mobile'],
            defaults=patient_data
        )
        patients.append(patient)
        if created:
            print(f"Created patient: {patient.name} - {patient.age} years")
        else:
            print(f"Patient already exists: {patient.name}")
    
    return patients

def create_sample_schedules(doctors, services):
    """Create sample doctor schedules"""
    today = date.today()
    
    # Map doctors to their corresponding services
    doctor_service_map = {
        'Cardiology': 'Cardiology Consultation',
        'Dermatology': 'Dermatology Consultation',
        'Orthopedics': 'Orthopedic Consultation',
        'Pediatrics': 'Pediatric Consultation',
        'General Medicine': 'General Consultation',
        'Gynecology': 'Gynecology Consultation',
        'Neurology': 'Neurology Consultation',
        'ENT': 'ENT Consultation'
    }
    
    schedules_created = 0
    
    for doctor in doctors:
        # Find the corresponding service for this doctor
        service_name = doctor_service_map.get(doctor.special)
        if service_name:
            service = next((s for s in services if s.name == service_name), None)
        else:
            service = services[0]  # Default to first service
        
        if not service:
            continue
        
        # Create schedules for the next 7 days
        for i in range(7):
            schedule_date = today + timedelta(days=i)
            
            # Check if morning schedule already exists
            morning_exists = DoctorSchedule.objects.filter(
                doctor=doctor,
                date=schedule_date,
                start_time=datetime.strptime('09:00', '%H:%M').time()
            ).exists()
            
            if not morning_exists:
                morning_schedule = DoctorSchedule.objects.create(
                    doctor=doctor,
                    service=service,
                    date=schedule_date,
                    start_time=datetime.strptime('09:00', '%H:%M').time(),
                    end_time=datetime.strptime('12:00', '%H:%M').time(),
                    is_available=True
                )
                schedules_created += 1
            
            # Check if afternoon schedule already exists
            afternoon_exists = DoctorSchedule.objects.filter(
                doctor=doctor,
                date=schedule_date,
                start_time=datetime.strptime('14:00', '%H:%M').time()
            ).exists()
            
            if not afternoon_exists:
                afternoon_schedule = DoctorSchedule.objects.create(
                    doctor=doctor,
                    service=service,
                    date=schedule_date,
                    start_time=datetime.strptime('14:00', '%H:%M').time(),
                    end_time=datetime.strptime('17:00', '%H:%M').time(),
                    is_available=True
                )
                schedules_created += 1
    
    print(f"Created {schedules_created} doctor schedules")

def create_sample_appointments(doctors, services):
    """Create sample appointments"""
    today = date.today()
    
    # Sample appointment data
    appointments_data = [
        {
            'patient_name': 'Arjun Thapa',
            'patient_age': 35,
            'patient_gender': 'Male',
            'patient_mobile': '9841111111',
            'patient_address': 'Baneshwor, Kathmandu',
            'emergency_contact': '9842222222',
            'doctor_special': 'Cardiology',
            'service_name': 'Cardiology Consultation',
            'date': today + timedelta(days=1),
            'time': '09:30',
            'status': 'confirmed',
            'payment_status': 'paid'
        },
        {
            'patient_name': 'Sita Tamang',
            'patient_age': 28,
            'patient_gender': 'Female',
            'patient_mobile': '9843333333',
            'patient_address': 'Lalitpur, Nepal',
            'emergency_contact': '9844444444',
            'doctor_special': 'Dermatology',
            'service_name': 'Dermatology Consultation',
            'date': today + timedelta(days=2),
            'time': '14:30',
            'status': 'pending',
            'payment_status': 'pending'
        },
        {
            'patient_name': 'Bikash Gurung',
            'patient_age': 42,
            'patient_gender': 'Male',
            'patient_mobile': '9845555555',
            'patient_address': 'Pokhara, Nepal',
            'emergency_contact': '9846666666',
            'doctor_special': 'Orthopedics',
            'service_name': 'Orthopedic Consultation',
            'date': today + timedelta(days=1),
            'time': '15:00',
            'status': 'confirmed',
            'payment_status': 'paid'
        },
        {
            'patient_name': 'Puja Rai',
            'patient_age': 25,
            'patient_gender': 'Female',
            'patient_mobile': '9847777777',
            'patient_address': 'Bhaktapur, Nepal',
            'emergency_contact': '9848888888',
            'doctor_special': 'General Medicine',
            'service_name': 'General Consultation',
            'date': today,
            'time': '10:00',
            'status': 'completed',
            'payment_status': 'paid'
        },
        {
            'patient_name': 'Nepal Magar',
            'patient_age': 50,
            'patient_gender': 'Male',
            'patient_mobile': '9849999999',
            'patient_address': 'Dharan, Nepal',
            'emergency_contact': '9840000000',
            'doctor_special': 'Cardiology',
            'service_name': 'Cardiology Consultation',
            'date': today + timedelta(days=3),
            'time': '11:00',
            'status': 'pending',
            'payment_status': 'pending'
        },
        {
            'patient_name': 'Rita Limbu',
            'patient_age': 32,
            'patient_gender': 'Female',
            'patient_mobile': '9841111222',
            'patient_address': 'Biratnagar, Nepal',
            'emergency_contact': '9842222333',
            'doctor_special': 'Neurology',
            'service_name': 'Neurology Consultation',
            'date': today + timedelta(days=2),
            'time': '16:00',
            'status': 'confirmed',
            'payment_status': 'paid'
        },
        {
            'patient_name': 'Krishna Shrestha',
            'patient_age': 38,
            'patient_gender': 'Male',
            'patient_mobile': '9843333444',
            'patient_address': 'Chitwan, Nepal',
            'emergency_contact': '9844444555',
            'doctor_special': 'ENT',
            'service_name': 'ENT Consultation',
            'date': today + timedelta(days=1),
            'time': '14:00',
            'status': 'pending',
            'payment_status': 'pending'
        },
        {
            'patient_name': 'Anita Basnet',
            'patient_age': 29,
            'patient_gender': 'Female',
            'patient_mobile': '9845555666',
            'patient_address': 'Butwal, Nepal',
            'emergency_contact': '9846666777',
            'doctor_special': 'Gynecology',
            'service_name': 'Gynecology Consultation',
            'date': today + timedelta(days=4),
            'time': '09:00',
            'status': 'confirmed',
            'payment_status': 'paid'
        }
    ]
    
    appointments_created = 0
    
    for appt_data in appointments_data:
        # Find the doctor by specialization
        doctor = next((d for d in doctors if d.special == appt_data['doctor_special']), None)
        if not doctor:
            continue
        
        # Find the service
        service = next((s for s in services if s.name == appt_data['service_name']), None)
        if not service:
            continue
        
        # Generate a unique token
        for _ in range(5):  # Try up to 5 times
            token = uuid.uuid4().hex[:10].upper()
            if not PublicAppointment.objects.filter(token=token).exists():
                break
        else:
            print("Could not generate unique token for appointment, skipping.")
            continue
        
        # Create appointment
        appointment = PublicAppointment.objects.create(
            token=token,
            patient_name=appt_data['patient_name'],
            patient_age=appt_data['patient_age'],
            patient_gender=appt_data['patient_gender'],
            patient_mobile=appt_data['patient_mobile'],
            patient_address=appt_data['patient_address'],
            emergency_contact=appt_data['emergency_contact'],
            doctor=doctor,
            service=service,
            date=appt_data['date'],
            time=datetime.strptime(appt_data['time'], '%H:%M').time(),
            status=appt_data['status'],
            payment_status=appt_data['payment_status'],
            notes=f"Sample appointment for {appt_data['patient_name']}"
        )
        
        appointments_created += 1
        print(f"Created appointment: {appointment.token} - {appointment.patient_name} with Dr. {doctor.name}")
    
    print(f"Created {appointments_created} appointments")

def main():
    """Main function to populate all sample data"""
    print("Starting to populate sample data...")
    print("=" * 50)
    
    # Create services
    print("\n1. Creating services...")
    services = create_sample_services()
    
    # Create doctors
    print("\n2. Creating doctors...")
    doctors = create_sample_doctors()
    
    # Create patients
    print("\n3. Creating patients...")
    patients = create_sample_patients()
    
    # Create schedules
    print("\n4. Creating doctor schedules...")
    create_sample_schedules(doctors, services)
    
    # Create appointments
    print("\n5. Creating appointments...")
    create_sample_appointments(doctors, services)
    
    print("\n" + "=" * 50)
    print("Sample data population completed!")
    print(f"Total services: {Service.objects.count()}")
    print(f"Total doctors: {Doctor.objects.count()}")
    print(f"Total patients: {Patient.objects.count()}")
    print(f"Total schedules: {DoctorSchedule.objects.count()}")
    print(f"Total appointments: {PublicAppointment.objects.count()}")

if __name__ == '__main__':
    main() 