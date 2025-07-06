from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import *
from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.decorators import login_required
# Create your views here.
def About(request):
    return render(request, 'about.html')
def Contact(request):
    return render(request, 'contact.html')
# def Service(request):
#     return render(request, 'service.html')
@login_required
def Index(request):
    doctors = Doctor.objects.all()
    patients = Patient.objects.all()
    appointments = Appointment.objects.all()
    d = doctors.count()
    p = patients.count()
    a = appointments.count()
    return render(request, 'index.html', {'d': d, 'p': p, 'a': a})

def Login(request):
    error = ""
    if request.method == 'POST':
        u = request.POST['uname']
        p = request.POST['pwd']
        user = authenticate(username=u, password=p)
        if user is not None:
            if user.is_staff:
                login(request, user)
                error = "no"
            else:
                error = "yes"
        else:
            error = "yes"
    d = {'error': error}
    return render(request, 'login.html', d)


def Logout_admin(request):
    logout(request)
    return redirect('unified_login')


@login_required
def View_Doctor(request):
    doctors = Doctor.objects.all()
    context = {'doctors': doctors}
    return render(request, 'view_doctor.html', context)

@login_required
def View_Patient(request):
    patients = Patient.objects.all()
    context = {
        'patients': patients
    }
    return render(request, 'view_patient.html', context)

@login_required
def Add_Doctor(request):
    error = ""
    if request.method == 'POST':
        name = request.POST.get('name')
        mobile = request.POST.get('mobile')
        special = request.POST.get('special')

        try:
            Doctor.objects.create(name=name, mobile=mobile, special=special)
            error = "no"
        except:
            error = "yes"

        if error == "no":
            return redirect('view_doctor') 

    return render(request, 'add_doctor.html', {'error': error})

@login_required
def Delete_Doctor(request,pid):
    doctor = Doctor.objects.get(id=pid)
    doctor.delete()
    return redirect('view_doctor')

@login_required
def Add_Patient(request):
    error = ""
    if request.method == 'POST':
        name = request.POST.get('name')
        gender = request.POST.get('gender')
        mobile = request.POST.get('mobile')
        age = request.POST.get('age')
        address = request.POST.get('address')

        try:
            Patient.objects.create(name=name, gender=gender, mobile=mobile, age=age, address=address)
            error = "no"
        except:
            error = "yes"

        if error == "no":
            return redirect('view_patient')

    return render(request, 'add_patient.html', {'error': error})

@login_required
def Delete_Patient(request,pid):
    patient = Patient.objects.get(id=pid)
    patient.delete()
    return redirect('view_patient')

@login_required
def Add_Appointment(request):
    error = ""
    if request.method == 'POST':
        doctor_id = request.POST.get('doctor')
        patient_id = request.POST.get('patient')
        date1 = request.POST.get('date1')
        time1 = request.POST.get('time1')

        try:
            doctor = Doctor.objects.get(id=doctor_id)
            patient = Patient.objects.get(id=patient_id)
            Appointment.objects.create(doctor=doctor, patient=patient, date1=date1, time1=time1)
            error = "no"
            return redirect('view_appointment')
        except:
            error = "yes"

    context = {
        'doctors': Doctor.objects.all(),
        'patients': Patient.objects.all(),
        'error': error
    }
    return render(request, 'add_appointment.html', context)


@login_required
def View_Appointment(request):
    appointments = Appointment.objects.select_related('doctor', 'patient').all()
    return render(request, 'view_appointment.html', {'appointments': appointments})

@login_required
def Delete_Appointment(request, aid):
    appointment = Appointment.objects.get(id=aid)
    appointment.delete()
    return redirect('view_appointment')

