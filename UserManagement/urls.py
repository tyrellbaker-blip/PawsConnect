# UserManagement/urls.py
from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'UserManagement'

urlpatterns = [
    path('home/', views.home, name='home'),

    path('login/', views.user_login, name='login'),
    path('logout/', LogoutView.as_view(next_page='UserManagement:login'), name='logout'),
    path('register/', views.register, name='register'),
    path('landing/', views.landing_page, name='landing_page'),
    path('profile/', views.profile, name='profile'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('friends/', views.friends, name='friends'),
    path('photos/', views.photos, name='photos'),
    path('pets/', views.pets, name='pets'),
]
