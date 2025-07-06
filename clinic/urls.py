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
    path('delete_doctor/<int:pid>/', Delete_Doctor, name='delete_doctor'),
    path('delete_patient/<int:pid>/', Delete_Patient, name='delete_patient'),

    path('view_patient/', View_Patient, name='view_patient'),
    path('add_patient/', Add_Patient, name='add_patient'),

    path('view_appointment/', View_Appointment, name='view_appointment'),
    path('add_appointment/', Add_Appointment, name='add_appointment'),
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
]
