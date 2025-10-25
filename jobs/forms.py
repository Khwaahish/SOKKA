from django import forms
from .models import Job, JobApplication, EmailCommunication


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = [
            "title",
            "description",
            "skills",
            "location",
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
