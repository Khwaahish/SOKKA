from django import forms
from .models import Job, JobApplication


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
