from django.shortcuts import render,redirect, get_object_or_404
from django.contrib import auth, messages
from django.contrib.auth.models import User
from . models import UserProfile

# Create your views here.
def login_user(request):
    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            messages.success(request, f"Welcome, {user.username}.")

            try:
                profile = UserProfile.objects.get(user=user)

            except UserProfile.DoesNotExist:
                messages.error(request, "UserProfile does not exist")
                return redirect('landing')

            if profile.role == 'donor':
                return redirect('donor_dashboard')
            elif profile.role == 'consumer':
                return redirect('consumer_dashboard')
            else:
                messages.error(request, "You dont have a Profile")

        else:
            messages.error(request, "Oops! something went wrong")
            return render(request, 'authentication/login.html')
        
    else:
        pass
    
    return render(request, "authentication/login.html")

def register(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if password != confirm_password:
            messages.error(request, "Your password does not match")
            return redirect('register')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exixts")
            return redirect('register')
        
        if email and User.objects.filter(email=email).exists():
            messages.error(request, 'email already exists')
            return redirect('register')
        
        user = User.objects.create_user(username=username, password=password, first_name=first_name, last_name=last_name)
        messages.success(request, f"{user.username} created successfully")
        return redirect('login')
    
    return render(request, 'authentication/register.html')

def logout(request):
    auth.logout(request)
    return redirect('landing')

# TODO: password reset
