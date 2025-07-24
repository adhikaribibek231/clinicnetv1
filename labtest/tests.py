from django.test import TestCase
from clinic.models import Patient
from .models import LabTestRecord, LabTestResult

# Create your tests here.

class LabTestRecordTest(TestCase):
    def test_create_lab_record(self):
        patient = Patient.objects.create(name='Test', gender='Male', mobile='123', age=30, address='Test')
        record = LabTestRecord.objects.create(patient=patient, notes='Sample note')
        LabTestResult.objects.create(record=record, test_name='Hemoglobin', value='15', unit='g/dl', reference='13.5-18')
        self.assertEqual(record.results.count(), 1)
        self.assertEqual(record.notes, 'Sample note')
