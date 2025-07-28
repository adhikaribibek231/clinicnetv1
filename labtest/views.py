from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from clinic.models import Patient
from .models import LabTestRecord, LabTestResult
import json
import os
from django.conf import settings
from datetime import date

# Helper to load reference values
REFERENCE_FILE = os.path.join(settings.BASE_DIR, 'lab-reference-values.json')
def load_reference_values():
    with open(REFERENCE_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

# Lab analysis form: select patient, select tests, enter values
def lab_analysis_form(request):
    reference_data = load_reference_values()
    patients = Patient.objects.all()
    if request.method == 'POST':
        patient_id = request.POST.get('patient')
        selected_tests = request.POST.getlist('selected_tests')
        test_values = {k: v for k, v in request.POST.items() if k.startswith('test_')}
        notes = request.POST.get('notes', '')
        patient = get_object_or_404(Patient, id=patient_id)
        record = LabTestRecord.objects.create(patient=patient, date=date.today(), notes=notes)
        for test in selected_tests:
            value = test_values.get(f'test_{test}', '')
            # Find unit/reference from reference_data if available
            unit, reference = '', ''
            for section in reference_data.values():
                if isinstance(section, list):
                    for t in section:
                        if t.get('test') == test or t.get('serotype') == test:
                            unit = t.get('unit', '')
                            reference = t.get('reference', '')
                elif isinstance(section, dict):
                    for sublist in section.values():
                        for t in sublist:
                            if t.get('test') == test:
                                unit = t.get('unit', '')
                                reference = t.get('reference', '')
            LabTestResult.objects.create(record=record, test_name=test, value=value, unit=unit, reference=reference)
        # Handle urine/stool/other tests (no reference)
        for extra in ['Urine', 'Stool', 'Other']:
            if f'extra_{extra.lower()}' in request.POST:
                value = request.POST.get(f'extra_{extra.lower()}')
                LabTestResult.objects.create(record=record, test_name=extra, value=value)
        return redirect('labtest:print_lab_report', record_id=record.id)
    return render(request, 'labtest/lab_analysis_form.html', {'reference_data': reference_data, 'patients': patients})

# Print lab report (A4 layout)
def print_lab_report(request, record_id):
    record = get_object_or_404(LabTestRecord, id=record_id)
    results = {r.test_name: r for r in record.results.all()}
    # Only include tests that have results for this record
    ticked_tests = []
    for r in record.results.all():
        ticked_tests.append({
            'name': r.test_name,
            'unit': r.unit,
            'reference': r.reference,
        })
    return render(request, 'labtest/print_lab_report.html', {
        'record': record,
        'results': results,
        'all_tests': ticked_tests,
    })

def patient_lab_records(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    records = patient.lab_records.all()
    return render(request, 'labtest/patient_lab_records.html', {'patient': patient, 'records': records})

def all_lab_records(request):
    records = LabTestRecord.objects.select_related('patient').all()
    return render(request, 'labtest/all_lab_records.html', {'records': records})

def edit_lab_record(request, record_id):
    record = get_object_or_404(LabTestRecord, id=record_id)
    reference_data = load_reference_values()
    if request.method == 'POST':
        notes = request.POST.get('notes', '')
        record.notes = notes
        record.save()
        for result in record.results.all():
            value = request.POST.get(f'test_{result.test_name}', '')
            if value:
                result.value = value
                result.save()
        return redirect('labtest:print_lab_report', record_id=record.id)
    return render(request, 'labtest/edit_lab_record.html', {'record': record, 'reference_data': reference_data})

def delete_lab_record(request, record_id):
    record = get_object_or_404(LabTestRecord, id=record_id)
    patient_id = record.patient.id
    if request.method == 'POST':
        record.delete()
        return redirect('labtest:patient_lab_records', patient_id=patient_id)
    return render(request, 'labtest/confirm_delete_lab_record.html', {'record': record})

def lab_reports_list(request):
    from django.db.models import Q
    query = request.GET.get('q', '')
    # Get patients who have at least one lab record
    patients = Patient.objects.filter(lab_records__isnull=False).distinct()
    if query:
        patients = patients.filter(Q(name__icontains=query) | Q(mobile__icontains=query) | Q(email__icontains=query))
    patients = patients.order_by('name')
    return render(request, 'labtest/lab_reports_list.html', {'patients': patients, 'query': query})

__all__ = [
    'lab_analysis_form',
    'print_lab_report',
    'patient_lab_records',
    'all_lab_records',
    'edit_lab_record',
    'delete_lab_record',
]
