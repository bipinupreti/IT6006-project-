from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),

    path('patient/', views.patient_dashboard, name='patient_dashboard'),
    path('appointments/book/', views.book_appointment, name='book_appointment'),
    path('appointments/<int:appointment_id>/update/', views.update_appointment, name='update_appointment'),
    path('appointments/<int:appointment_id>/cancel/', views.cancel_appointment, name='cancel_appointment'),
    path('appointments/<int:appointment_id>/confirm/', views.confirm_appointment, name='confirm_appointment'),
    path('appointments/<int:appointment_id>/doctor-cancel/', views.doctor_cancel_appointment, name='doctor_cancel_appointment'),

    path('doctor/', views.doctor_dashboard, name='doctor_dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/doctors/', views.admin_doctors, name='admin_doctors'),
    path('admin-panel/doctors/<int:user_id>/edit/', views.admin_doctor_update, name='admin_doctor_update'),
    path('admin-panel/doctors/<int:user_id>/delete/', views.admin_doctor_delete, name='admin_doctor_delete'),
    path('admin-panel/appointments/', views.admin_appointments, name='admin_appointments'),
    path('admin-panel/appointments/<int:appointment_id>/edit/', views.admin_update_appointment, name='admin_update_appointment'),
]