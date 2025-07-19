from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from .models import *
from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta, date
import json
import io
import base64
from django.contrib import messages
import time
import sqlite3
from django.db import connection
from PIL import Image, ImageDraw, ImageFont  # type: ignore
from django.db.models import Count, Q
from django.db.models import Q, Exists, OuterRef
from .models import ContactMessage
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.admin.views.decorators import staff_member_required
from ClinicNet0.models import UserProfile
from functools import wraps
from django.http import HttpResponseForbidden

# Database performance monitoring
def get_db_stats():
    """Get SQLite database statistics for monitoring"""
    try:
        with sqlite3.connect('db.sqlite3') as conn:
            cursor = conn.cursor()
            
            # Get database size
            cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size();")
            db_size = cursor.fetchone()[0]
            
            # Get table sizes
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            table_stats = {}
            for table in tables:
                table_name = table[0]
                cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                count = cursor.fetchone()[0]
                table_stats[table_name] = count
            
            return {
                'database_size_mb': round(db_size / (1024 * 1024), 2),
                'table_counts': table_stats,
                'total_tables': len(tables)
            }
    except Exception as e:
        return {'error': str(e)}

# Create your views here.

def Home(request):
    """Public home page accessible without login"""
    return render(request, 'home.html')

def About_Public(request):
    """Public about page accessible without login"""
    return render(request, 'about_public.html')

def Contact_Public(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        message = request.POST.get('message', '').strip()
        errors = []
        # Validate all fields
        if not name or not email or not phone or not message:
            errors.append('All fields are required.')
        # Validate phone: only digits allowed
        if not phone.isdigit():
            errors.append('Phone number must contain only numbers.')
        # Validate email
        try:
            validate_email(email)
        except ValidationError:
            errors.append('Invalid email address.')
        if errors or 'verify' not in request.POST:
            # Show verification page if no errors and not yet verified
            if not errors and 'verify' not in request.POST:
                return render(request, 'verify_contact_message.html', {
                    'name': name, 'email': email, 'phone': phone, 'message': message
                })
            return render(request, 'contact.html', {'errors': errors, 'name': name, 'email': email, 'phone': phone, 'message': message})
        # Save message
        ContactMessage.objects.create(name=name, email=email, phone=phone, message=message)
        return render(request, 'contact.html', {'success': True})
    return render(request, 'contact.html')

def BookAppointment(request):
    """Public appointment booking page"""
    services = Service.objects.all()  # type: ignore
    doctors = Doctor.objects.all()  # type: ignore
    
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
        schedules = DoctorSchedule.objects.filter(service_id=service_id, is_available=True)  # type: ignore
        doctors = Doctor.objects.filter(id__in=schedules.values_list('doctor', flat=True)).distinct()  # type: ignore
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
        
        schedules = DoctorSchedule.objects.filter( # type: ignore
            doctor_id=doctor_id,
            service_id=service_id,
            date__gte=today,
            date__lte=end_date,
            is_available=True
        ).values_list('date', flat=True).distinct()  # type: ignore
        
        # Filter out dates where all slots are booked
        available_dates = []
        for schedule_date in schedules:
            day_schedules = DoctorSchedule.objects.filter( # type: ignore
                doctor_id=doctor_id,
                service_id=service_id,
                date=schedule_date,
                is_available=True
            )  # type: ignore
            
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
            schedules = DoctorSchedule.objects.filter( # type: ignore
                doctor_id=doctor_id,
                service_id=service_id,
                date=date_obj,
                is_available=True
            )  # type: ignore
            
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
            # Find or create patient
            patient = Patient.objects.filter(mobile=data['patient_mobile'].strip()).first()
            if not patient:
                patient = Patient.objects.create(
                    name=data['patient_name'].strip(),
                    age=data['patient_age'],
                    gender=data['patient_gender'],
                    mobile=data['patient_mobile'].strip(),
                    address=data['patient_address'],
                    emergency_contact=data.get('emergency_contact', ''),
                    email=data['patient_email'],
                    blood_group='',
                    medical_history=''
                )
            # Create the appointment and link patient
            appointment = PublicAppointment.objects.create( # type: ignore
                patient=patient,
                patient_name=data['patient_name'],
                patient_age=data['patient_age'],
                patient_gender=data['patient_gender'],
                patient_mobile=data['patient_mobile'],
                patient_email=data['patient_email'],
                patient_address=data['patient_address'],
                emergency_contact=data.get('emergency_contact', ''),
                doctor_id=data['doctor_id'],
                service_id=data['service_id'],
                date=data['date'],
                time=data['time']
            )  # type: ignore
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
        appointment = PublicAppointment.objects.get(token=token)  # type: ignore
        context = {
            'appointment': appointment
        }
        return render(request, 'appointment_confirmation.html', context)
    except PublicAppointment.DoesNotExist:  # type: ignore
        return render(request, 'appointment_not_found.html')

def download_token(request, token):
    """Generate and download appointment token as JPEG"""
    try:
        appointment = PublicAppointment.objects.get(token=token)  # type: ignore
        
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
        # Doctor details
        doctor_name = appointment.doctor.name
        if not doctor_name.lower().startswith('dr.'):
            doctor_name = f"Dr. {doctor_name}"
        draw.text((50, y_position), f"Doctor: {doctor_name} ({appointment.doctor.special})", fill='black', font=font_small)
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
        
    except PublicAppointment.DoesNotExist:  # type: ignore
        return HttpResponse("Appointment not found", status=404)  # type: ignore

@login_required
def About(request):
    return render(request, 'about.html')
@login_required
def Contact(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        message = request.POST.get('message', '').strip()
        errors = []
        # Validate all fields
        if not name or not email or not phone or not message:
            errors.append('All fields are required.')
        # Validate phone: must start with 9, 10 digits, all numeric
        if not (phone.isdigit() and len(phone) == 10 and phone.startswith('9')):
            errors.append('Phone number must start with 9 and be exactly 10 digits.')
        # Validate email
        try:
            validate_email(email)
        except ValidationError:
            errors.append('Invalid email address.')
        if errors or 'verify' not in request.POST:
            # Show verification page if no errors and not yet verified
            if not errors and 'verify' not in request.POST:
                return render(request, 'verify_contact_message.html', {
                    'name': name, 'email': email, 'phone': phone, 'message': message
                })
            return render(request, 'contact.html', {'errors': errors, 'name': name, 'email': email, 'phone': phone, 'message': message})
        # Save message
        ContactMessage.objects.create(name=name, email=email, phone=phone, message=message)
        return render(request, 'contact.html', {'success': True})
    return render(request, 'contact.html')

from django.contrib.admin.views.decorators import staff_member_required

def clinic_user_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden('You must be logged in.')
        if not hasattr(request.user, 'userprofile') or request.user.userprofile.user_type != 'clinic':
            return HttpResponseForbidden('You do not have permission to view this page.')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

@clinic_user_required
def admin_inbox(request):
    messages = ContactMessage.objects.order_by('is_read', '-created_at')
    unread_count = ContactMessage.objects.filter(is_read=False).count()
    return render(request, 'admin_inbox.html', {'messages': messages, 'unread_count': unread_count})

@clinic_user_required
def admin_message_detail(request, msg_id):
    msg = ContactMessage.objects.get(id=msg_id)
    if not msg.is_read:
        msg.is_read = True
        msg.save()
    return render(request, 'admin_message_detail.html', {'msg': msg})

# def Service(request):
#     return render(request, 'service.html')
@login_required
def Index(request):
    doctors = Doctor.objects.all()  # type: ignore
    patients = Patient.objects.all()  # type: ignore
    appointments = PublicAppointment.objects.all()  # type: ignore
    services = Service.objects.all()  # type: ignore
    
    # Get recent appointments (last 10)
    recent_appointments = PublicAppointment.objects.select_related('doctor', 'service').order_by('-created_at')[:10]  # type: ignore
    
    d = doctors.count()
    p = patients.count()
    a = appointments.count()
    services_count = services.count()
    
    # Get database statistics
    db_stats = get_db_stats()
    
    unread_count = ContactMessage.objects.filter(is_read=False).count()
    context = {
        'd': d, 
        'p': p, 
        'a': a,
        'services_count': services_count,
        'recent_appointments': recent_appointments,
        'db_stats': db_stats,
        'unread_count': unread_count,
    }
    return render(request, 'index.html', context)

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
    doctors = Doctor.objects.all()  # type: ignore
    total_doctors = doctors.count()
    # Active = doctors with at least one appointment in last 30 days
    last_30_days = date.today() - timedelta(days=30)
    active_doctors = Doctor.objects.filter(
        publicappointment__date__gte=last_30_days
    ).distinct().count()
    # This month = doctors created this month
    this_month_doctors = doctors.filter(
        created_at__year=date.today().year,
        created_at__month=date.today().month
    ).count()
    context = {
        'doctors': doctors,
        'total_doctors': total_doctors,
        'active_doctors': active_doctors,
        'this_month_doctors': this_month_doctors,
    }
    return render(request, 'view_doctor.html', context)

@login_required
def View_Patient(request):
    patients = Patient.objects.all()  # type: ignore
    total_patients = patients.count()
    # Active = patients with at least one uncompleted Appointment or matching PublicAppointment
    # Uncompleted Appointments
    appt_qs = Patient.objects.filter(appointment__status__in=['pending', 'confirmed']).values_list('id', flat=True)
    # Uncompleted PublicAppointments (match by name+mobile)
    public_qs = Patient.objects.annotate(
        has_uncompleted_public=Exists(
            PublicAppointment.objects.filter(
                patient_name=OuterRef('name'),
                patient_mobile=OuterRef('mobile'),
                status__in=['pending', 'confirmed']
            )
        )
    ).filter(has_uncompleted_public=True).values_list('id', flat=True)
    active_patients = Patient.objects.filter(Q(id__in=appt_qs) | Q(id__in=public_qs)).distinct().count()
    # This month = patients created this month
    this_month_patients = patients.filter(
        created_at__year=date.today().year,
        created_at__month=date.today().month
    ).count()
    # List of active patients (for display)
    active_patients_list = Patient.objects.filter(Q(id__in=appt_qs) | Q(id__in=public_qs)).distinct()
    context = {
        'patients': patients,
        'total_patients': total_patients,
        'active_patients': active_patients,
        'active_patients_list': active_patients_list,
        'this_month_patients': this_month_patients,
    }
    return render(request, 'view_patient.html', context)

@login_required
def Add_Doctor(request):
    error = ""
    if request.method == 'POST':
        name = request.POST.get('name')
        mobile = request.POST.get('mobile')
        special = request.POST.get('special')
        email = request.POST.get('email', '')
        qualification = request.POST.get('qualification', '')
        experience = request.POST.get('experience', 0)
        consultation_fee = request.POST.get('consultation_fee', 0)

        try:
            Doctor.objects.create( # type: ignore
                name=name, 
                mobile=mobile, 
                special=special,
                email=email,
                qualification=qualification,
                experience=experience,
                consultation_fee=consultation_fee
            )  # type: ignore
            error = "no"
        except Exception as e:
            print(f"Error creating doctor: {e}")
            error = "yes"

        if error == "no":
            return redirect('clinic:view_doctor') 

    return render(request, 'add_doctor.html', {'error': error})

@login_required
def Delete_Doctor(request,pid):
    doctor = Doctor.objects.get(id=pid)  # type: ignore
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
        email = request.POST.get('email', '')
        blood_group = request.POST.get('blood_group', '')
        emergency_contact = request.POST.get('emergency_contact', '')
        medical_history = request.POST.get('medical_history', '')

        try:
            Patient.objects.create( # type: ignore 
                name=name, 
                gender=gender, 
                mobile=mobile, 
                age=age, 
                address=address,
                email=email,
                blood_group=blood_group,
                emergency_contact=emergency_contact,
                medical_history=medical_history
            )  # type: ignore
            error = "no"
        except Exception as e:
            print(f"Error creating patient: {e}")
            error = "yes"

        if error == "no":
            return redirect('clinic:view_patient')

    return render(request, 'add_patient.html', {'error': error})

@login_required
def Delete_Patient(request,pid):
    patient = Patient.objects.get(id=pid)  # type: ignore
    patient.delete()
    return redirect('clinic:view_patient')

@login_required
def Add_Appointment(request):
    """Admin appointment booking with new unified system"""
    services = Service.objects.all()  # type: ignore
    doctors = Doctor.objects.all()  # type: ignore
    patients = Patient.objects.all()  # type: ignore
    
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
            patient_id = data.get('patient_id', '')
            if patient_id:
                # Use existing patient
                patient = Patient.objects.get(id=patient_id)  # type: ignore
            else:
                # Try to find by mobile
                patient = Patient.objects.filter(mobile=data['patient_mobile'].strip()).first()
                if not patient:
                    patient = Patient.objects.create(
                        name=data['patient_name'].strip(),
                        age=data['patient_age'],
                        gender=data['patient_gender'],
                        mobile=data['patient_mobile'].strip(),
                        address=data['patient_address'],
                        emergency_contact=data.get('emergency_contact', ''),
                        email=data['patient_email'],
                        blood_group='',
                        medical_history=''
                    )
            # Create the appointment and link patient
            appointment = PublicAppointment.objects.create( # type: ignore
                patient=patient,
                patient_name=patient.name,
                patient_age=patient.age,
                patient_gender=patient.gender,
                patient_mobile=patient.mobile,
                patient_email=patient.email,
                patient_address=patient.address,
                emergency_contact=patient.emergency_contact or '',
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
    today = date.today()
    appointments = PublicAppointment.objects.select_related('doctor', 'service').all().order_by('-created_at')
    total_appointments = appointments.count()
    pending_appointments = appointments.filter(status='pending').count()
    confirmed_appointments = appointments.filter(status='confirmed').count()
    completed_appointments = appointments.filter(status='completed').count()
    cancelled_appointments = appointments.filter(status='cancelled').count()
    todays_appointments = appointments.filter(date=today).count()
    context = {
        'appointments': appointments,
        'total_appointments': total_appointments,
        'pending_appointments': pending_appointments,
        'confirmed_appointments': confirmed_appointments,
        'completed_appointments': completed_appointments,
        'cancelled_appointments': cancelled_appointments,
        'todays_appointments': todays_appointments,
    }
    return render(request, 'view_appointment.html', context)

@login_required
def Delete_Appointment(request, aid):
    try:
        appointment = PublicAppointment.objects.get(id=aid)  # type: ignore
        appointment.delete()
        messages.success(request, 'Appointment deleted successfully!')
    except PublicAppointment.DoesNotExist:  # type: ignore
        messages.error(request, 'Appointment not found!')
    
    return redirect('clinic:view_appointment')

@login_required
def View_Schedules(request):
    """View all doctor schedules"""
    schedules = DoctorSchedule.objects.select_related('doctor', 'service').order_by('date', 'start_time')  # type: ignore
    doctors = Doctor.objects.all()  # type: ignore
    services = Service.objects.all()  # type: ignore
    
    context = {
        'schedules': schedules,
        'doctors': doctors,
        'services': services
    }
    return render(request, 'view_schedules.html', context)



@login_required
def Update_Doctor_Availability(request, doctor_id):
    """Update doctor availability for specific dates"""
    try:
        doctor = Doctor.objects.get(id=doctor_id)  # type: ignore
    except Doctor.DoesNotExist:  # type: ignore
        messages.error(request, 'Doctor not found!')
        return redirect('clinic:doctor_schedules_overview')
    
    if request.method == 'POST':
        schedule_date = request.POST.get('date')
        is_available = request.POST.get('is_available') == 'on'
        
        # Update all schedules for this doctor on this date
        schedules = DoctorSchedule.objects.filter(doctor=doctor, date=schedule_date)  # type: ignore
        schedules.update(is_available=is_available)
        
        status = "available" if is_available else "unavailable"
        messages.success(request, f'Dr. {doctor.name} marked as {status} for {schedule_date}')
        return redirect('clinic:doctor_schedules_overview')
    
    # Get doctor's schedules for the next 30 days
    today = date.today()
    end_date = today + timedelta(days=30)
    schedules = DoctorSchedule.objects.filter( # type: ignore
        doctor=doctor,
        date__gte=today,
        date__lte=end_date
    ).order_by('date')  # type: ignore
    
    context = {
        'doctor': doctor,
        'schedules': schedules
    }
    return render(request, 'update_doctor_availability.html', context)

@login_required
def Manage_Services(request):
    """Manage services - add/edit/delete"""
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add':
            try:
                Service.objects.create( # type: ignore
                    name=request.POST.get('name'),
                    description=request.POST.get('description', ''),
                    duration_minutes=request.POST.get('duration_minutes', 30),
                    price=request.POST.get('price', 0.00)
                )  # type: ignore
                messages.success(request, 'Service added successfully!')
            except Exception as e:
                messages.error(request, f'Error adding service: {str(e)}')
        
        elif action == 'update':
            service_id = request.POST.get('service_id')
            try:
                service = Service.objects.get(id=service_id)  # type: ignore
                service.name = request.POST.get('name')
                service.description = request.POST.get('description', '')
                service.duration_minutes = request.POST.get('duration_minutes', 30)
                service.price = request.POST.get('price', 0.00)
                service.save()
                messages.success(request, 'Service updated successfully!')
            except Service.DoesNotExist:  # type: ignore
                messages.error(request, 'Service not found!')
            except Exception as e:
                messages.error(request, f'Error updating service: {str(e)}')
        
        elif action == 'delete':
            service_id = request.POST.get('service_id')
            try:
                service = Service.objects.get(id=service_id)  # type: ignore
                service.delete()
                messages.success(request, 'Service deleted successfully!')
            except Service.DoesNotExist:  # type: ignore
                messages.error(request, 'Service not found!')
            except Exception as e:
                messages.error(request, f'Error deleting service: {str(e)}')
        
        return redirect('clinic:manage_services')
    
    services = Service.objects.all().order_by('name')  # type: ignore
    
    context = {
        'services': services
    }
    return render(request, 'manage_services.html', context)

@login_required
def Edit_Doctor(request, doctor_id):
    """Edit doctor information"""
    try:
        doctor = Doctor.objects.get(id=doctor_id)  # type: ignore
        if request.method == 'POST':
            doctor.name = request.POST.get('name')
            doctor.mobile = request.POST.get('mobile')
            doctor.special = request.POST.get('special')
            doctor.email = request.POST.get('email', '')
            doctor.qualification = request.POST.get('qualification', '')
            doctor.experience = request.POST.get('experience', 0)
            doctor.consultation_fee = request.POST.get('consultation_fee', 0.00)
            doctor.save()
            messages.success(request, 'Doctor updated successfully!')
            return redirect('clinic:view_doctor')
        
        context = {'doctor': doctor}
        return render(request, 'edit_doctor.html', context)
    except Doctor.DoesNotExist:  # type: ignore
        messages.error(request, 'Doctor not found!')
        return redirect('clinic:view_doctor')

@login_required
def Edit_Patient(request, patient_id):
    """Edit patient information"""
    try:
        patient = Patient.objects.get(id=patient_id)  # type: ignore
        if request.method == 'POST':
            patient.name = request.POST.get('name')
            patient.gender = request.POST.get('gender')
            patient.mobile = request.POST.get('mobile')
            patient.age = request.POST.get('age')
            patient.address = request.POST.get('address')
            patient.email = request.POST.get('email', '')
            patient.blood_group = request.POST.get('blood_group', '')
            patient.emergency_contact = request.POST.get('emergency_contact', '')
            patient.medical_history = request.POST.get('medical_history', '')
            patient.save()
            messages.success(request, 'Patient updated successfully!')
            return redirect('clinic:view_patient')
        
        context = {'patient': patient}
        return render(request, 'edit_patient.html', context)
    except Patient.DoesNotExist:  # type: ignore
        messages.error(request, 'Patient not found!')
        return redirect('clinic:view_patient')

@login_required
def Edit_Appointment(request, appointment_id):
    """Edit appointment information"""
    try:
        appointment = PublicAppointment.objects.get(id=appointment_id)  # type: ignore
        if request.method == 'POST':
            appointment.patient_name = request.POST.get('patient_name')
            appointment.patient_age = request.POST.get('patient_age')
            appointment.patient_gender = request.POST.get('patient_gender')
            appointment.patient_mobile = request.POST.get('patient_mobile')
            appointment.patient_address = request.POST.get('patient_address')
            appointment.emergency_contact = request.POST.get('emergency_contact', '')
            appointment.doctor_id = request.POST.get('doctor')
            appointment.service_id = request.POST.get('service')
            appointment.date = request.POST.get('date')
            appointment.time = request.POST.get('time')
            appointment.status = request.POST.get('status')
            appointment.payment_status = request.POST.get('payment_status')
            appointment.notes = request.POST.get('notes', '')
            appointment.save()
            # If status is now completed, ensure patient exists
            if appointment.status == 'completed':
                ensure_patient_from_appointment(
                    appointment.patient_name,
                    appointment.patient_age,
                    appointment.patient_gender,
                    appointment.patient_mobile,
                    appointment.patient_address,
                    email=None,
                    blood_group=None,
                    emergency_contact=appointment.emergency_contact,
                    medical_history=None
                )
            messages.success(request, 'Appointment updated successfully!')
            return redirect('clinic:view_appointment')
        
        doctors = Doctor.objects.all()  # type: ignore
        services = Service.objects.all()  # type: ignore
        context = {
            'appointment': appointment,
            'doctors': doctors,
            'services': services,
        }
        return render(request, 'edit_appointment.html', context)
    except PublicAppointment.DoesNotExist:  # type: ignore
        messages.error(request, 'Appointment not found!')
        return redirect('clinic:view_appointment')

@login_required
def doctor_schedules_overview(request):
    """Overview page showing all doctors with their schedule summaries"""
    doctors = Doctor.objects.all().prefetch_related('doctorschedule_set')  # type: ignore
    services = Service.objects.all()  # type: ignore
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add':
            try:
                DoctorSchedule.objects.create( # type: ignore
                    doctor_id=request.POST.get('doctor'),
                    service_id=request.POST.get('service'),
                    date=request.POST.get('date'),
                    start_time=request.POST.get('start_time'),
                    end_time=request.POST.get('end_time'),
                    is_available=request.POST.get('is_available') == 'on'
                )  # type: ignore
                messages.success(request, 'Schedule added successfully!')
            except Exception as e:
                messages.error(request, f'Error adding schedule: {str(e)}')
        
        return redirect('clinic:doctor_schedules_overview')
    
    # Get schedule statistics for each doctor
    for doctor in doctors:
        today = date.today()
        end_date = today + timedelta(days=30)
        
        # Get upcoming schedules
        upcoming_schedules = DoctorSchedule.objects.filter( # type: ignore
            doctor=doctor,
            date__gte=today,
            date__lte=end_date,
            is_available=True
        ).count()
        
        # Get total schedules this month
        total_schedules = DoctorSchedule.objects.filter( # type: ignore
            doctor=doctor,
            date__gte=today,
            date__lte=end_date
        ).count()
        
        doctor.upcoming_schedules = upcoming_schedules
        doctor.total_schedules = total_schedules
    
    context = {
        'doctors': doctors,
        'services': services
    }
    return render(request, 'doctor_schedules_overview.html', context)

@login_required
def doctor_schedule_calendar(request, doctor_id):
    """Individual doctor schedule calendar view"""
    try:
        doctor = Doctor.objects.get(id=doctor_id)  # type: ignore
    except Doctor.DoesNotExist:  # type: ignore
        messages.error(request, 'Doctor not found!')
        return redirect('clinic:doctor_schedules_overview')
    
    # Get current month/year from request or use current date
    year = int(request.GET.get('year', date.today().year))
    month = int(request.GET.get('month', date.today().month))
    
    # Get all schedules for this doctor in the specified month
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(year, month + 1, 1) - timedelta(days=1)
    
    schedules = DoctorSchedule.objects.filter( # type: ignore
        doctor=doctor,
        date__gte=start_date,
        date__lte=end_date
    ).select_related('service').order_by('date', 'start_time')
    
    # Group schedules by date for calendar display
    calendar_data = {}
    for schedule in schedules:
        date_str = schedule.date.strftime('%Y-%m-%d')
        if date_str not in calendar_data:
            calendar_data[date_str] = []
        calendar_data[date_str].append(schedule)
    
    # Generate calendar days
    import calendar
    cal = calendar.monthcalendar(year, month)
    calendar_days = []
    today = date.today()
    
    for week in cal:
        for day in week:
            if day == 0:
                # Empty day (from previous/next month)
                calendar_days.append({
                    'day': '',
                    'date': None,
                    'is_other_month': True,
                    'is_today': False,
                    'schedules': []
                })
            else:
                current_date = date(year, month, day)
                date_str = current_date.strftime('%Y-%m-%d')
                day_schedules = calendar_data.get(date_str, [])
                
                calendar_days.append({
                    'day': day,
                    'date': current_date,
                    'is_other_month': False,
                    'is_today': current_date == today,
                    'schedules': day_schedules
                })
    
    # Get services for adding new schedules
    services = Service.objects.all()  # type: ignore
    
    context = {
        'doctor': doctor,
        'year': year,
        'month': month,
        'calendar_days': calendar_days,
        'calendar_data': calendar_data,
        'services': services,
        'start_date': start_date,
        'end_date': end_date
    }
    return render(request, 'doctor_schedule_calendar.html', context)

@login_required
def add_schedule_ajax(request, doctor_id):
    """AJAX endpoint to add a new schedule for a doctor"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    
    try:
        doctor = Doctor.objects.get(id=doctor_id)  # type: ignore
    except Doctor.DoesNotExist:  # type: ignore
        return JsonResponse({'success': False, 'error': 'Doctor not found'})
    
    try:
        data = json.loads(request.body)
        
        # Validate required fields
        required_fields = ['service_id', 'date', 'start_time', 'end_time']
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({'success': False, 'error': f'{field} is required'})
        
        # Convert string date to date object
        from datetime import datetime
        date_obj = datetime.strptime(data['date'], '%Y-%m-%d').date()
        
        # Create the schedule
        schedule = DoctorSchedule.objects.create( # type: ignore
            doctor=doctor,
            service_id=data['service_id'],
            date=date_obj,
            start_time=data['start_time'],
            end_time=data['end_time'],
            is_available=data.get('is_available', True)
        )
        
        return JsonResponse({
            'success': True,
            'schedule': {
                'id': schedule.id,
                'service_name': schedule.service.name,
                'date': schedule.date.strftime('%Y-%m-%d'),
                'start_time': schedule.start_time.strftime('%H:%M'),
                'end_time': schedule.end_time.strftime('%H:%M'),
                'is_available': schedule.is_available
            }
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def update_schedule_ajax(request, doctor_id, schedule_id):
    """AJAX endpoint to update an existing schedule"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    
    try:
        doctor = Doctor.objects.get(id=doctor_id)  # type: ignore
        schedule = DoctorSchedule.objects.get(id=schedule_id, doctor=doctor)  # type: ignore
    except (Doctor.DoesNotExist, DoctorSchedule.DoesNotExist):  # type: ignore
        return JsonResponse({'success': False, 'error': 'Doctor or schedule not found'})
    
    try:
        data = json.loads(request.body)
        
        # Update schedule fields
        if 'service_id' in data:
            schedule.service_id = data['service_id']
        if 'date' in data:
            # Convert string date to date object
            from datetime import datetime
            date_obj = datetime.strptime(data['date'], '%Y-%m-%d').date()
            schedule.date = date_obj
        if 'start_time' in data:
            schedule.start_time = data['start_time']
        if 'end_time' in data:
            schedule.end_time = data['end_time']
        if 'is_available' in data:
            schedule.is_available = data['is_available']
        
        schedule.save()
        
        return JsonResponse({
            'success': True,
            'schedule': {
                'id': schedule.id,
                'service_name': schedule.service.name,
                'date': schedule.date.strftime('%Y-%m-%d'),
                'start_time': schedule.start_time.strftime('%H:%M'),
                'end_time': schedule.end_time.strftime('%H:%M'),
                'is_available': schedule.is_available
            }
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def delete_schedule_ajax(request, doctor_id, schedule_id):
    """AJAX endpoint to delete a schedule"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    
    try:
        doctor = Doctor.objects.get(id=doctor_id)  # type: ignore
        schedule = DoctorSchedule.objects.get(id=schedule_id, doctor=doctor)  # type: ignore
    except (Doctor.DoesNotExist, DoctorSchedule.DoesNotExist):  # type: ignore
        return JsonResponse({'success': False, 'error': 'Doctor or schedule not found'})
    
    try:
        schedule.delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def get_schedule_details_ajax(request, doctor_id, schedule_id):
    """AJAX endpoint to get schedule details for editing"""
    try:
        doctor = Doctor.objects.get(id=doctor_id)  # type: ignore
        schedule = DoctorSchedule.objects.get(id=schedule_id, doctor=doctor)  # type: ignore
    except (Doctor.DoesNotExist, DoctorSchedule.DoesNotExist):  # type: ignore
        return JsonResponse({'success': False, 'error': 'Doctor or schedule not found'})
    
    return JsonResponse({
        'success': True,
        'schedule': {
            'id': schedule.id,
            'service_id': schedule.service.id,
            'service_name': schedule.service.name,
            'date': schedule.date.strftime('%Y-%m-%d'),
            'start_time': schedule.start_time.strftime('%H:%M'),
            'end_time': schedule.end_time.strftime('%H:%M'),
            'is_available': schedule.is_available
        }
    })

@login_required
def view_patient_detail(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    appointments = Appointment.objects.filter(patient=patient).select_related('doctor').order_by('-date1', '-time1')
    # Also fetch matching PublicAppointments (by name and mobile)
    public_appointments = PublicAppointment.objects.filter(
        patient_name=patient.name,
        patient_mobile=patient.mobile
    ).order_by('-date', '-time')
    return render(request, 'view_patient_detail.html', {
        'patient': patient,
        'appointments': appointments,
        'public_appointments': public_appointments,
    })

def test_modal(request):
    return render(request, 'test_modal.html')

# Utility function to add patient from appointment if not exists

def ensure_patient_from_appointment(patient_name, patient_age, patient_gender, patient_mobile, patient_address, email=None, blood_group=None, emergency_contact=None, medical_history=None):
    # Try to find a matching patient (by name, age, gender, mobile)
    patient = Patient.objects.filter(
        name=patient_name.strip(),
        age=patient_age,
        gender=patient_gender,
        mobile=patient_mobile.strip()
    ).first()
    if not patient:
        patient = Patient.objects.create(
            name=patient_name.strip(),
            age=patient_age,
            gender=patient_gender,
            mobile=patient_mobile.strip(),
            address=patient_address,
            email=email or '',
            blood_group=blood_group or '',
            emergency_contact=emergency_contact or '',
            medical_history=medical_history or ''
        )
    return patient