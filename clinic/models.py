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
    name = models.CharField(max_length=50)
    mobile = models.IntegerField(null=True)
    special = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    duration_minutes = models.IntegerField(default=30)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    def __str__(self):
        return self.name

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
    
class Patient(models.Model):
    name = models.CharField(max_length= 50)
    gender = models.CharField(max_length= 10)
    mobile = models.IntegerField(null=True)
    age = models.IntegerField(null=True)
    address = models.CharField(max_length= 10)
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
    patient_name = models.CharField(max_length=100)
    patient_age = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(150)])
    patient_gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    patient_mobile = models.CharField(max_length=15)
    patient_address = models.TextField()
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
        if not self.token:
            self.token = uuid.uuid4().hex[:10].upper()
        super().save(*args, **kwargs)

class Appointment(models.Model):
    doctor = models.ForeignKey(Doctor,on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient,on_delete=models.CASCADE)
    date1 = models.DateField()
    time1 = models.TimeField()

    def __str__(self):
        return self.doctor.name+"--"+ self.patient.name
    

    