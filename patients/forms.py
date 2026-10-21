from django import forms
from .models import Patient, Visit

# Add the validate_file function directly in forms.py
def validate_file(file):
    MAX_FILE_SIZE = 25 * 1024 * 1024  # 25MB
    if file.size > MAX_FILE_SIZE:
        raise forms.ValidationError(f"File too large. Maximum size is {MAX_FILE_SIZE/1024/1024}MB")

class PatientForm(forms.ModelForm):
    diagnosis = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)
    treatment = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)
    medication = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)
    notes = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)

    class Meta:
        model = Patient
        fields = ['name', 'age', 'gender', 'phone', 'email', 'date_of_diagnosis', 
                 'diagnosis', 'treatment', 'medication', 'notes']
        widgets = {
            'date_of_diagnosis': forms.DateInput(attrs={'type': 'date'}),
        }

class VisitForm(forms.ModelForm):
    class Meta:
        model = Visit
        fields = ['date', 'diagnosis', 'treatment', 'medication', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'diagnosis': forms.Textarea(attrs={'rows': 3}),
            'treatment': forms.Textarea(attrs={'rows': 3}),
            'medication': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = []
            for file in data:
                try:
                    result.append(single_file_clean(file, initial))
                except forms.ValidationError as e:
                    raise forms.ValidationError([e])
            return result
        return [single_file_clean(data, initial)]

class DocumentForm(forms.Form):
    diagnosis_file = forms.FileField(
        required=False,
        label='Add Diagnosis Document'
    )
    treatment_file = forms.FileField(
        required=False,
        label='Add Treatment Document'
    )
    medication_file = forms.FileField(
        required=False,
        label='Add Medication Document'
    )
    other_file = forms.FileField(
        required=False,
        label='Add Other Document'
    )