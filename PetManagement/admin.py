from django.contrib import admin

from django.contrib import admin
from .models import Pet, PetTransferRequest

admin.site.register(Pet)

admin.site.register(PetTransferRequest)