# Generated by Django 5.2 on 2025-07-15 15:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clinic', '0006_doctor_created_at_patient_created_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='pending', max_length=20),
        ),
        migrations.AlterField(
            model_name='publicappointment',
            name='token',
            field=models.CharField(default='0587E91D56', max_length=10, unique=True),
        ),
    ]
