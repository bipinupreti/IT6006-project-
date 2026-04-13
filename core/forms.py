from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

from .models import Appointment, UserProfile


class DoctorModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        specialty = getattr(obj.profile, 'specialty', None)
        specialty_label = f" - {obj.profile.get_specialty_display()}" if specialty else ''
        if obj.email:
            return f"{obj.username} ({obj.email}){specialty_label}"
        return f"{obj.username}{specialty_label}"


class SignUpForm(UserCreationForm):
    ROLE_CHOICES = (
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
        ('admin_staff', 'Admin Staff'),
    )

    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=ROLE_CHOICES)
    image = forms.ImageField(required=False)
    phone = forms.CharField(max_length=20, required=False)
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)
    specialty = forms.ChoiceField(choices=[('', 'Select Specialty')] + list(UserProfile.SPECIALTY_CHOICES), required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'role', 'specialty', 'image', 'phone', 'address']

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        specialty = cleaned_data.get('specialty')
        if role == 'doctor' and not specialty:
            raise forms.ValidationError('Doctor signup requires selecting a specialty.')
        if role != 'doctor':
            cleaned_data['specialty'] = ''
        return cleaned_data


class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['image', 'phone', 'address', 'specialty']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'specialty': forms.Select(attrs={'class': 'form-control'}),
        }


class AdminDoctorForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }


class AppointmentForm(forms.ModelForm):
    specialty = forms.ChoiceField(
        choices=[('', 'Select Specialty')] + list(UserProfile.SPECIALTY_CHOICES),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    doctor = DoctorModelChoiceField(
        queryset=User.objects.filter(profile__role='doctor'),
        empty_label="Select Doctor"
    )

    class Meta:
        model = Appointment
        fields = ['specialty', 'doctor', 'appointment_date', 'appointment_time', 'reason']
        widgets = {
            'appointment_date': forms.DateInput(attrs={'type': 'date'}),
            'appointment_time': forms.TimeInput(attrs={'type': 'time'}),
            'reason': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Enter reason for appointment'}),
        }

    def __init__(self, *args, **kwargs):
        patient = kwargs.pop('patient', None)
        super().__init__(*args, **kwargs)

        selected_specialty = None
        if self.data.get('specialty'):
            selected_specialty = self.data.get('specialty')
        elif self.instance.pk and self.instance.doctor_id:
            selected_specialty = getattr(self.instance.doctor.profile, 'specialty', None)

        if selected_specialty:
            self.fields['doctor'].queryset = User.objects.filter(profile__role='doctor', profile__specialty=selected_specialty)
            self.fields['specialty'].initial = selected_specialty
        else:
            self.fields['doctor'].queryset = User.objects.filter(profile__role='doctor')

        self.fields['doctor'].empty_label = "Select Doctor"
        self.fields['reason'].required = True

        self.fields['specialty'].widget.attrs.update({'class': 'form-control'})
        self.fields['doctor'].widget.attrs.update({'class': 'form-control'})
        self.fields['appointment_date'].widget.attrs.update({'class': 'form-control'})
        self.fields['appointment_time'].widget.attrs.update({'class': 'form-control'})
        self.fields['reason'].widget.attrs.update({'class': 'form-control'})


class AdminAppointmentForm(forms.ModelForm):
    doctor = DoctorModelChoiceField(
        queryset=User.objects.filter(profile__role='doctor'),
        empty_label="Select Doctor"
    )

    class Meta:
        model = Appointment
        fields = ['doctor', 'appointment_date', 'appointment_time', 'reason', 'status']
        widgets = {
            'appointment_date': forms.DateInput(attrs={'type': 'date'}),
            'appointment_time': forms.TimeInput(attrs={'type': 'time'}),
            'reason': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Enter reason for appointment'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['doctor'].queryset = User.objects.filter(profile__role='doctor')
        self.fields['doctor'].empty_label = "Select Doctor"

        self.fields['doctor'].widget.attrs.update({'class': 'form-control'})
        self.fields['appointment_date'].widget.attrs.update({'class': 'form-control'})
        self.fields['appointment_time'].widget.attrs.update({'class': 'form-control'})
        self.fields['reason'].widget.attrs.update({'class': 'form-control'})
        self.fields['status'].widget.attrs.update({'class': 'form-control'})