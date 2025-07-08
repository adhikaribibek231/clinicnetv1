from django.shortcuts import render, redirect
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
from PIL import Image, ImageDraw, ImageFont

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
    appointments = PublicAppointment.objects.all()
    services = Service.objects.all()
    
    # Get recent appointments (last 10)
    recent_appointments = PublicAppointment.objects.select_related('doctor', 'service').order_by('-created_at')[:10]
    
    d = doctors.count()
    p = patients.count()
    a = appointments.count()
    services_count = services.count()
    
    # Get database statistics
    db_stats = get_db_stats()
    
    context = {
        'd': d, 
        'p': p, 
        'a': a,
        'services_count': services_count,
        'recent_appointments': recent_appointments,
        'db_stats': db_stats
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
        email = request.POST.get('email', '')
        qualification = request.POST.get('qualification', '')
        experience = request.POST.get('experience', 0)
        consultation_fee = request.POST.get('consultation_fee', 0)

        try:
            Doctor.objects.create(
                name=name, 
                mobile=mobile, 
                special=special,
                email=email,
                qualification=qualification,
                experience=experience,
                consultation_fee=consultation_fee
            )
            error = "no"
        except Exception as e:
            print(f"Error creating doctor: {e}")
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
        email = request.POST.get('email', '')
        blood_group = request.POST.get('blood_group', '')
        emergency_contact = request.POST.get('emergency_contact', '')
        medical_history = request.POST.get('medical_history', '')

        try:
            Patient.objects.create(
                name=name, 
                gender=gender, 
                mobile=mobile, 
                age=age, 
                address=address,
                email=email,
                blood_group=blood_group,
                emergency_contact=emergency_contact,
                medical_history=medical_history
            )
            error = "no"
        except Exception as e:
            print(f"Error creating patient: {e}")
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
    # Get only new appointments
    appointments = PublicAppointment.objects.select_related('doctor', 'service').all().order_by('-created_at')
    
    context = {
        'appointments': appointments
    }
    return render(request, 'view_appointment.html', context)

@login_required
def Delete_Appointment(request, aid):
    try:
        appointment = PublicAppointment.objects.get(id=aid)
        appointment.delete()
        messages.success(request, 'Appointment deleted successfully!')
    except PublicAppointment.DoesNotExist:
        messages.error(request, 'Appointment not found!')
    
    return redirect('clinic:view_appointment')

@login_required
def View_Schedules(request):
    """View all doctor schedules"""
    schedules = DoctorSchedule.objects.select_related('doctor', 'service').order_by('date', 'start_time')
    doctors = Doctor.objects.all()
    services = Service.objects.all()
    
    context = {
        'schedules': schedules,
        'doctors': doctors,
        'services': services
    }
    return render(request, 'view_schedules.html', context)

@login_required
def Manage_Schedules(request):
    """Manage doctor schedules - add/edit/delete"""
    doctors = Doctor.objects.all()
    services = Service.objects.all()
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add':
            try:
                DoctorSchedule.objects.create(
                    doctor_id=request.POST.get('doctor'),
                    service_id=request.POST.get('service'),
                    date=request.POST.get('date'),
                    start_time=request.POST.get('start_time'),
                    end_time=request.POST.get('end_time'),
                    is_available=request.POST.get('is_available') == 'on'
                )
                messages.success(request, 'Schedule added successfully!')
            except Exception as e:
                messages.error(request, f'Error adding schedule: {str(e)}')
        
        elif action == 'update':
            schedule_id = request.POST.get('schedule_id')
            try:
                schedule = DoctorSchedule.objects.get(id=schedule_id)
                schedule.doctor_id = request.POST.get('doctor')
                schedule.service_id = request.POST.get('service')
                schedule.date = request.POST.get('date')
                schedule.start_time = request.POST.get('start_time')
                schedule.end_time = request.POST.get('end_time')
                schedule.is_available = request.POST.get('is_available') == 'on'
                schedule.save()
                messages.success(request, 'Schedule updated successfully!')
            except DoctorSchedule.DoesNotExist:
                messages.error(request, 'Schedule not found!')
            except Exception as e:
                messages.error(request, f'Error updating schedule: {str(e)}')
        
        elif action == 'delete':
            schedule_id = request.POST.get('schedule_id')
            try:
                schedule = DoctorSchedule.objects.get(id=schedule_id)
                schedule.delete()
                messages.success(request, 'Schedule deleted successfully!')
            except DoctorSchedule.DoesNotExist:
                messages.error(request, 'Schedule not found!')
            except Exception as e:
                messages.error(request, f'Error deleting schedule: {str(e)}')
        
        return redirect('clinic:manage_schedules')
    
    schedules = DoctorSchedule.objects.select_related('doctor', 'service').order_by('date', 'start_time')
    
    context = {
        'schedules': schedules,
        'doctors': doctors,
        'services': services
    }
    return render(request, 'manage_schedules.html', context)

@login_required
def Update_Doctor_Availability(request, doctor_id):
    """Update doctor availability for specific dates"""
    try:
        doctor = Doctor.objects.get(id=doctor_id)
    except Doctor.DoesNotExist:
        messages.error(request, 'Doctor not found!')
        return redirect('clinic:manage_schedules')
    
    if request.method == 'POST':
        date = request.POST.get('date')
        is_available = request.POST.get('is_available') == 'on'
        
        # Update all schedules for this doctor on this date
        schedules = DoctorSchedule.objects.filter(doctor=doctor, date=date)
        schedules.update(is_available=is_available)
        
        status = "available" if is_available else "unavailable"
        messages.success(request, f'Dr. {doctor.name} marked as {status} for {date}')
        return redirect('clinic:manage_schedules')
    
    # Get doctor's schedules for the next 30 days
    today = date.today()
    end_date = today + timedelta(days=30)
    schedules = DoctorSchedule.objects.filter(
        doctor=doctor,
        date__gte=today,
        date__lte=end_date
    ).order_by('date')
    
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
                Service.objects.create(
                    name=request.POST.get('name'),
                    description=request.POST.get('description', ''),
                    duration_minutes=request.POST.get('duration_minutes', 30),
                    price=request.POST.get('price', 0.00)
                )
                messages.success(request, 'Service added successfully!')
            except Exception as e:
                messages.error(request, f'Error adding service: {str(e)}')
        
        elif action == 'update':
            service_id = request.POST.get('service_id')
            try:
                service = Service.objects.get(id=service_id)
                service.name = request.POST.get('name')
                service.description = request.POST.get('description', '')
                service.duration_minutes = request.POST.get('duration_minutes', 30)
                service.price = request.POST.get('price', 0.00)
                service.save()
                messages.success(request, 'Service updated successfully!')
            except Service.DoesNotExist:
                messages.error(request, 'Service not found!')
            except Exception as e:
                messages.error(request, f'Error updating service: {str(e)}')
        
        elif action == 'delete':
            service_id = request.POST.get('service_id')
            try:
                service = Service.objects.get(id=service_id)
                service.delete()
                messages.success(request, 'Service deleted successfully!')
            except Service.DoesNotExist:
                messages.error(request, 'Service not found!')
            except Exception as e:
                messages.error(request, f'Error deleting service: {str(e)}')
        
        return redirect('clinic:manage_services')
    
    services = Service.objects.all().order_by('name')
    
    context = {
        'services': services
    }
    return render(request, 'manage_services.html', context)

@login_required
def Edit_Doctor(request, doctor_id):
    """Edit doctor information"""
    try:
        doctor = Doctor.objects.get(id=doctor_id)
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
    except Doctor.DoesNotExist:
        messages.error(request, 'Doctor not found!')
        return redirect('clinic:view_doctor')

@login_required
def Edit_Patient(request, patient_id):
    """Edit patient information"""
    try:
        patient = Patient.objects.get(id=patient_id)
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
    except Patient.DoesNotExist:
        messages.error(request, 'Patient not found!')
        return redirect('clinic:view_patient')

@login_required
def Edit_Appointment(request, appointment_id):
    """Edit appointment information"""
    try:
        appointment = PublicAppointment.objects.get(id=appointment_id)
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
            messages.success(request, 'Appointment updated successfully!')
            return redirect('clinic:view_appointment')
        
        doctors = Doctor.objects.all()
        services = Service.objects.all()
        context = {
            'appointment': appointment,
            'doctors': doctors,
            'services': services,
        }
        return render(request, 'edit_appointment.html', context)
    except PublicAppointment.DoesNotExist:
        messages.error(request, 'Appointment not found!')
        return redirect('clinic:view_appointment')

