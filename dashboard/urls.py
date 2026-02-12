from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_dashboard_view, name='admin_dashboard'),
    path('verify/<int:pk>/', views.verify_employee_view, name='verify_employee'),
]
