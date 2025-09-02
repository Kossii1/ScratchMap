from django.urls import path
from . import views

urlpatterns = [
    path('', views.welcome_page, name='welcome_page'),
    path('sign-in/', views.sign_in_reg, name='sig_in_reg'),
    path('show_map/', views.show_map, name='show_map'),
    path('get_profile/', views.get_profile, name='get_profile'),
    path('show_info/', views.show_info, name='show_info'),
]