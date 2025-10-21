from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, ProfileSkill, Education, WorkExperience, Link, Skill, UserProfile


class CustomUserCreationForm(UserCreationForm):
    """Custom signup form that includes user type selection"""
    email = forms.EmailField(required=True, help_text="Required. Enter a valid email address.")
    first_name = forms.CharField(max_length=30, required=True, help_text="Required.")
    last_name = forms.CharField(max_length=30, required=True, help_text="Required.")
    user_type = forms.ChoiceField(
        choices=UserProfile.USER_TYPE_CHOICES,
        required=False,  # Made optional since we set it programmatically in views
        widget=forms.RadioSelect,
        label="I am a",
        help_text="Select your role on the platform"
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            # Update the UserProfile with the selected user_type if provided
            if self.cleaned_data.get('user_type'):
                user_profile = user.user_profile
                user_profile.user_type = self.cleaned_data['user_type']
                user_profile.save()
        
        return user


class ProfileForm(forms.ModelForm):
    """Form for creating and editing user profiles"""
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    
    class Meta:
        model = Profile
        fields = ['headline', 'bio', 'location', 'phone', 'profile_picture']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
            'headline': forms.TextInput(attrs={'placeholder': 'e.g., Software Engineer, Marketing Manager'}),
            'location': forms.TextInput(attrs={'placeholder': 'e.g., San Francisco, CA'}),
            'phone': forms.TextInput(attrs={'placeholder': 'e.g., +1 (555) 123-4567'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.user:
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name
            self.fields['email'].initial = self.user.email
        elif self.instance and self.instance.pk:
            # For anonymous profiles, populate from instance
            self.fields['first_name'].initial = self.instance.first_name
            self.fields['last_name'].initial = self.instance.last_name
            self.fields['email'].initial = self.instance.email
    
    def save(self, commit=True):
        profile = super().save(commit=False)
        if self.user:
            profile.user = self.user
            if commit:
                # Update user information
                self.user.first_name = self.cleaned_data['first_name']
                self.user.last_name = self.cleaned_data['last_name']
                self.user.email = self.cleaned_data['email']
                self.user.save()
                profile.save()
        else:
            # For anonymous profiles, save to profile fields
            profile.first_name = self.cleaned_data['first_name']
            profile.last_name = self.cleaned_data['last_name']
            profile.email = self.cleaned_data['email']
            if commit:
                profile.save()
        return profile


class ProfileSkillForm(forms.ModelForm):
    """Form for adding skills to a profile"""
    skill_name = forms.CharField(max_length=100, required=True, 
                                widget=forms.TextInput(attrs={'placeholder': 'e.g., Python, JavaScript, Marketing'}))
    
    class Meta:
        model = ProfileSkill
        fields = ['proficiency_level']
        widgets = {
            'proficiency_level': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def save(self, commit=True):
        profile_skill = super().save(commit=False)
        skill_name = self.cleaned_data['skill_name']
        
        # Get or create the skill
        skill, created = Skill.objects.get_or_create(name=skill_name.strip())
        profile_skill.skill = skill
        
        if commit:
            profile_skill.save()
        return profile_skill


class EducationForm(forms.ModelForm):
    """Form for adding education to a profile"""
    
    class Meta:
        model = Education
        fields = ['institution', 'degree', 'field_of_study', 'start_date', 'end_date', 'is_current', 'gpa', 'description']
        widgets = {
            'institution': forms.TextInput(attrs={'placeholder': 'e.g., University of California'}),
            'degree': forms.TextInput(attrs={'placeholder': 'e.g., Bachelor of Science'}),
            'field_of_study': forms.TextInput(attrs={'placeholder': 'e.g., Computer Science'}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'gpa': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'max': '4.0'}),
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Describe your academic achievements, coursework, etc.'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['end_date'].required = False
        self.fields['gpa'].required = False
        self.fields['field_of_study'].required = False
        self.fields['description'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        is_current = cleaned_data.get('is_current')
        end_date = cleaned_data.get('end_date')
        
        if is_current and end_date:
            raise forms.ValidationError("Cannot have an end date if currently studying.")
        
        return cleaned_data


class WorkExperienceForm(forms.ModelForm):
    """Form for adding work experience to a profile"""
    
    class Meta:
        model = WorkExperience
        fields = ['company', 'position', 'start_date', 'end_date', 'is_current', 'location', 'description']
        widgets = {
            'company': forms.TextInput(attrs={'placeholder': 'e.g., Google, Microsoft'}),
            'position': forms.TextInput(attrs={'placeholder': 'e.g., Software Engineer, Marketing Manager'}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'location': forms.TextInput(attrs={'placeholder': 'e.g., San Francisco, CA'}),
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe your responsibilities, achievements, etc.'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['end_date'].required = False
        self.fields['location'].required = False
        self.fields['description'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        is_current = cleaned_data.get('is_current')
        end_date = cleaned_data.get('end_date')
        start_date = cleaned_data.get('start_date')
        
        if is_current and end_date:
            raise forms.ValidationError("Cannot have an end date if currently working.")
        
        if end_date and start_date and end_date < start_date:
            raise forms.ValidationError("End date cannot be before start date.")
        
        return cleaned_data


class LinkForm(forms.ModelForm):
    """Form for adding links to a profile"""
    
    class Meta:
        model = Link
        fields = ['link_type', 'url', 'title']
        widgets = {
            'url': forms.URLInput(attrs={'placeholder': 'https://example.com'}),
            'title': forms.TextInput(attrs={'placeholder': 'Optional: Custom title for the link'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].required = False


class SkillSearchForm(forms.Form):
    """Form for searching skills when adding them to a profile"""
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search for skills...',
            'class': 'form-control'
        })
    )

