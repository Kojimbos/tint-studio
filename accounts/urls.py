from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/add-car/', views.add_car, name='add_car'),
    path('profile/delete-car/<int:car_id>/', views.delete_car, name='delete_car'),
    path('profile/history/', views.booking_history, name='booking_history'),
]
