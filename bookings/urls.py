from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('employees/', views.employee_list_view, name='employee_list'),
    path('book/<int:employee_pk>/', views.create_booking_view, name='create_booking'),
    path('bookings/', views.booking_list_view, name='booking_list'),
    path('bookings/<int:pk>/', views.booking_detail_view, name='booking_detail'),
    path('bookings/<int:pk>/<str:action>/', views.booking_action_view, name='booking_action'),
    path('bookings/<int:booking_pk>/review/', views.add_review_view, name='add_review'),
    path('bookings/<int:booking_pk>/proof/', views.add_work_proof_view, name='add_work_proof'),
]
