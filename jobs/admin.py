from django.contrib import admin
from django.http import HttpResponse
from django.utils import timezone
import csv
from .models import Job, JobApplication, EmailCommunication, SavedCandidateSearch, SearchNotification, JobRecommendation


def export_jobs_to_csv(modeladmin, request, queryset):
    """Export selected jobs to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="jobs_export_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Job ID', 'Title', 'Location', 'Remote', 'Visa Sponsorship', 
        'Salary Min', 'Salary Max', 'Skills Required', 'Posted By', 
        'Is Active', 'Created At', 'Updated At', 'Total Applications'
    ])
    
    for job in queryset:
        writer.writerow([
            job.id,
            job.title,
            job.location,
            'Yes' if job.is_remote else 'No',
            'Yes' if job.visa_sponsorship else 'No',
            job.salary_min or 'N/A',
            job.salary_max or 'N/A',
            job.skills,
            job.posted_by.get_full_name() if job.posted_by else 'N/A',
            'Active' if job.is_active else 'Inactive',
            job.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            job.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            job.applications.count()
        ])
    
    return response

export_jobs_to_csv.short_description = "Export selected jobs to CSV"


def export_job_applications_to_csv(modeladmin, request, queryset):
    """Export selected job applications to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="job_applications_export_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Application ID', 'Job Title', 'Job Location', 'Applicant Name', 
        'Applicant Email', 'Applied At', 'Current Status', 'Status Display',
        'Pipeline Stage', 'Last Updated', 'Tailored Note Preview', 
        'Days Since Application'
    ])
    
    for application in queryset:
        # Calculate days since application
        days_since = (timezone.now() - application.applied_at).days
        
        # Get pipeline stage if exists
        pipeline_stage = 'N/A'
        if hasattr(application, 'pipeline_card') and application.pipeline_card:
            pipeline_stage = application.pipeline_card.stage.get_name_display()
        
        # Get tailored note preview (first 100 chars)
        note_preview = application.tailored_note[:100] + '...' if len(application.tailored_note) > 100 else application.tailored_note
        
        writer.writerow([
            application.id,
            application.job.title,
            application.job.location,
            application.applicant.get_full_name(),
            application.applicant.email,
            application.applied_at.strftime('%Y-%m-%d %H:%M:%S'),
            application.status,
            application.status_display,
            pipeline_stage,
            application.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            note_preview,
            days_since
        ])
    
    return response

export_job_applications_to_csv.short_description = "Export selected applications to CSV"


def export_email_communications_to_csv(modeladmin, request, queryset):
    """Export selected email communications to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="email_communications_export_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Email ID', 'Job Application', 'Sender', 'Recipient Email', 
        'Subject', 'Message Preview', 'Sent At', 'Is Read', 'Read At',
        'Days Since Sent'
    ])
    
    for email in queryset:
        # Calculate days since sent
        days_since = (timezone.now() - email.sent_at).days
        
        # Get job application info
        job_app_info = 'N/A'
        if email.job_application:
            job_app_info = f"{email.job_application.applicant.get_full_name()} - {email.job_application.job.title}"
        
        # Get message preview (first 150 chars)
        message_preview = email.message[:150] + '...' if len(email.message) > 150 else email.message
        
        writer.writerow([
            email.id,
            job_app_info,
            email.sender.get_full_name(),
            email.recipient_email,
            email.subject,
            message_preview,
            email.sent_at.strftime('%Y-%m-%d %H:%M:%S'),
            'Yes' if email.is_read else 'No',
            email.read_at.strftime('%Y-%m-%d %H:%M:%S') if email.read_at else 'N/A',
            days_since
        ])
    
    return response

export_email_communications_to_csv.short_description = "Export selected emails to CSV"


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("title", "location", "is_remote", "visa_sponsorship", "posted_by", "is_active", "created_at", "application_count")
    list_filter = ("is_remote", "visa_sponsorship", "is_active", "location", "created_at")
    search_fields = ("title", "description", "skills", "location")
    ordering = ("-created_at",)
    actions = [export_jobs_to_csv]
    
    def application_count(self, obj):
        return obj.applications.count()
    application_count.short_description = "Applications"


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ("applicant_name", "job_title", "applied_at", "status", "pipeline_stage", "days_since_application")
    list_filter = ("status", "applied_at", "job")
    search_fields = ("applicant__first_name", "applicant__last_name", "applicant__email", "job__title")
    ordering = ("-applied_at",)
    readonly_fields = ("applied_at", "updated_at")
    actions = [export_job_applications_to_csv]
    
    fieldsets = (
        ('Application Details', {
            'fields': ('job', 'applicant', 'status')
        }),
        ('Applicant Note', {
            'fields': ('tailored_note',)
        }),
        ('Pipeline', {
            'fields': ('kanban_card',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('applied_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def applicant_name(self, obj):
        return obj.applicant.get_full_name()
    applicant_name.short_description = "Applicant"
    
    def job_title(self, obj):
        return obj.job.title
    job_title.short_description = "Job"
    
    def pipeline_stage(self, obj):
        if hasattr(obj, 'pipeline_card') and obj.pipeline_card:
            return obj.pipeline_card.stage.get_name_display()
        return 'N/A'
    pipeline_stage.short_description = "Pipeline Stage"
    
    def days_since_application(self, obj):
        days = (timezone.now() - obj.applied_at).days
        return f"{days} days"
    days_since_application.short_description = "Days Since Applied"


@admin.register(EmailCommunication)
class EmailCommunicationAdmin(admin.ModelAdmin):
    list_display = ("subject", "sender", "recipient_email", "sent_at", "is_read", "related_job")
    list_filter = ("is_read", "sent_at", "sender")
    search_fields = ("subject", "recipient_email", "sender__first_name", "sender__last_name", "message")
    ordering = ("-sent_at",)
    readonly_fields = ("sent_at", "read_at")
    actions = [export_email_communications_to_csv]
    
    fieldsets = (
        ('Email Details', {
            'fields': ('sender', 'recipient_email', 'subject')
        }),
        ('Message', {
            'fields': ('message',)
        }),
        ('Related Application', {
            'fields': ('job_application',),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_read', 'read_at')
        }),
        ('Timestamps', {
            'fields': ('sent_at',),
            'classes': ('collapse',)
        }),
    )
    
    def related_job(self, obj):
        if obj.job_application:
            return obj.job_application.job.title
        return 'N/A'
    related_job.short_description = "Related Job"


@admin.register(SavedCandidateSearch)
class SavedCandidateSearchAdmin(admin.ModelAdmin):
    list_display = ("name", "recruiter", "notify_on_new_matches", "notification_frequency", "created_at", "last_checked_at", "notification_count")
    list_filter = ("notify_on_new_matches", "notification_frequency", "created_at")
    search_fields = ("name", "search_query", "skills", "location", "recruiter__username", "recruiter__email")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at", "last_checked_at")
    
    def notification_count(self, obj):
        return obj.notifications.count()
    notification_count.short_description = "Notifications"


@admin.register(SearchNotification)
class SearchNotificationAdmin(admin.ModelAdmin):
    list_display = ("saved_search", "matched_profile", "is_read", "created_at")
    list_filter = ("is_read", "created_at", "saved_search")
    search_fields = ("saved_search__name", "matched_profile__headline", "matched_profile__user__username")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "read_at")


@admin.register(JobRecommendation)
class JobRecommendationAdmin(admin.ModelAdmin):
    list_display = ("job", "candidate_profile", "match_score", "is_viewed", "is_contacted", "created_at")
    list_filter = ("is_viewed", "is_contacted", "created_at", "job")
    search_fields = ("job__title", "candidate_profile__headline", "candidate_profile__user__username")
    ordering = ("-match_score", "-created_at")
    readonly_fields = ("created_at", "updated_at")
