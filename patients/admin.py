from django.contrib import admin
from .models import Patient, PatientDocument

admin.site.register(Patient)
admin.site.register(PatientDocument)