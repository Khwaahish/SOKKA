from django.db import models
from django.conf import settings


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


class JobApplication(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tailored_note = models.TextField(max_length=1000, help_text="Personalized note to the employer")
    applied_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('reviewed', 'Reviewed'),
            ('accepted', 'Accepted'),
            ('rejected', 'Rejected'),
        ],
        default='pending'
    )

    class Meta:
        unique_together = ['job', 'applicant']
        ordering = ['-applied_at']

    def __str__(self):
        return f"{self.applicant.get_full_name()} applied to {self.job.title}"