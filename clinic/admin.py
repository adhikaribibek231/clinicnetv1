from django.contrib import admin
from .models import Doctor, Patient, Appointment, Service, DoctorSchedule, PublicAppointment, ContactMessage, RecurringSchedule, EmergencyService

# Register your models here.
@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('name', 'special', 'mobile', 'email', 'consultation_fee', 'experience')
    list_filter = ('special', 'experience')
    search_fields = ('name', 'special', 'mobile', 'email')
    ordering = ('name',)

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('name', 'gender', 'mobile', 'age', 'created_at')
    list_filter = ('gender', 'created_at')
    search_fields = ('name', 'mobile')
    ordering = ('name',)

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'patient', 'date1', 'time1', 'status')
    list_filter = ('status', 'date1', 'doctor')
    search_fields = ('doctor__name', 'patient__name')
    ordering = ('-date1', '-time1')

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'duration_minutes', 'price')
    list_filter = ('duration_minutes', 'price')
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(DoctorSchedule)
class DoctorScheduleAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'service', 'date', 'start_time', 'end_time', 'is_available')
    list_filter = ('date', 'doctor', 'service', 'is_available')
    search_fields = ('doctor__name', 'service__name')
    date_hierarchy = 'date'
    ordering = ('date', 'start_time')

@admin.register(RecurringSchedule)
class RecurringScheduleAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'service', 'get_day_of_week_display', 'start_time', 'end_time', 'is_active')
    list_filter = ('day_of_week', 'doctor', 'service', 'is_active')
    search_fields = ('doctor__name', 'service__name')
    ordering = ('doctor__name', 'day_of_week', 'start_time')

@admin.register(EmergencyService)
class EmergencyServiceAdmin(admin.ModelAdmin):
    list_display = ('patient_name', 'emergency_type', 'priority', 'status', 'arrival_time', 'attending_doctor')
    list_filter = ('priority', 'status', 'arrival_time', 'attending_doctor')
    search_fields = ('patient_name', 'emergency_type', 'symptoms')
    date_hierarchy = 'arrival_time'
    ordering = ('-arrival_time',)
    
    fieldsets = (
        ('Patient Information', {
            'fields': ('patient_name', 'patient_age', 'patient_gender', 'patient_mobile', 'patient_address', 'emergency_contact', 'patient_email', 'patient')
        }),
        ('Emergency Information', {
            'fields': ('emergency_type', 'symptoms', 'priority', 'status')
        }),
        ('Vital Signs', {
            'fields': ('blood_pressure_systolic', 'blood_pressure_diastolic', 'heart_rate', 'temperature', 'respiratory_rate', 'oxygen_saturation', 'blood_sugar'),
            'classes': ('collapse',)
        }),
        ('Medical Information', {
            'fields': ('allergies', 'current_medications', 'medical_history'),
            'classes': ('collapse',)
        }),
        ('Treatment Information', {
            'fields': ('treatment_plan', 'notes'),
            'classes': ('collapse',)
        }),
        ('Staff Information', {
            'fields': ('attending_doctor', 'nurse_staff')
        }),
        ('Timestamps', {
            'fields': ('arrival_time', 'treatment_start_time', 'completion_time', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('arrival_time', 'updated_at')
    
    actions = ['mark_as_completed', 'mark_as_discharged', 'mark_as_transferred']
    
    def mark_as_completed(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='completed', completion_time=timezone.now())
    mark_as_completed.short_description = "Mark selected emergencies as completed"
    
    def mark_as_discharged(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='discharged', completion_time=timezone.now())
    mark_as_discharged.short_description = "Mark selected emergencies as discharged"
    
    def mark_as_transferred(self, request, queryset):
        queryset.update(status='transferred')
    mark_as_transferred.short_description = "Mark selected emergencies as transferred"

@admin.register(PublicAppointment)
class PublicAppointmentAdmin(admin.ModelAdmin):
    list_display = ('token', 'patient_name', 'doctor', 'service', 'date', 'time', 'status', 'payment_status')
    list_filter = ('status', 'payment_status', 'date', 'doctor', 'service')
    search_fields = ('token', 'patient_name', 'patient_mobile', 'doctor__name')
    date_hierarchy = 'date'
    ordering = ('-date', '-time')

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'phone', 'message')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)