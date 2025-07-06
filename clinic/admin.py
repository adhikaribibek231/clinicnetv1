from django.contrib import admin
from .models import Doctor, Patient, Appointment, Service, DoctorSchedule, PublicAppointment

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('name', 'special', 'mobile')
    search_fields = ('name', 'special')
    list_filter = ('special',)

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('name', 'gender', 'age', 'mobile', 'address')
    search_fields = ('name', 'mobile')
    list_filter = ('gender', 'age')

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'patient', 'date1', 'time1')
    list_filter = ('date1', 'doctor', 'patient')
    search_fields = ('doctor__name', 'patient__name')
    date_hierarchy = 'date1'

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'duration_minutes', 'price')
    search_fields = ('name',)
    list_filter = ('duration_minutes',)

@admin.register(DoctorSchedule)
class DoctorScheduleAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'service', 'date', 'start_time', 'end_time', 'is_available')
    list_filter = ('date', 'doctor', 'service', 'is_available')
    search_fields = ('doctor__name', 'service__name')
    date_hierarchy = 'date'
    ordering = ('date', 'start_time')

@admin.register(PublicAppointment)
class PublicAppointmentAdmin(admin.ModelAdmin):
    list_display = ('token', 'patient_name', 'doctor', 'service', 'date', 'time', 'status', 'payment_status')
    list_filter = ('status', 'payment_status', 'date', 'doctor', 'service')
    search_fields = ('token', 'patient_name', 'patient_mobile', 'doctor__name')
    date_hierarchy = 'date'
    ordering = ('-created_at',)
    readonly_fields = ('token', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Appointment Information', {
            'fields': ('token', 'status', 'payment_status', 'notes')
        }),
        ('Patient Information', {
            'fields': ('patient_name', 'patient_age', 'patient_gender', 'patient_mobile', 'patient_address', 'emergency_contact')
        }),
        ('Appointment Details', {
            'fields': ('doctor', 'service', 'date', 'time')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_confirmed', 'mark_as_completed', 'mark_as_cancelled', 'mark_as_paid']
    
    def mark_as_confirmed(self, request, queryset):
        queryset.update(status='confirmed')
    mark_as_confirmed.short_description = "Mark selected appointments as confirmed"
    
    def mark_as_completed(self, request, queryset):
        queryset.update(status='completed')
    mark_as_completed.short_description = "Mark selected appointments as completed"
    
    def mark_as_cancelled(self, request, queryset):
        queryset.update(status='cancelled')
    mark_as_cancelled.short_description = "Mark selected appointments as cancelled"
    
    def mark_as_paid(self, request, queryset):
        queryset.update(payment_status='paid')
    mark_as_paid.short_description = "Mark selected appointments as paid"