from django.db import models
from django.urls import reverse

class PatientDocument(models.Model):
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE)
    visit = models.ForeignKey('Visit', on_delete=models.CASCADE, null=True, blank=True)
    file = models.FileField(upload_to='patient_docs/%Y/%m/%d/')
    category = models.CharField(max_length=20, choices=[
        ('diagnosis', 'Diagnosis'),
        ('treatment', 'Treatment'), 
        ('medication', 'Medication'),
        ('other', 'Other')
    ])
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_category_display()} document for {self.patient.name}"
    
    def file_type(self):
        ext = self.file.name.split('.')[-1].lower()
        if ext in ['jpg', 'jpeg', 'png', 'gif']:
            return 'image'
        elif ext == 'pdf':
            return 'pdf'
        elif ext in ['doc', 'docx']:
            return 'word'
        elif ext in ['xls', 'xlsx']:
            return 'excel'
        else:
            return 'file'

class Visit(models.Model):
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE)
    visit_number = models.PositiveIntegerField()
    date = models.DateField()
    diagnosis = models.TextField(blank=True)
    treatment = models.TextField(blank=True)
    medication = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['visit_number']
        unique_together = ['patient', 'visit_number']

    def __str__(self):
        return f"Visit {self.visit_number} for {self.patient.name}"

class Patient(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    name = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    date_of_diagnosis = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    diagnosis = models.TextField(blank=True, null=True)
    treatment = models.TextField(blank=True, null=True)
    medication = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('patient_detail', kwargs={'pk': self.pk})