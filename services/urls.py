from django.urls import path
from . import views

urlpatterns = [
    path('prices/', views.price_list, name='price_list'),
    path('api/calc-tint/', views.calculate_tint_price, name='calc_tint_price'),
    path('api/calc-armor/', views.calculate_armor_price, name='calc_armor_price'),
    path('api/calc-armor-element/', views.calculate_armor_element_price, name='calc_armor_element_price'),
    path('api/film-percents/', views.get_film_percents, name='film_percents'),
    path('api/tint-services/', views.get_tint_services, name='tint_services'),
    path('api/armor-elements/', views.get_armor_elements, name='armor_elements'),
]
