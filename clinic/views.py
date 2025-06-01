from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import *
from django.contrib.auth import authenticate, logout, login
# Create your views here.
def About(request):
    return render(request, 'about.html')
def Contact(request):
    return render(request, 'contact.html')
# def Service(request):
#     return render(request, 'service.html')
def Index(request):
    if not request.user.is_staff:
        return redirect('login')
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
    if not request.user.is_staff:
        return redirect('login')
    logout(request)
    return redirect('login')


def View_Doctor(request):
    if not request.user.is_staff:
        return redirect('login')
    doctors = Doctor.objects.all()
    context = {'doctors': doctors}
    return render(request, 'view_doctor.html', context)

def View_Patient(request):
    if not request.user.is_staff:
        return redirect('login')
    patients = Patient.objects.all()
    context = {
        'patients': patients
    }
    return render(request, 'view_patient.html', context)

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

def Delete_Doctor(request,pid):
    if not request.user.is_staff:
        return redirect('login')
    doctor = Doctor.objects.get(id=pid)
    doctor.delete()
    return redirect('view_doctor')

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

def Delete_Patient(request,pid):
    if not request.user.is_staff:
        return redirect('login')
    patient = Patient.objects.get(id=pid)
    patient.delete()
    return redirect('view_patient')

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


def View_Appointment(request):
    appointments = Appointment.objects.select_related('doctor', 'patient').all()
    return render(request, 'view_appointment.html', {'appointments': appointments})

def Delete_Appointment(request, aid):
    if not request.user.is_staff:
        return redirect('login')
    appointment = Appointment.objects.get(id=aid)
    appointment.delete()
    return redirect('view_appointment')

