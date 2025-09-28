from django.contrib import admin
from .models import Job


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("title", "location", "is_remote", "visa_sponsorship", "posted_by", "is_active", "created_at")
    list_filter = ("is_remote", "visa_sponsorship", "is_active", "location")
    search_fields = ("title", "description", "skills", "location")
    ordering = ("-created_at",)
