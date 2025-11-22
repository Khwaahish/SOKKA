from django import forms
from .models import Job, JobApplication, EmailCommunication, SavedCandidateSearch


class JobForm(forms.ModelForm):
    latitude = forms.DecimalField(
        max_digits=10,
        decimal_places=7,
        required=False,
        widget=forms.HiddenInput()
    )
    longitude = forms.DecimalField(
        max_digits=10,
        decimal_places=7,
        required=False,
        widget=forms.HiddenInput()
    )
    
    class Meta:
        model = Job
        fields = [
            "title",
            "description",
            "skills",
            "location",
            "latitude",
            "longitude",
            "salary_min",
            "salary_max",
            "is_remote",
            "visa_sponsorship",
            "is_active",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 6}),
            "skills": forms.TextInput(attrs={"placeholder": "e.g. Python, Django, React"}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        is_remote = cleaned_data.get('is_remote', False)
        latitude = cleaned_data.get('latitude')
        longitude = cleaned_data.get('longitude')
        
        # If job is not remote, require location coordinates
        if not is_remote:
            if not latitude or not longitude:
                raise forms.ValidationError(
                    "Please pin the office location on the map. This is required for non-remote jobs."
                )
        
        return cleaned_data
    
    def save(self, commit=True):
        job = super().save(commit=False)
        if commit:
            job.save()
        return job


class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ['tailored_note']
        widgets = {
            'tailored_note': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Write a personalized note explaining why you\'re interested in this position and what makes you a good fit...'
            })
        }


class EmailForm(forms.ModelForm):
    class Meta:
        model = EmailCommunication
        fields = ['subject', 'message']
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter email subject...'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 8,
                'placeholder': 'Write your message to the candidate...'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['subject'].required = True
        self.fields['message'].required = True


class SavedSearchForm(forms.ModelForm):
    class Meta:
        model = SavedCandidateSearch
        fields = ['name', 'search_query', 'skills', 'location', 'min_years_experience', 
                  'education_level', 'notify_on_new_matches', 'notification_frequency']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Senior Python Developers in NYC'
            }),
            'search_query': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'General search terms...'
            }),
            'skills': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Python, Django, React'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., New York, NY'
            }),
            'min_years_experience': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0
            }),
            'education_level': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Bachelor\'s, Master\'s'
            }),
            'notify_on_new_matches': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'notification_frequency': forms.Select(attrs={
                'class': 'form-select'
            })
        }
