from django.contrib import admin
from .models import UserProfile, MedicalRecord


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone')
    search_fields = ('user__username', 'user__email', 'role')


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'diagnosis', 'record_date')
    search_fields = ('patient__username', 'doctor__username', 'diagnosis')