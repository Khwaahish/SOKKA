from django.db import models
from django.conf import settings
from kanban.models import ProfileCard, PipelineStage
from profiles.models import ProfileSkill


class Job(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    skills = models.CharField(
        max_length=512,
        help_text="Comma-separated list of required skills",
        blank=True,
    )
    location = models.CharField(max_length=255, blank=True)
    salary_min = models.PositiveIntegerField(null=True, blank=True)
    salary_max = models.PositiveIntegerField(null=True, blank=True)
    is_remote = models.BooleanField(default=False)
    visa_sponsorship = models.BooleanField(default=False)
    posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} - {self.location or 'Remote/Unknown'}"
    
    def get_required_skills(self):
        """Get list of required skills from the skills field"""
        if not self.skills:
            return []
        return [skill.strip().lower() for skill in self.skills.split(',') if skill.strip()]
    
    def calculate_skill_match_score(self, user_profile):
        """
        Calculate how well a user's skills match this job's requirements
        Returns a score between 0 and 100
        """
        if not user_profile:
            return 0
            
        required_skills = self.get_required_skills()
        if not required_skills:
            return 0
            
        user_skills = []
        try:
            # Get user's skills from their profile
            profile_skills = ProfileSkill.objects.filter(profile=user_profile)
            user_skills = [ps.skill.name.lower() for ps in profile_skills]
        except:
            pass
            
        if not user_skills:
            return 0
            
        # Calculate matches
        matches = 0
        for required_skill in required_skills:
            for user_skill in user_skills:
                if required_skill in user_skill or user_skill in required_skill:
                    matches += 1
                    break
        
        # Calculate percentage match
        match_percentage = (matches / len(required_skills)) * 100
        return round(match_percentage, 1)


class JobApplication(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tailored_note = models.TextField(max_length=1000, help_text="Personalized note to the employer")
    applied_at = models.DateTimeField(auto_now_add=True)
    kanban_card = models.OneToOneField(
        'kanban.ProfileCard',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='application_link'
    )

    STATUS_APPLIED = 'applied'
    STATUS_REVIEW = 'review'
    STATUS_INTERVIEW = 'interview'
    STATUS_OFFER = 'offer'
    STATUS_CLOSED = 'closed'
    
    STATUS_CHOICES = [
        (STATUS_APPLIED, 'Application Submitted'),
        (STATUS_REVIEW, 'Under Review'),
        (STATUS_INTERVIEW, 'Interview Stage'),
        (STATUS_OFFER, 'Offer Received'),
        (STATUS_CLOSED, 'Application Closed'),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_APPLIED
    )
    updated_at = models.DateTimeField(auto_now=True)

    def update_status_from_stage(self, pipeline_stage):
        """Update status based on the pipeline stage"""
        stage_status_map = {
            'profile_interest': self.STATUS_APPLIED,
            'resume_review': self.STATUS_REVIEW,
            'interview': self.STATUS_INTERVIEW,
            'hired': self.STATUS_OFFER,
            'rejected': self.STATUS_CLOSED,
        }
        new_status = stage_status_map.get(pipeline_stage.name, self.STATUS_APPLIED)
        if self.status != new_status:
            self.status = new_status
            self.save(update_fields=['status', 'updated_at'])

    @property
    def status_display(self):
        """Get a user-friendly status display"""
        status_display_map = {
            'applied': 'Application Submitted',
            'review': 'Under Review',
            'interview': 'Interview Stage',
            'offer': 'Offer Received',
            'closed': 'Application Closed'
        }
        return status_display_map.get(self.status, 'Application Submitted')

    class Meta:
        unique_together = ['job', 'applicant']
        ordering = ['-applied_at']

    def __str__(self):
        return f"{self.applicant.get_full_name()} applied to {self.job.title}"


class EmailCommunication(models.Model):
    """Model to store email communications between recruiters and candidates"""
    job_application = models.ForeignKey(JobApplication, on_delete=models.CASCADE, related_name='emails', null=True, blank=True)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_emails')
    recipient_email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-sent_at']
    
    def __str__(self):
        return f"Email to {self.recipient_email} - {self.subject}"
    
    def mark_as_read(self):
        """Mark the email as read"""
        if not self.is_read:
            from django.utils import timezone
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])