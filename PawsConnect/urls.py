"""
URL configuration for PawsConnect project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import path, include
from django.contrib.auth.views import LogoutView

from UserManagement.views import user_login, home, register, landing_page

urlpatterns = [
                  path('admin/', admin.site.urls),
                  path('user/', include('UserManagement.urls', namespace='UserManagement')),
                  # Redirect the root URL to the 'home' view within the UserManagement namespace
                  path('', lambda request: redirect('UserManagement:login')),  # Redirect the root URL
                  path('social/', include('SocialInteraction.urls')),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
