from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.contrib import messages

from .forms import SignUpForm, LoginForm, AppointmentForm
from .models import UserProfile, Appointment


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

            if role == 'patient':
                group_name = 'Patient'
            elif role == 'doctor':
                group_name = 'Doctor'
            else:
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

    if profile:
        if profile.role == 'patient':
            return redirect('patient_dashboard')
        if profile.role == 'doctor':
            return render(request, 'core/dashboard.html', {'profile': profile})
        if profile.role == 'admin_staff':
            return redirect('/admin/')

    return render(request, 'core/dashboard.html', {'profile': profile})


@login_required
def patient_dashboard(request):
    profile = getattr(request.user, 'profile', None)

    if not profile or profile.role != 'patient':
        messages.error(request, 'Only patients can access this page.')
        return redirect('dashboard')

    appointments = Appointment.objects.filter(patient=request.user)

    context = {
        'appointments': appointments,
        'profile': profile,
    }
    return render(request, 'core/patient_dashboard.html', context)


@login_required
def book_appointment(request):
    profile = getattr(request.user, 'profile', None)

    if not profile or profile.role != 'patient':
        messages.error(request, 'Only patients can book appointments.')
        return redirect('dashboard')

    if request.method == 'POST':
        form = AppointmentForm(request.POST, patient=request.user)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = request.user
            appointment.status = 'Pending'
            appointment.save()
            messages.success(request, 'Appointment booked successfully.')
            return redirect('patient_dashboard')
    else:
        form = AppointmentForm(patient=request.user)

    return render(request, 'core/book_appointment.html', {'form': form})


@login_required
def update_appointment(request, appointment_id):
    profile = getattr(request.user, 'profile', None)

    if not profile or profile.role != 'patient':
        messages.error(request, 'Only patients can update appointments.')
        return redirect('dashboard')

    appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user)

    if appointment.status == 'Cancelled':
        messages.error(request, 'Cancelled appointments cannot be updated.')
        return redirect('patient_dashboard')

    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment, patient=request.user)
        if form.is_valid():
            updated_appointment = form.save(commit=False)
            updated_appointment.patient = request.user
            updated_appointment.save()
            messages.success(request, 'Appointment updated successfully.')
            return redirect('patient_dashboard')
    else:
        form = AppointmentForm(instance=appointment, patient=request.user)

    return render(request, 'core/update_appointment.html', {
        'form': form,
        'appointment': appointment,
    })


@login_required
def cancel_appointment(request, appointment_id):
    profile = getattr(request.user, 'profile', None)

    if not profile or profile.role != 'patient':
        messages.error(request, 'Only patients can cancel appointments.')
        return redirect('dashboard')

    appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user)

    if request.method == 'POST':
        appointment.status = 'Cancelled'
        appointment.save()
        messages.success(request, 'Appointment cancelled successfully.')
        return redirect('patient_dashboard')

    return render(request, 'core/cancel_appointment.html', {'appointment': appointment})