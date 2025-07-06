from django.contrib import admin
from django.urls import path, include
from clinic.views import *

app_name = 'clinic'

urlpatterns = [
    path('',Index, name='home'),
    path('admin_login/', Login, name='login'),
    path('logout/', Logout_admin, name='logout'),
    path('view_doctor/', View_Doctor, name='view_doctor'),
    path('add_doctor/', Add_Doctor, name='add_doctor'),
    path('delete_doctor/<int:pid>/', Delete_Doctor, name='delete_doctor'),
    path('delete_patient/<int:pid>/', Delete_Patient, name='delete_patient'),

    path('view_patient/', View_Patient, name='view_patient'),
    path('add_patient/', Add_Patient, name='add_patient'),

    path('view_appointment/', View_Appointment, name='view_appointment'),
    path('add_appointment/', Add_Appointment, name='add_appointment'),
    path('delete-appointment/<int:aid>/', Delete_Appointment, name='delete_appointment'),

]
