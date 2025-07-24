from django.urls import path
from . import views

app_name = 'labtest'

urlpatterns = [
    path('analysis/', views.lab_analysis_form, name='lab_analysis_form'),
    path('report/<int:record_id>/', views.print_lab_report, name='print_lab_report'),
    path('patient/<int:patient_id>/lab-records/', views.patient_lab_records, name='patient_lab_records'),
    path('all-records/', views.all_lab_records, name='all_lab_records'),
    path('edit/<int:record_id>/', views.edit_lab_record, name='edit_lab_record'),
    path('delete/<int:record_id>/', views.delete_lab_record, name='delete_lab_record'),
] 