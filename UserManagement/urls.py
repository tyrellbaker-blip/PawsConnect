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
    path('connections/', views.connections, name='connections'),
    path('index/', views.index, name='index'),
    path('network/', views.network, name='network'),

    # Other URL patterns...
]
