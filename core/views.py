from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, User
from django.contrib import messages
from django.views.decorators.csrf import ensure_csrf_cookie

from .forms import SignUpForm, LoginForm, AppointmentForm, UserProfileForm, AdminDoctorForm, AdminAppointmentForm
from .models import UserProfile, Appointment, MedicalRecord


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
            specialty = form.cleaned_data.get('specialty')

            UserProfile.objects.create(
                user=user,
                role=role,
                specialty=specialty if role == 'doctor' else None,
                image=image,
                phone=phone,
                address=address
            )

            if role == 'patient':
                group_name = 'Patient'
            elif role == 'doctor':
                group_name = 'Doctor'
            else:
                group_name = 'Admin'

            group, created = Group.objects.get_or_create(name=group_name)
            user.groups.add(group)

            messages.success(request, 'Account created successfully. Please log in.')
            return redirect('login')
    else:
        form = SignUpForm()

    return render(request, 'core/signup.html', {'form': form})


@ensure_csrf_cookie
def login_view(request):
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
        if request.user.is_authenticated:
            messages.info(request, 'You are already logged in. Please logout first to switch accounts.')
        form = LoginForm()

    return render(request, 'core/login.html', {'form': form})


@login_required(login_url='login')
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('login')


@login_required(login_url='login')
def dashboard_view(request):
    profile = getattr(request.user, 'profile', None)

    if profile:
        if profile.role == 'patient':
            return redirect('patient_dashboard')
        if profile.role == 'doctor':
            return redirect('doctor_dashboard')
        if profile.role == 'admin_staff':
            return redirect('admin_dashboard')

    return render(request, 'core/dashboard.html', {'profile': profile})


@login_required(login_url='login')
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


@login_required(login_url='login')
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


@login_required(login_url='login')
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


@login_required(login_url='login')
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


@login_required(login_url='login')
def confirm_appointment(request, appointment_id):
    profile = getattr(request.user, 'profile', None)

    if not profile or profile.role != 'doctor':
        messages.error(request, 'Only doctors can confirm appointments.')
        return redirect('dashboard')

    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=request.user)

    if appointment.status == 'Cancelled':
        messages.error(request, 'Cancelled appointments cannot be confirmed.')
    else:
        appointment.status = 'Confirmed'
        appointment.save()
        messages.success(request, 'Appointment confirmed successfully.')

    return redirect('doctor_dashboard')


@login_required(login_url='login')
def doctor_cancel_appointment(request, appointment_id):
    profile = getattr(request.user, 'profile', None)

    if not profile or profile.role != 'doctor':
        messages.error(request, 'Only doctors can cancel appointments.')
        return redirect('dashboard')

    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=request.user)

    if appointment.status == 'Cancelled':
        messages.info(request, 'Appointment is already cancelled.')
    else:
        appointment.status = 'Cancelled'
        appointment.save()
        messages.success(request, 'Appointment cancelled successfully.')

    return redirect('doctor_dashboard')


@login_required(login_url='login')
def admin_doctors(request):
    profile = getattr(request.user, 'profile', None)

    if not profile or profile.role != 'admin_staff':
        messages.error(request, 'Only admin users can access this page.')
        return redirect('dashboard')

    doctors = User.objects.filter(profile__role='doctor')
    return render(request, 'core/admin_doctors.html', {'doctors': doctors, 'profile': profile})


@login_required(login_url='login')
def admin_doctor_update(request, user_id):
    profile = getattr(request.user, 'profile', None)
    if not profile or profile.role != 'admin_staff':
        messages.error(request, 'Only admin users can access this page.')
        return redirect('dashboard')

    doctor_user = get_object_or_404(User, id=user_id, profile__role='doctor')
    doctor_profile = doctor_user.profile

    if request.method == 'POST':
        user_form = AdminDoctorForm(request.POST, instance=doctor_user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=doctor_profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Doctor profile updated successfully.')
            return redirect('admin_doctors')
    else:
        user_form = AdminDoctorForm(instance=doctor_user)
        profile_form = UserProfileForm(instance=doctor_profile)

    return render(request, 'core/admin_doctor_form.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'doctor_user': doctor_user,
    })


@login_required(login_url='login')
def admin_doctor_delete(request, user_id):
    profile = getattr(request.user, 'profile', None)
    if not profile or profile.role != 'admin_staff':
        messages.error(request, 'Only admin users can access this page.')
        return redirect('dashboard')

    doctor_user = get_object_or_404(User, id=user_id, profile__role='doctor')

    if request.method == 'POST':
        doctor_user.delete()
        messages.success(request, 'Doctor removed successfully.')
        return redirect('admin_doctors')

    return render(request, 'core/admin_doctor_confirm_delete.html', {'doctor_user': doctor_user})


@login_required(login_url='login')
def admin_appointments(request):
    profile = getattr(request.user, 'profile', None)
    if not profile or profile.role != 'admin_staff':
        messages.error(request, 'Only admin users can access this page.')
        return redirect('dashboard')

    appointments = Appointment.objects.all().order_by('-appointment_date', '-appointment_time')
    return render(request, 'core/admin_appointments.html', {'appointments': appointments, 'profile': profile})


@login_required(login_url='login')
def admin_update_appointment(request, appointment_id):
    profile = getattr(request.user, 'profile', None)
    if not profile or profile.role != 'admin_staff':
        messages.error(request, 'Only admin users can access this page.')
        return redirect('dashboard')

    appointment = get_object_or_404(Appointment, id=appointment_id)

    if request.method == 'POST':
        form = AdminAppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Appointment updated successfully.')
            return redirect('admin_appointments')
    else:
        form = AdminAppointmentForm(instance=appointment)

    return render(request, 'core/admin_appointment_form.html', {
        'form': form,
        'appointment': appointment,
    })


@login_required(login_url='login')
def doctor_dashboard(request):
    profile = getattr(request.user, 'profile', None)

    if not profile or profile.role != 'doctor':
        messages.error(request, 'Only doctors can access this page.')
        return redirect('dashboard')

    appointments = Appointment.objects.filter(doctor=request.user)
    context = {
        'profile': profile,
        'appointments': appointments,
    }
    return render(request, 'core/doctor_dashboard.html', context)


@login_required(login_url='login')
def admin_dashboard(request):
    profile = getattr(request.user, 'profile', None)

    if not profile or profile.role != 'admin_staff':
        messages.error(request, 'Only admin users can access this page.')
        return redirect('dashboard')

    total_users = User.objects.count()
    total_patients = UserProfile.objects.filter(role='patient').count()
    total_doctors = UserProfile.objects.filter(role='doctor').count()
    total_admins = UserProfile.objects.filter(role='admin_staff').count()
    total_appointments = Appointment.objects.count()
    total_medical_records = MedicalRecord.objects.count()

    context = {
        'profile': profile,
        'total_users': total_users,
        'total_patients': total_patients,
        'total_doctors': total_doctors,
        'total_admins': total_admins,
        'total_appointments': total_appointments,
        'total_medical_records': total_medical_records,
    }
    return render(request, 'core/admin_dashboard.html', context)