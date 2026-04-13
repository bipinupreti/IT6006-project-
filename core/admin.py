from django.contrib import admin
from .models import UserProfile, MedicalRecord, Appointment


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone')
    search_fields = ('user__username', 'user__email', 'role')


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'diagnosis', 'record_date')
    search_fields = ('patient__username', 'doctor__username', 'diagnosis')


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'appointment_date', 'appointment_time', 'status')
    search_fields = ('patient__username', 'doctor__username', 'status')
    list_filter = ('status', 'appointment_date')