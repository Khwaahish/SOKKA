from django import forms
from .models import Job


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
