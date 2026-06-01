from django.urls import path
from django.shortcuts import redirect
from . import views

urlpatterns = [
    path('', lambda request: redirect('student_dashboard'), name='root_redirect'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    
    # AJAX APIs
    path('api/complaints/raise/', views.raise_complaint_api, name='raise_complaint_api'),
    path('api/notifications/read/', views.mark_notifications_read, name='mark_notifications_read'),
]
