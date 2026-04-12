from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.contrib import messages

from .forms import SignUpForm, LoginForm
from .models import UserProfile


def home(request):
    return render(request, 'core/home.html')


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = SignUpForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data['email']
            user.save()

            role = form.cleaned_data['role']
            image = form.cleaned_data.get('image')
            phone = form.cleaned_data.get('phone')
            address = form.cleaned_data.get('address')

            UserProfile.objects.create(
                user=user,
                role=role,
                image=image,
                phone=phone,
                address=address
            )

            # Create group if not exists and assign user
            group_name = ''
            if role == 'patient':
                group_name = 'Patient'
            elif role == 'doctor':
                group_name = 'Doctor'
            elif role == 'admin_staff':
                group_name = 'AdminStaff'

            group, created = Group.objects.get_or_create(name=group_name)
            user.groups.add(group)

            messages.success(request, 'Account created successfully. Please log in.')
            return redirect('login')
    else:
        form = SignUpForm()

    return render(request, 'core/signup.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = LoginForm(request=request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'Login successful.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()

    return render(request, 'core/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('login')


@login_required
def dashboard_view(request):
    profile = getattr(request.user, 'profile', None)
    return render(request, 'core/dashboard.html', {'profile': profile})