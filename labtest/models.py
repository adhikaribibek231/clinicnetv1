from django.db import models
from clinic.models import Patient

# Create your models here.

class LabTestRecord(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='lab_records')
    date = models.DateField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    # Optionally, add who entered the record, notes, etc.
    def __str__(self):
        return f"{self.patient.name} - {self.date}"
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('labtest:print_lab_report', args=[str(self.id)])
    class Meta:
        ordering = ['-date']
        verbose_name = 'Lab Test Record'
        verbose_name_plural = 'Lab Test Records'

class LabTestResult(models.Model):
    record = models.ForeignKey(LabTestRecord, on_delete=models.CASCADE, related_name='results')
    test_name = models.CharField(max_length=100)
    value = models.CharField(max_length=100, blank=True)
    unit = models.CharField(max_length=50, blank=True)
    reference = models.CharField(max_length=100, blank=True)
    # For tests like Widal, you can use value for titre, and test_name for serotype
    def __str__(self):
        return f"{self.test_name}: {self.value} {self.unit} ({self.reference})"
    class Meta:
        verbose_name = 'Lab Test Result'
        verbose_name_plural = 'Lab Test Results'

# For urine, stool, and other tests that may not have reference values, just use test_name/value/unit as needed.
