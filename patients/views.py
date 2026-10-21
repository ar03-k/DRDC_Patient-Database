from django.shortcuts import render, redirect, get_object_or_404
from .models import Patient, PatientDocument, Visit
from .forms import PatientForm, DocumentForm, VisitForm
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError

MAX_FILE_SIZE = 25 * 1024 * 1024  # 25MB

def validate_file(file):
    if file.size > MAX_FILE_SIZE:
        raise ValidationError(f"File too large. Maximum size is {MAX_FILE_SIZE/1024/1024}MB")

def home(request):
    return render(request, 'patients/home.html')

@login_required
def add_patient(request):
    if request.method == 'POST':
        form = PatientForm(request.POST)
        document_form = DocumentForm(request.POST, request.FILES)
        
        if form.is_valid() and document_form.is_valid():
            patient = form.save()
            
            categories = {
                'diagnosis_files': 'diagnosis',
                'treatment_files': 'treatment',
                'medication_files': 'medication',
                'other_files': 'other'
            }
            
            for field_name, category in categories.items():
                files = request.FILES.getlist(field_name)
                for file in files:
                    try:
                        validate_file(file)
                        PatientDocument.objects.create(
                            patient=patient,
                            file=file,
                            category=category
                        )
                    except ValidationError as e:
                        messages.error(request, str(e))
            
            request.session['last_patient_id'] = patient.pk
            messages.success(request, 'Patient added successfully!')
            return redirect('addpatient_success')
    else:
        form = PatientForm()
        document_form = DocumentForm()
    
    return render(request, 'patients/add_patient.html', {
        'form': form,
        'document_form': document_form
    })


@login_required
def add_visit(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        form = VisitForm(request.POST)
        document_form = DocumentForm(request.POST, request.FILES)
        
        if form.is_valid() and document_form.is_valid():
            next_visit_number = patient.visit_set.count() + 2
            visit = form.save(commit=False)
            visit.patient = patient
            visit.visit_number = next_visit_number
            visit.save()
            
            # Handle file uploads
            categories = {
                'diagnosis_files': 'diagnosis',
                'treatment_files': 'treatment',
                'medication_files': 'medication', 
                'other_files': 'other'
            }
            
            for field_name, category in categories.items():
                files = request.FILES.getlist(field_name)
                for file in files:
                    try:
                        validate_file(file)
                        PatientDocument.objects.create(
                            patient=patient,
                            file=file,
                            category=category,
                            visit=visit
                        )
                    except ValidationError as e:
                        messages.error(request, str(e))
            
            messages.success(request, f'Visit {next_visit_number} added successfully!')
            return redirect('patient_detail', pk=patient.pk)  # This redirects to patient detail
    else:
        form = VisitForm()
        document_form = DocumentForm()
    
    return render(request, 'patients/add_visit.html', {
        'form': form,
        'document_form': document_form,
        'patient': patient
    })

@login_required
def addpatient_success(request):
    return render(request, 'patients/addpatient_success.html', {
        'last_patient_id': request.session.get('last_patient_id')
    })

@login_required
def patient_detail(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    visits = patient.visit_set.all().order_by('visit_number')
    documents = patient.patientdocument_set.all()
    
    if request.method == 'POST':
        visit_form = VisitForm(request.POST)
        if visit_form.is_valid():
            next_visit_number = patient.visit_set.count() + 1
            visit = visit_form.save(commit=False)
            visit.patient = patient
            visit.visit_number = next_visit_number
            visit.save()
            messages.success(request, f'Visit {next_visit_number} added successfully!')
            return redirect('patient_detail', pk=patient.pk)
    else:
        visit_form = VisitForm()
    
    context = {
        'patient': patient,
        'visits': visits,
        'documents': documents,
        'visit_form': visit_form,
    }
    return render(request, 'patients/patient_detail.html', context)

@login_required
def edit_patient(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        form = PatientForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            messages.success(request, 'Patient updated successfully!')
            return redirect('patient_detail', pk=patient.pk)
    else:
        form = PatientForm(instance=patient)
    
    return render(request, 'patients/edit_patient.html', {
        'form': form,
        'patient': patient
    })

@login_required
def view_patients(request):
    patients = Patient.objects.all().order_by('-created_at')
    query = request.GET.get('q')
    
    if query:
        patients = patients.filter(
            Q(name__icontains=query) |
            Q(phone__icontains=query) |
            Q(email__icontains=query)
        )
    
    return render(request, 'patients/view_patients.html', {'patients': patients})

@login_required
def delete_patient(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        patient.delete()
        return redirect('view_patients')
    return render(request, 'patients/delete_patient.html', {'patient': patient})