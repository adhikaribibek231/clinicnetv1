from django.urls import path
from . import views

app_name = 'clinic'

urlpatterns = [
    path('', views.Home, name='home'),
    path('dashboard/', views.Index, name='dashboard'),  # Admin dashboard
    path('admin_login/', views.Login, name='login'),
    path('logout/', views.Logout_admin, name='logout'),
    path('about/', views.About, name='about'),
    path('contact/', views.Contact, name='contact'),
    path('admin_inbox/', views.admin_inbox, name='admin_inbox'),
    path('admin_message_detail/<int:msg_id>/', views.admin_message_detail, name='admin_message_detail'),
    
    # Doctor Management URLs
    path('view_doctor/', views.View_Doctor, name='view_doctor'),
    path('add_doctor/', views.Add_Doctor, name='add_doctor'),
    path('delete_doctor/<int:pid>/', views.Delete_Doctor, name='delete_doctor'),
    path('edit_doctor/<int:doctor_id>/', views.Edit_Doctor, name='edit_doctor'),
    
    # Patient Management URLs
    path('view_patient/', views.View_Patient, name='view_patient'),
    path('add_patient/', views.Add_Patient, name='add_patient'),
    path('delete_patient/<int:pid>/', views.Delete_Patient, name='delete_patient'),
    path('edit_patient/<int:patient_id>/', views.Edit_Patient, name='edit_patient'),
    path('view_patient_detail/<int:patient_id>/', views.view_patient_detail, name='view_patient_detail'),
    
    # Appointment Management URLs
    path('view_appointment/', views.View_Appointment, name='view_appointment'),
    path('add_appointment/', views.Add_Appointment, name='add_appointment'),
    path('confirm_admin_appointment/', views.confirm_admin_appointment, name='confirm_admin_appointment'),
    path('delete_appointment/<int:aid>/', views.Delete_Appointment, name='delete_appointment'),
    path('edit_appointment/<int:appointment_id>/', views.Edit_Appointment, name='edit_appointment'),
    
    # Public appointment booking URLs
    path('book/', views.BookAppointment, name='book_appointment_public'),
    path('api/doctors/', views.get_available_doctors, name='get_available_doctors'),
    path('api/dates/', views.get_available_dates, name='get_available_dates'),
    path('api/times/', views.get_available_times, name='get_available_times'),
    path('api/confirm/', views.confirm_appointment, name='confirm_appointment'),
    path('confirmation/<str:token>/', views.appointment_confirmation, name='appointment_confirmation'),
    path('download/<str:token>/', views.download_token, name='download_token'),
    
    # Schedule Management URLs
    path('view_schedules/', views.View_Schedules, name='view_schedules'),
    path('doctor_schedules_overview/', views.doctor_schedules_overview, name='doctor_schedules_overview'),
    path('doctor_schedule_calendar/<int:doctor_id>/', views.doctor_schedule_calendar, name='doctor_schedule_calendar'),
    path('update_doctor_availability/<int:doctor_id>/', views.Update_Doctor_Availability, name='update_doctor_availability'),
    
    # Schedule AJAX URLs
    path('doctor_schedule_calendar/<int:doctor_id>/add_schedule/', views.add_schedule_ajax, name='add_schedule_ajax'),
    path('doctor_schedule_calendar/<int:doctor_id>/update_schedule/<int:schedule_id>/', views.update_schedule_ajax, name='update_schedule_ajax'),
    path('doctor_schedule_calendar/<int:doctor_id>/delete_schedule/<int:schedule_id>/', views.delete_schedule_ajax, name='delete_schedule_ajax'),
    path('doctor_schedule_calendar/<int:doctor_id>/get_schedule_details/<int:schedule_id>/', views.get_schedule_details_ajax, name='get_schedule_details_ajax'),
    
    # Recurring Schedule Management URLs
    path('recurring-schedules/', views.recurring_schedules_overview, name='recurring_schedules_overview'),
    path('recurring-schedules/edit/<int:schedule_id>/', views.edit_recurring_schedule, name='edit_recurring_schedule'),
    path('recurring-schedules/delete/<int:schedule_id>/', views.delete_recurring_schedule, name='delete_recurring_schedule'),
    path('recurring-schedules/<int:doctor_id>/generate-monthly/', views.generate_monthly_schedules_ajax, name='generate_monthly_schedules_ajax'),
    
    # Emergency Services URLs
    path('emergency-services/', views.emergency_services_overview, name='emergency_services_overview'),
    path('emergency-services/register/', views.emergency_patient_registration, name='emergency_patient_registration'),
    path('emergency-services/<int:emergency_id>/', views.emergency_patient_detail, name='emergency_patient_detail'),
    path('emergency-services/list/', views.emergency_patient_list, name='emergency_patient_list'),
    
    # Service Management URLs
    path('manage_services/', views.Manage_Services, name='manage_services'),
    
    # Test URL
    path('test_modal/', views.test_modal, name='test_modal'),
]
