from django.urls import path
from . import views

urlpatterns = [
    path('', views.welcome_page, name='welcome_page'),
    path('sign-in/', views.sign_in_reg, name='sig_in_reg'),
    path('show_map/', views.show_map, name='show_map'),
    path('get_profile/', views.get_profile, name='get_profile'),
    path('save_profile/', views.save_profile, name='save_profile'),
    path('exit_profile/', views.exit_profile, name='exit_profile'),
    path('save_col_des_country/', views.save_col_des_country, name='save_col_des_country'),
    path('get_user_countries/', views.get_user_countries, name='get_user_countries'),
    path('save_photo/', views.save_photo, name='save_photo'),
    path('load_photos_country/', views.load_photos_country, name='load_photos_country'),
    path('get_photo/', views.get_photo, name='get_photo'),
    path('delete_photo/', views.delete_photo, name='delete_photo'),
    path('show_info/', views.show_info, name='show_info'),
]