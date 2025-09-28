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