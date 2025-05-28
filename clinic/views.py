from django.shortcuts import render
from django.contrib.auth.models import users
# Create your views here.
def About(request):
    return render(request, 'about.html')
def Index(request):
    if not request.user.is_staff:
        return redirect('login')
    return render(request, 'about.html')
