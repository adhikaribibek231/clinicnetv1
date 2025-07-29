from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
from datetime import datetime, timedelta
# cmd commands
# py manage.py makemigrations
# py manage.py migrate
# py manage.py shell
#from clinic.models import Doctor, Patient, Appointment
#Doctor.objects.all()

# Create your models here.
class Doctor(models.Model):
    name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15, default='', unique=True)
    special = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True, unique=True)
    qualification = models.CharField(max_length=100, blank=True, null=True)
    experience = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(50)])
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.name

class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    duration_minutes = models.IntegerField(default=30)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.name

class RecurringSchedule(models.Model):
    """Model to store recurring schedule patterns for doctors"""
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    day_of_week = models.IntegerField(choices=[
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ])
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['doctor', 'day_of_week', 'start_time']
        ordering = ['day_of_week', 'start_time']

    def __str__(self):
        return f"{self.doctor.name} - {self.service.name} - {self.get_day_of_week_display()} {self.start_time}"

    def generate_schedules_for_month(self, year, month):
        """Generate DoctorSchedule instances for a specific month based on this recurring pattern"""
        from calendar import monthcalendar
        from datetime import date

        schedules_created = 0
        cal = monthcalendar(year, month)

        for week in cal:
            for day in week:
                if day == 0:  # Empty day
                    continue

                schedule_date = date(year, month, day)

                # Check if this day matches our recurring pattern
                if schedule_date.weekday() == self.day_of_week:
                    # Check if schedule already exists for this date and time
                    existing_schedule = DoctorSchedule.objects.filter(
                        doctor=self.doctor,
                        date=schedule_date,
                        start_time=self.start_time
                    ).first()

                    if not existing_schedule:
                        # Create new schedule
                        DoctorSchedule.objects.create(
                            doctor=self.doctor,
                            service=self.service,
                            date=schedule_date,
                            start_time=self.start_time,
                            end_time=self.end_time,
                            is_available=True
                        )
                        schedules_created += 1

        return schedules_created

class DoctorSchedule(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)

    class Meta:
        unique_together = ['doctor', 'date', 'start_time']

    def __str__(self):
        return f"{self.doctor.name} - {self.service.name} - {self.date} {self.start_time}"

    def get_available_slots(self):
        """Get available time slots for this schedule"""
        slots = []
        current_time = datetime.combine(self.date, self.start_time)
        end_datetime = datetime.combine(self.date, self.end_time)

        while current_time < end_datetime:
            slot_end = current_time + timedelta(minutes=self.service.duration_minutes)
            if slot_end <= end_datetime:
                # Check if this slot is already booked
                if not PublicAppointment.objects.filter(
                    doctor=self.doctor,
                    date=self.date,
                    time=current_time.time()
                ).exists():
                    slots.append(current_time.time())
            current_time = slot_end

        return slots

    @classmethod
    def generate_monthly_schedules(cls, doctor, year, month):
        """Generate all schedules for a doctor for a specific month based on recurring patterns"""
        total_created = 0

        # Get all active recurring schedules for this doctor
        recurring_schedules = RecurringSchedule.objects.filter(
            doctor=doctor,
            is_active=True
        )

        for recurring_schedule in recurring_schedules:
            created = recurring_schedule.generate_schedules_for_month(year, month)
            total_created += created

        return total_created

class Patient(models.Model):
    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    mobile = models.CharField(max_length=15, default='', unique=True)
    age = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(150)])
    address = models.TextField()
    email = models.EmailField(blank=True, null=True, unique=True)
    blood_group = models.CharField(max_length=5, blank=True, null=True,
                                 choices=[('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
                                         ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-')])
    emergency_contact = models.CharField(max_length=15, blank=True, null=True)
    medical_history = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.name

class PublicAppointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    token = models.CharField(max_length=10, unique=True, default=uuid.uuid4().hex[:10].upper())
    # New: Link to Patient if possible
    patient = models.ForeignKey('Patient', on_delete=models.SET_NULL, null=True, blank=True, related_name='public_appointments')
    patient_name = models.CharField(max_length=100)
    patient_age = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(150)])
    patient_gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    patient_mobile = models.CharField(max_length=15)
    patient_address = models.TextField()
    patient_email = models.EmailField(blank=True, null=True)
    emergency_contact = models.CharField(max_length=15, blank=True)

    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('paid', 'Paid')], default='pending')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.token} - {self.patient_name} - {self.doctor.name}"

    def save(self, *args, **kwargs):
        if not self.token or PublicAppointment.objects.filter(token=self.token).exclude(pk=self.pk).exists():
            # Ensure unique token
            for _ in range(5):  # Try up to 5 times
                token = uuid.uuid4().hex[:10].upper()
                if not PublicAppointment.objects.filter(token=token).exists():
                    self.token = token
                    break
            else:
                raise ValueError("Could not generate a unique token for the appointment.")
        super().save(*args, **kwargs)

class Appointment(models.Model):
    doctor = models.ForeignKey(Doctor,on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient,on_delete=models.CASCADE)
    date1 = models.DateField()
    time1 = models.TimeField()
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return self.doctor.name+"--"+ self.patient.name

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=10)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.name} ({self.email}) - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

class EmergencyService(models.Model):
    """Model for emergency patient services and vital signs"""
    PRIORITY_CHOICES = [
        ('critical', 'Critical'),
        ('urgent', 'Urgent'),
        ('stable', 'Stable'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('transferred', 'Transferred'),
        ('discharged', 'Discharged'),
    ]
    
    # Patient Information
    patient_name = models.CharField(max_length=100)
    patient_age = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(150)])
    patient_gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    patient_mobile = models.CharField(max_length=15)
    patient_address = models.TextField()
    emergency_contact = models.CharField(max_length=15, blank=True)
    patient_email = models.EmailField(blank=True, null=True)
    
    # Emergency Information
    emergency_type = models.CharField(max_length=100, help_text="Type of emergency (e.g., Chest Pain, Accident, Fever)")
    symptoms = models.TextField(help_text="Patient's symptoms and complaints")
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='stable')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Vital Signs
    blood_pressure_systolic = models.IntegerField(blank=True, null=True, help_text="Systolic BP (mmHg)")
    blood_pressure_diastolic = models.IntegerField(blank=True, null=True, help_text="Diastolic BP (mmHg)")
    heart_rate = models.IntegerField(blank=True, null=True, help_text="Heart rate (bpm)")
    temperature = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True, help_text="Temperature (°C)")
    respiratory_rate = models.IntegerField(blank=True, null=True, help_text="Respiratory rate (breaths/min)")
    oxygen_saturation = models.IntegerField(blank=True, null=True, help_text="Oxygen saturation (%)")
    blood_sugar = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True, help_text="Blood sugar (mg/dL)")
    
    # Medical Information
    allergies = models.TextField(blank=True, help_text="Known allergies")
    current_medications = models.TextField(blank=True, help_text="Current medications")
    medical_history = models.TextField(blank=True, help_text="Relevant medical history")
    
    # Treatment Information
    treatment_plan = models.TextField(blank=True, help_text="Treatment plan and medications given")
    notes = models.TextField(blank=True, help_text="Additional notes")
    
    # Staff Information
    attending_doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True)
    nurse_staff = models.CharField(max_length=100, blank=True, help_text="Nurse or staff member on duty")
    
    # Timestamps
    arrival_time = models.DateTimeField(auto_now_add=True)
    treatment_start_time = models.DateTimeField(blank=True, null=True)
    completion_time = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Link to Patient (if found)
    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True, blank=True, related_name='emergency_services')
    
    class Meta:
        ordering = ['-arrival_time']
    
    def __str__(self):
        return f"Emergency: {self.patient_name} - {self.emergency_type} ({self.priority})"
    
    def get_blood_pressure_display(self):
        """Get formatted blood pressure display"""
        if self.blood_pressure_systolic and self.blood_pressure_diastolic:
            return f"{self.blood_pressure_systolic}/{self.blood_pressure_diastolic} mmHg"
        return "Not recorded"
    
    def get_vital_signs_summary(self):
        """Get a summary of vital signs"""
        vitals = []
        if self.blood_pressure_systolic and self.blood_pressure_diastolic:
            vitals.append(f"BP: {self.blood_pressure_systolic}/{self.blood_pressure_diastolic}")
        if self.heart_rate:
            vitals.append(f"HR: {self.heart_rate} bpm")
        if self.temperature:
            vitals.append(f"Temp: {self.temperature}°C")
        if self.oxygen_saturation:
            vitals.append(f"O2: {self.oxygen_saturation}%")
        return ", ".join(vitals) if vitals else "No vitals recorded"
    
    def get_priority_color(self):
        """Get CSS color class for priority"""
        colors = {
            'critical': 'danger',
            'urgent': 'warning', 
            'stable': 'success'
        }
        return colors.get(self.priority, 'secondary')
    
    def get_status_color(self):
        """Get CSS color class for status"""
        colors = {
            'active': 'primary',
            'completed': 'success',
            'transferred': 'info',
            'discharged': 'secondary'
        }
        return colors.get(self.status, 'secondary')
    
    def duration_minutes(self):
        """Calculate duration in minutes"""
        if self.completion_time:
            duration = self.completion_time - self.arrival_time
            return int(duration.total_seconds() / 60)
        return None
    

    