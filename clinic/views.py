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
    return render(request, 'index.html')
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
            return redirect('view_doctor')  # Redirect after successful save

    return render(request, 'add_doctor.html', {'error': error})