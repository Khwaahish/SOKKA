from django.db import models
from django.contrib.auth.models import User
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError


class Profile(models.Model):
    """Main profile model for job seekers"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', null=True, blank=True)
    # Anonymous profile fields
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    # Profile content
    headline = models.CharField(max_length=200, help_text="Professional headline or title")
    bio = models.TextField(max_length=1000, blank=True, help_text="Brief professional summary")
    location = models.CharField(max_length=100, blank=True, help_text="City, State/Country")
    phone = models.CharField(max_length=20, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        if self.user:
            return f"{self.user.get_full_name()} - {self.headline}"
        else:
            return f"{self.first_name} {self.last_name} - {self.headline}"
    
    def get_full_name(self):
        """Get the full name of the profile owner"""
        if self.user:
            return self.user.get_full_name()
        else:
            return f"{self.first_name} {self.last_name}".strip()
    
    def get_email(self):
        """Get the email of the profile owner"""
        if self.user:
            return self.user.email
        else:
            return self.email


class Skill(models.Model):
    """Skills that can be associated with a profile"""
    name = models.CharField(max_length=100, unique=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class ProfileSkill(models.Model):
    """Many-to-many relationship between Profile and Skill with proficiency level"""
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='profile_skills')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    proficiency_level = models.CharField(
        max_length=20,
        choices=[
            ('beginner', 'Beginner'),
            ('intermediate', 'Intermediate'),
            ('advanced', 'Advanced'),
            ('expert', 'Expert'),
        ],
        default='intermediate'
    )
    
    class Meta:
        unique_together = ['profile', 'skill']
    
    def __str__(self):
        return f"{self.profile.user.get_full_name()} - {self.skill.name} ({self.proficiency_level})"


class Education(models.Model):
    """Education history for profiles"""
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='educations')
    institution = models.CharField(max_length=200)
    degree = models.CharField(max_length=100)
    field_of_study = models.CharField(max_length=100, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    gpa = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    description = models.TextField(max_length=500, blank=True)
    is_current = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-end_date', '-start_date']
    
    def clean(self):
        if self.end_date and self.start_date and self.end_date < self.start_date:
            raise ValidationError('End date cannot be before start date.')
        if self.is_current and self.end_date:
            raise ValidationError('Cannot have end date if currently studying.')
    
    def __str__(self):
        return f"{self.degree} in {self.field_of_study} at {self.institution}"


class WorkExperience(models.Model):
    """Work experience history for profiles"""
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='work_experiences')
    company = models.CharField(max_length=200)
    position = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    description = models.TextField(max_length=2000, blank=True)
    location = models.CharField(max_length=100, blank=True)
    
    class Meta:
        ordering = ['-end_date', '-start_date']
    
    def clean(self):
        if self.end_date and self.start_date and self.end_date < self.start_date:
            raise ValidationError('End date cannot be before start date.')
        if self.is_current and self.end_date:
            raise ValidationError('Cannot have end date if currently working.')
    
    def __str__(self):
        return f"{self.position} at {self.company}"


class Link(models.Model):
    """External links (LinkedIn, GitHub, portfolio, etc.)"""
    LINK_TYPES = [
        ('linkedin', 'LinkedIn'),
        ('github', 'GitHub'),
        ('portfolio', 'Portfolio'),
        ('website', 'Website'),
        ('twitter', 'Twitter'),
        ('other', 'Other'),
    ]
    
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='links')
    link_type = models.CharField(max_length=20, choices=LINK_TYPES)
    url = models.URLField()
    title = models.CharField(max_length=100, blank=True)
    
    class Meta:
        ordering = ['link_type', 'title']
    
    def clean(self):
        # Validate URL format
        validator = URLValidator()
        try:
            validator(self.url)
        except ValidationError:
            raise ValidationError('Please enter a valid URL.')
    
    def __str__(self):
        return f"{self.get_link_type_display()}: {self.title or self.url}"