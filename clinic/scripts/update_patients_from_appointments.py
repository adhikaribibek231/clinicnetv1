from clinic.models import PublicAppointment, Patient

count = 0
for appt in PublicAppointment.objects.filter(status='completed'):
    patient = Patient.objects.filter(
        name=appt.patient_name.strip(),
        age=appt.patient_age,
        gender=appt.patient_gender,
        mobile=appt.patient_mobile.strip()
    ).first()
    if not patient:
        Patient.objects.create(
            name=appt.patient_name.strip(),
            age=appt.patient_age,
            gender=appt.patient_gender,
            mobile=appt.patient_mobile.strip(),
            address=appt.patient_address,
            email='',
            blood_group='',
            emergency_contact=appt.emergency_contact or '',
            medical_history=''
        )
        count += 1
print(f'Added {count} new patients from completed appointments.') 