from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def unified_login(request):
    """Unified login view that redirects to clinic or pharmacy based on user type"""
    if request.user.is_authenticated:
        # If user is already logged in, redirect based on their type
        if hasattr(request.user, 'userprofile'):
            if request.user.userprofile.user_type == 'pharmacy':
                return redirect('pharmacy:home')
            else:
                return redirect('clinic:dashboard')
        else:
            # Default to clinic for existing users without profile
            return redirect('clinic:dashboard')
    
    error = ""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user_type = request.POST.get('user_type', 'clinic')
        
        user = authenticate(username=username, password=password)
        
        if user is not None and user.is_active:
            if user.is_staff:
                login(request, user)
                
                # Create or update user profile
                from .models import UserProfile
                profile, created = UserProfile.objects.get_or_create(
                    user=user,
                    defaults={'user_type': user_type}
                )
                if not created:
                    profile.user_type = user_type
                    profile.save()
                
                messages.success(request, f'Welcome to {user_type.title()} Management System!')
                
                # Redirect based on user type
                if user_type == 'pharmacy':
                    return redirect('pharmacy:home')
                else:
                    return redirect('clinic:dashboard')
            else:
                error = "Access denied. Staff privileges required."
        else:
            error = "Invalid username or password."
    
    return render(request, 'unified_login.html', {'error': error})

@login_required
def unified_logout(request):
    """Unified logout view"""
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('unified_login') 