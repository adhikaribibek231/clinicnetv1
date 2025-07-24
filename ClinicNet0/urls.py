"""
URL configuration for ClinicNet0 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from clinic.views import *
from .views import unified_login, unified_logout

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', Home, name='home'),  # Public home page
    path('login/', unified_login, name='unified_login'),  # Login page
    path('logout/', unified_logout, name='unified_logout'),
    path('about/', About_Public, name='about'),  # Public about page
    path('contact/', Contact_Public, name='contact'),  # Public contact page
    path('book-appointment/', BookAppointment, name='book_appointment_public'),  # Public booking page
    path('clinic/', include('clinic.urls', namespace='clinic')),
    path('pharmacy/', include('pharmacy.urls', namespace='pharmacy')),
    path('labtest/', include('labtest.urls', namespace='labtest')),
]
