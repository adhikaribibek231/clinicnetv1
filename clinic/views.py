from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import *
from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta, date
import json
from PIL import Image, ImageDraw, ImageFont
import io
import base64
# Create your views here.

def Home(request):
    """Public home page accessible without login"""
    return render(request, 'home.html')

def About_Public(request):
    """Public about page accessible without login"""
    return render(request, 'about_public.html')

def Contact_Public(request):
    """Public contact page accessible without login"""
    return render(request, 'contact_public.html')

def BookAppointment(request):
    """Public appointment booking page"""
    services = Service.objects.all()
    doctors = Doctor.objects.all()
    
    context = {
        'services': services,
        'doctors': doctors,
    }
    return render(request, 'book_appointment.html', context)

def get_available_doctors(request):
    """AJAX endpoint to get available doctors for a service"""
    service_id = request.GET.get('service_id')
    if service_id:
        # Get doctors who can provide this service
        schedules = DoctorSchedule.objects.filter(service_id=service_id, is_available=True)
        doctors = Doctor.objects.filter(id__in=schedules.values_list('doctor', flat=True)).distinct()
        doctor_list = [{'id': doctor.id, 'name': doctor.name, 'special': doctor.special} for doctor in doctors]
        return JsonResponse({'doctors': doctor_list})
    return JsonResponse({'doctors': []})

def get_available_dates(request):
    """AJAX endpoint to get available dates for a doctor and service"""
    doctor_id = request.GET.get('doctor_id')
    service_id = request.GET.get('service_id')
    
    if doctor_id and service_id:
        # Get dates in the next 30 days
        today = date.today()
        end_date = today + timedelta(days=30)
        
        schedules = DoctorSchedule.objects.filter(
            doctor_id=doctor_id,
            service_id=service_id,
            date__gte=today,
            date__lte=end_date,
            is_available=True
        ).values_list('date', flat=True).distinct()
        
        # Filter out dates where all slots are booked
        available_dates = []
        for schedule_date in schedules:
            day_schedules = DoctorSchedule.objects.filter(
                doctor_id=doctor_id,
                service_id=service_id,
                date=schedule_date,
                is_available=True
            )
            
            # Check if any slots are available for this date
            has_available_slots = False
            for schedule in day_schedules:
                if schedule.get_available_slots():
                    has_available_slots = True
                    break
            
            if has_available_slots:
                available_dates.append(schedule_date.strftime('%Y-%m-%d'))
        
        return JsonResponse({'dates': available_dates})
    return JsonResponse({'dates': []})

def get_available_times(request):
    """AJAX endpoint to get available time slots for a specific date"""
    doctor_id = request.GET.get('doctor_id')
    service_id = request.GET.get('service_id')
    selected_date = request.GET.get('date')
    
    if doctor_id and service_id and selected_date:
        try:
            date_obj = datetime.strptime(selected_date, '%Y-%m-%d').date()
            schedules = DoctorSchedule.objects.filter(
                doctor_id=doctor_id,
                service_id=service_id,
                date=date_obj,
                is_available=True
            )
            
            all_slots = []
            for schedule in schedules:
                slots = schedule.get_available_slots()
                all_slots.extend([slot.strftime('%H:%M') for slot in slots])
            
            return JsonResponse({'times': all_slots})
        except ValueError:
            return JsonResponse({'times': []})
    return JsonResponse({'times': []})

def confirm_appointment(request):
    """Handle appointment confirmation and create the appointment"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Create the appointment
            appointment = PublicAppointment.objects.create(
                patient_name=data['patient_name'],
                patient_age=data['patient_age'],
                patient_gender=data['patient_gender'],
                patient_mobile=data['patient_mobile'],
                patient_address=data['patient_address'],
                emergency_contact=data.get('emergency_contact', ''),
                doctor_id=data['doctor_id'],
                service_id=data['service_id'],
                date=data['date'],
                time=data['time']
            )
            
            return JsonResponse({
                'success': True,
                'token': appointment.token,
                'appointment_id': appointment.id
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def appointment_confirmation(request, token):
    """Show appointment confirmation with token"""
    try:
        appointment = PublicAppointment.objects.get(token=token)
        context = {
            'appointment': appointment
        }
        return render(request, 'appointment_confirmation.html', context)
    except PublicAppointment.DoesNotExist:
        return render(request, 'appointment_not_found.html')

def download_token(request, token):
    """Generate and download appointment token as JPEG"""
    try:
        appointment = PublicAppointment.objects.get(token=token)
        
        # Create image
        img = Image.new('RGB', (800, 600), color='white')
        draw = ImageDraw.Draw(img)
        
        # Try to use a default font, fallback to basic if not available
        try:
            font_large = ImageFont.truetype("arial.ttf", 24)
            font_medium = ImageFont.truetype("arial.ttf", 18)
            font_small = ImageFont.truetype("arial.ttf", 14)
        except:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Draw content
        y_position = 50
        
        # Header
        draw.text((400, y_position), "CLINICNET APPOINTMENT TOKEN", fill='black', anchor='mm', font=font_large)
        y_position += 60
        
        # Token
        draw.text((400, y_position), f"TOKEN: {appointment.token}", fill='blue', anchor='mm', font=font_large)
        y_position += 80
        
        # Patient details
        draw.text((50, y_position), "PATIENT DETAILS:", fill='black', font=font_medium)
        y_position += 30
        draw.text((50, y_position), f"Name: {appointment.patient_name}", fill='black', font=font_small)
        y_position += 25
        draw.text((50, y_position), f"Age: {appointment.patient_age} | Gender: {appointment.patient_gender}", fill='black', font=font_small)
        y_position += 25
        draw.text((50, y_position), f"Mobile: {appointment.patient_mobile}", fill='black', font=font_small)
        y_position += 25
        draw.text((50, y_position), f"Address: {appointment.patient_address}", fill='black', font=font_small)
        y_position += 40
        
        # Appointment details
        draw.text((50, y_position), "APPOINTMENT DETAILS:", fill='black', font=font_medium)
        y_position += 30
        draw.text((50, y_position), f"Doctor: Dr. {appointment.doctor.name} ({appointment.doctor.special})", fill='black', font=font_small)
        y_position += 25
        draw.text((50, y_position), f"Service: {appointment.service.name}", fill='black', font=font_small)
        y_position += 25
        draw.text((50, y_position), f"Date: {appointment.date.strftime('%B %d, %Y')}", fill='black', font=font_small)
        y_position += 25
        draw.text((50, y_position), f"Time: {appointment.time.strftime('%I:%M %p')}", fill='black', font=font_small)
        y_position += 40
        
        # Instructions
        draw.text((50, y_position), "IMPORTANT INSTRUCTIONS:", fill='red', font=font_medium)
        y_position += 30
        draw.text((50, y_position), "• Please arrive 15 minutes before your appointment time", fill='black', font=font_small)
        y_position += 25
        draw.text((50, y_position), "• Bring this token with you", fill='black', font=font_small)
        y_position += 25
        draw.text((50, y_position), "• Payment will be collected at the clinic", fill='black', font=font_small)
        y_position += 25
        draw.text((50, y_position), "• Status: Pending (will be confirmed upon arrival)", fill='black', font=font_small)
        
        # Save to bytes
        img_io = io.BytesIO()
        img.save(img_io, 'JPEG', quality=95)
        img_io.seek(0)
        
        # Create response
        response = HttpResponse(img_io.getvalue(), content_type='image/jpeg')
        response['Content-Disposition'] = f'attachment; filename="appointment_token_{appointment.token}.jpg"'
        return response
        
    except PublicAppointment.DoesNotExist:
        return HttpResponse("Appointment not found", status=404)

@login_required
def About(request):
    return render(request, 'about.html')
@login_required
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
            return redirect('clinic:view_doctor') 

    return render(request, 'add_doctor.html', {'error': error})

@login_required
def Delete_Doctor(request,pid):
    doctor = Doctor.objects.get(id=pid)
    doctor.delete()
    return redirect('clinic:view_doctor')

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
            return redirect('clinic:view_patient')

    return render(request, 'add_patient.html', {'error': error})

@login_required
def Delete_Patient(request,pid):
    patient = Patient.objects.get(id=pid)
    patient.delete()
    return redirect('clinic:view_patient')

@login_required
def Add_Appointment(request):
    """Admin appointment booking with new unified system"""
    services = Service.objects.all()
    doctors = Doctor.objects.all()
    patients = Patient.objects.all()
    
    context = {
        'services': services,
        'doctors': doctors,
        'patients': patients,
    }
    return render(request, 'add_appointment.html', context)

@login_required
def confirm_admin_appointment(request):
    """Handle admin appointment confirmation and create the appointment"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Check if patient exists, if not create one
            patient_name = data.get('patient_name', '')
            patient_id = data.get('patient_id', '')
            
            if patient_id:
                # Use existing patient
                patient = Patient.objects.get(id=patient_id)
                patient_name = patient.name
                patient_age = patient.age
                patient_gender = patient.gender
                patient_mobile = patient.mobile
                patient_address = patient.address
            else:
                # Use provided patient details
                patient_name = data['patient_name']
                patient_age = data['patient_age']
                patient_gender = data['patient_gender']
                patient_mobile = data['patient_mobile']
                patient_address = data['patient_address']
            
            # Create the appointment
            appointment = PublicAppointment.objects.create(
                patient_name=patient_name,
                patient_age=patient_age,
                patient_gender=patient_gender,
                patient_mobile=patient_mobile,
                patient_address=patient_address,
                emergency_contact=data.get('emergency_contact', ''),
                doctor_id=data['doctor_id'],
                service_id=data['service_id'],
                date=data['date'],
                time=data['time'],
                status='confirmed',  # Admin bookings are confirmed by default
                payment_status='paid'  # Admin bookings are paid by default
            )
            
            return JsonResponse({
                'success': True,
                'token': appointment.token,
                'appointment_id': appointment.id
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def View_Appointment(request):
    # Get both old and new appointments
    old_appointments = Appointment.objects.select_related('doctor', 'patient').all()
    new_appointments = PublicAppointment.objects.select_related('doctor', 'service').all()
    
    context = {
        'old_appointments': old_appointments,
        'new_appointments': new_appointments,
        'appointments': new_appointments  # For backward compatibility
    }
    return render(request, 'view_appointment.html', context)

@login_required
def Delete_Appointment(request, aid):
    appointment = Appointment.objects.get(id=aid)
    appointment.delete()
    return redirect('clinic:view_appointment')

