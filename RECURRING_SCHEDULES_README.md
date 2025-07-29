# Recurring Schedules System

## Overview

The ClinicNet system now supports **recurring schedules** that automatically generate monthly doctor schedules based on weekly patterns. This eliminates the need to manually create schedules for each month.

## Features

### 1. Recurring Schedule Patterns
- Set up weekly recurring patterns for each doctor
- Define specific days of the week (Monday-Sunday)
- Set start and end times for each pattern
- Associate with specific medical services
- Enable/disable patterns as needed

### 2. Automatic Monthly Generation
- Generate schedules for any month based on recurring patterns
- Avoids duplicate schedules (won't create if already exists)
- Supports both individual doctor and bulk generation
- Command-line tool for automated generation

### 3. Management Interface
- Web-based interface for managing recurring schedules
- Overview page showing all doctors and their patterns
- Edit/delete individual recurring schedules
- Generate monthly schedules with one click

## How It Works

### 1. Setting Up Recurring Patterns

1. **Access the Recurring Schedules page**
   - Navigate to: `/clinic/recurring-schedules/`
   - Or click "Recurring Schedules" from the main schedules page

2. **Add a Recurring Schedule**
   - Click "Add Recurring Schedule" button
   - Select doctor, service, day of week, and times
   - Set as active/inactive

3. **Example Pattern**
   ```
   Doctor: Dr. John Smith
   Service: General Consultation
   Day: Monday
   Time: 9:00 AM - 12:00 PM
   Status: Active
   ```

### 2. Generating Monthly Schedules

#### Option A: Web Interface
1. Go to Recurring Schedules page
2. Use the "Generate Monthly Schedules" section
3. Select doctor, month, and year
4. Click "Generate"

#### Option B: Command Line
```bash
# Generate for next month (default)
python manage.py generate_monthly_schedules

# Generate for specific month
python manage.py generate_monthly_schedules --year 2025 --month 2

# Generate for specific doctor
python manage.py generate_monthly_schedules --doctor 1

# Generate for specific doctor and month
python manage.py generate_monthly_schedules --doctor 1 --year 2025 --month 2
```

### 3. Automation

Set up a cron job or scheduled task to automatically generate schedules:

```bash
# Add to crontab to generate next month's schedules on the 25th of each month
0 9 25 * * cd /path/to/clinicnet && python manage.py generate_monthly_schedules
```

## Database Models

### RecurringSchedule Model
```python
class RecurringSchedule(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    day_of_week = models.IntegerField(choices=[...])  # 0=Monday, 6=Sunday
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### DoctorSchedule Model (Enhanced)
The existing `DoctorSchedule` model now includes a class method for generating monthly schedules:

```python
@classmethod
def generate_monthly_schedules(cls, doctor, year, month):
    """Generate all schedules for a doctor for a specific month"""
```

## API Endpoints

### Web Interface URLs
- `/clinic/recurring-schedules/` - Overview page
- `/clinic/recurring-schedules/edit/<id>/` - Edit recurring schedule
- `/clinic/recurring-schedules/delete/<id>/` - Delete recurring schedule
- `/clinic/recurring-schedules/<doctor_id>/generate-monthly/` - AJAX endpoint

### Management Commands
- `generate_monthly_schedules` - Generate schedules for specified month

## Usage Examples

### Setting Up a Doctor's Weekly Schedule

1. **Cardiologist Schedule**
   ```
   Monday: 9:00 AM - 12:00 PM (Cardiology Consultation)
   Tuesday: 9:00 AM - 12:00 PM (Cardiology Consultation)
   Wednesday: 2:00 PM - 5:00 PM (General Consultation)
   Thursday: 9:00 AM - 12:00 PM (Cardiology Consultation)
   Friday: 2:00 PM - 5:00 PM (General Consultation)
   ```

2. **Pediatrician Schedule**
   ```
   Monday: 9:00 AM - 12:00 PM (Pediatric Consultation)
   Tuesday: 2:00 PM - 5:00 PM (Pediatric Consultation)
   Wednesday: 9:00 AM - 12:00 PM (Pediatric Consultation)
   Thursday: 2:00 PM - 5:00 PM (Pediatric Consultation)
   Friday: 9:00 AM - 12:00 PM (Pediatric Consultation)
   Saturday: 9:00 AM - 12:00 PM (Pediatric Consultation)
   ```

### Generating Schedules

```bash
# Generate January 2025 schedules for all doctors
python manage.py generate_monthly_schedules --year 2025 --month 1

# Generate February 2025 schedules for doctor ID 5
python manage.py generate_monthly_schedules --doctor 5 --year 2025 --month 2
```

## Benefits

1. **Time Savings**: No need to manually create schedules each month
2. **Consistency**: Same schedule pattern followed every month
3. **Flexibility**: Easy to modify patterns and regenerate
4. **Automation**: Can be fully automated with cron jobs
5. **Error Prevention**: Reduces manual scheduling errors

## Migration from Manual Scheduling

1. **Set up recurring patterns** for each doctor
2. **Generate schedules** for the next few months
3. **Review and adjust** patterns as needed
4. **Set up automation** for ongoing generation

## Troubleshooting

### Common Issues

1. **No schedules generated**
   - Check if recurring schedules are set to "Active"
   - Verify doctor has recurring patterns set up

2. **Duplicate schedules**
   - The system automatically prevents duplicates
   - Use `--force` flag if you need to regenerate

3. **Wrong times/dates**
   - Check the recurring schedule patterns
   - Verify timezone settings

### Debug Commands

```bash
# Check recurring schedules for a doctor
python manage.py shell
>>> from clinic.models import Doctor, RecurringSchedule
>>> doctor = Doctor.objects.get(id=1)
>>> RecurringSchedule.objects.filter(doctor=doctor, is_active=True)

# Check generated schedules for a month
>>> from datetime import date
>>> from clinic.models import DoctorSchedule
>>> DoctorSchedule.objects.filter(date__year=2025, date__month=1).count()
```

## Future Enhancements

1. **Advanced Patterns**: Support for bi-weekly, monthly patterns
2. **Holiday Exclusions**: Automatically exclude holidays
3. **Bulk Operations**: Edit multiple recurring schedules at once
4. **Template System**: Pre-defined schedule templates
5. **Conflict Detection**: Warn about overlapping schedules

## Support

For issues or questions about the recurring schedules system:
1. Check the Django admin interface for recurring schedules
2. Review the management command output for errors
3. Verify database migrations are applied
4. Check server logs for any errors 