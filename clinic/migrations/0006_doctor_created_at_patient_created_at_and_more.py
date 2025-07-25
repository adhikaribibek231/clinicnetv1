# Generated by Django 5.2 on 2025-07-15 15:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clinic', '0005_doctor_consultation_fee_doctor_email_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='doctor',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='patient',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='publicappointment',
            name='token',
            field=models.CharField(default='C163AB4129', max_length=10, unique=True),
        ),
    ]
