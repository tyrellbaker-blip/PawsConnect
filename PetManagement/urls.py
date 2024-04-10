from django.urls import path

from UserManagement import views

app_name = 'PetManagement'

urlpatterns = [
    # ... other url patterns ...
    path('pet/<slug:slug>/', views.pet_profile, name='pet_profile'),  # Use slug in URL pattern
    # ... other url patterns ...
]