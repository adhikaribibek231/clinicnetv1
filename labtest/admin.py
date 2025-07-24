from django.contrib import admin
from .models import LabTestRecord, LabTestResult

admin.site.register(LabTestRecord)
admin.site.register(LabTestResult)
