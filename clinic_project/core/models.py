from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
        ('admin_staff', 'Admin Staff'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"


class MedicalRecord(models.Model):
    patient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='patient_records',
        limit_choices_to={'profile__role': 'patient'}
    )
    doctor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='doctor_records',
        limit_choices_to={'profile__role': 'doctor'}
    )
    diagnosis = models.CharField(max_length=255)
    treatment = models.TextField()
    notes = models.TextField(blank=True)
    record_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Record for {self.patient.username} on {self.record_date}"