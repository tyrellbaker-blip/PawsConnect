from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.gis.admin import GISModelAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(GISModelAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('display_name', 'profile_picture', 'location', 'preferred_language', 'city', 'state')}),
    )
