from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_booking, name='create_booking'),
    path('<int:booking_id>/', views.booking_detail, name='booking_detail'),
    path('<int:booking_id>/cancel/', views.cancel_booking, name='cancel_booking'),
    path('api/available-slots/', views.get_available_slots, name='available_slots'),
]
