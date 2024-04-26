from django.contrib import admin

from django.contrib import admin
from .models import Pet, PetProfile, PetTransferRequest

admin.site.register(Pet)
admin.site.register(PetProfile)
admin.site.register(PetTransferRequest)