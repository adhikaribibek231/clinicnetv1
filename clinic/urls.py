from django.contrib import admin
from django.urls import path, include
from clinic.views import *

app_name = 'clinic'

urlpatterns = [
    path('dashboard/', Index, name='dashboard'),  # Admin dashboard
    path('admin_login/', Login, name='login'),
    path('logout/', Logout_admin, name='logout'),
    path('about/', About, name='about_protected'),  # Protected about page
    path('contact/', Contact, name='contact_protected'),  # Protected contact page
    path('view_doctor/', View_Doctor, name='view_doctor'),
    path('add_doctor/', Add_Doctor, name='add_doctor'),
    path('edit_doctor/<int:doctor_id>/', Edit_Doctor, name='edit_doctor'),
    path('delete_doctor/<int:pid>/', Delete_Doctor, name='delete_doctor'),
    path('delete_patient/<int:pid>/', Delete_Patient, name='delete_patient'),

    path('view_patient/', View_Patient, name='view_patient'),
    path('add_patient/', Add_Patient, name='add_patient'),
    path('edit_patient/<int:patient_id>/', Edit_Patient, name='edit_patient'),
    path('patient/<int:patient_id>/', view_patient_detail, name='view_patient_detail'),

    path('view_appointment/', View_Appointment, name='view_appointment'),
    path('add_appointment/', Add_Appointment, name='add_appointment'),
    path('edit_appointment/<int:appointment_id>/', Edit_Appointment, name='edit_appointment'),
    path('delete-appointment/<int:aid>/', Delete_Appointment, name='delete_appointment'),

    # Public appointment booking URLs
    path('book/', BookAppointment, name='book_appointment'),
    path('api/doctors/', get_available_doctors, name='get_available_doctors'),
    path('api/dates/', get_available_dates, name='get_available_dates'),
    path('api/times/', get_available_times, name='get_available_times'),
    path('api/confirm/', confirm_appointment, name='confirm_appointment'),
    path('api/admin-confirm/', confirm_admin_appointment, name='confirm_admin_appointment'),
    path('confirmation/<str:token>/', appointment_confirmation, name='appointment_confirmation'),
    path('download/<str:token>/', download_token, name='download_token'),
    
    # Schedule Management URLs
    path('schedules/', View_Schedules, name='view_schedules'),
    path('update-availability/<int:doctor_id>/', Update_Doctor_Availability, name='update_doctor_availability'),
    
    # Service Management URLs
    path('manage-services/', Manage_Services, name='manage_services'),

    # Doctor Schedule Management URLs
    path('doctor-schedules/', doctor_schedules_overview, name='doctor_schedules_overview'),
    path('doctor-schedules/<int:doctor_id>/', doctor_schedule_calendar, name='doctor_schedule_calendar'),
    path('doctor-schedules/<int:doctor_id>/add/', add_schedule_ajax, name='add_schedule_ajax'),
    path('doctor-schedules/<int:doctor_id>/update/<int:schedule_id>/', update_schedule_ajax, name='update_schedule_ajax'),
    path('doctor-schedules/<int:doctor_id>/delete/<int:schedule_id>/', delete_schedule_ajax, name='delete_schedule_ajax'),
    path('doctor-schedules/<int:doctor_id>/details/<int:schedule_id>/', get_schedule_details_ajax, name='get_schedule_details_ajax'),

    #test modal
    path('test-modal/', test_modal, name='test_modal'),
    path('admin/inbox/', admin_inbox, name='admin_inbox'),
    path('admin/message/<int:msg_id>/', admin_message_detail, name='admin_message_detail'),
]
