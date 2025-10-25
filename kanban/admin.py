from django.contrib import admin
from django.http import HttpResponse
from django.utils import timezone
import csv
from .models import PipelineStage, KanbanBoard, ProfileCard, ProfileLike


def export_pipeline_stages_to_csv(modeladmin, request, queryset):
    """Export pipeline stages with candidate counts to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="pipeline_stages_export_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Stage Name', 'Display Name', 'Order', 'Color', 'Total Candidates',
        'Average Days in Stage'
    ])
    
    for stage in queryset:
        # Count candidates in this stage
        candidates_count = stage.profile_cards.count()
        
        # Calculate average days in stage
        avg_days = 0
        if candidates_count > 0:
            total_days = 0
            for card in stage.profile_cards.all():
                days = (timezone.now() - card.updated_at).days
                total_days += days
            avg_days = total_days / candidates_count
        
        writer.writerow([
            stage.name,
            stage.get_name_display(),
            stage.order,
            stage.color,
            candidates_count,
            f"{avg_days:.1f}"
        ])
    
    return response

export_pipeline_stages_to_csv.short_description = "Export pipeline stages to CSV"


def export_profile_cards_to_csv(modeladmin, request, queryset):
    """Export profile cards (candidates in pipeline) to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="pipeline_candidates_export_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Candidate Name', 'Candidate Email', 'Job Title', 'Current Stage', 
        'Stage Order', 'Days in Stage', 'Days Since Application', 'Recruiter',
        'Application Status', 'Notes Preview', 'Added At', 'Last Updated'
    ])
    
    for card in queryset:
        # Calculate days in current stage
        days_in_stage = (timezone.now() - card.updated_at).days
        
        # Calculate days since application
        days_since_app = 'N/A'
        application_status = 'N/A'
        job_title = 'N/A'
        
        if card.job_application:
            days_since_app = (timezone.now() - card.job_application.applied_at).days
            application_status = card.job_application.status_display
            job_title = card.job_application.job.title
        
        # Notes preview
        notes_preview = card.notes[:100] + '...' if len(card.notes) > 100 else card.notes
        
        writer.writerow([
            card.profile.get_full_name(),
            card.profile.get_email(),
            job_title,
            card.stage.get_name_display(),
            card.stage.order,
            days_in_stage,
            days_since_app,
            card.board.recruiter.get_full_name(),
            application_status,
            notes_preview,
            card.added_at.strftime('%Y-%m-%d %H:%M:%S'),
            card.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    return response

export_profile_cards_to_csv.short_description = "Export pipeline candidates to CSV"


def export_kanban_boards_to_csv(modeladmin, request, queryset):
    """Export kanban boards summary to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="kanban_boards_export_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Board Name', 'Recruiter', 'Recruiter Email', 'Total Candidates',
        'Candidates in Interview', 'Candidates Hired', 'Candidates Rejected',
        'Created At', 'Last Updated'
    ])
    
    for board in queryset:
        # Count candidates by stage
        total_candidates = board.profile_cards.count()
        interview_count = board.profile_cards.filter(stage__name='interview').count()
        hired_count = board.profile_cards.filter(stage__name='hired').count()
        rejected_count = board.profile_cards.filter(stage__name='rejected').count()
        
        writer.writerow([
            board.name,
            board.recruiter.get_full_name(),
            board.recruiter.email,
            total_candidates,
            interview_count,
            hired_count,
            rejected_count,
            board.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            board.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    return response

export_kanban_boards_to_csv.short_description = "Export kanban boards to CSV"


def export_profile_likes_to_csv(modeladmin, request, queryset):
    """Export profile likes to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="profile_likes_export_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Recruiter', 'Recruiter Email', 'Candidate Name', 'Candidate Email',
        'Candidate Headline', 'Candidate Location', 'Liked At', 'Days Since Liked'
    ])
    
    for like in queryset:
        # Calculate days since liked
        days_since = (timezone.now() - like.liked_at).days
        
        writer.writerow([
            like.recruiter.get_full_name(),
            like.recruiter.email,
            like.profile.get_full_name(),
            like.profile.get_email(),
            like.profile.headline,
            like.profile.location or 'N/A',
            like.liked_at.strftime('%Y-%m-%d %H:%M:%S'),
            days_since
        ])
    
    return response

export_profile_likes_to_csv.short_description = "Export profile likes to CSV"


@admin.register(PipelineStage)
class PipelineStageAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_name_display', 'order', 'color', 'candidate_count']
    list_filter = ['name']
    ordering = ['order']
    actions = [export_pipeline_stages_to_csv]
    
    def candidate_count(self, obj):
        return obj.profile_cards.count()
    candidate_count.short_description = 'Candidates'


@admin.register(KanbanBoard)
class KanbanBoardAdmin(admin.ModelAdmin):
    list_display = ['name', 'recruiter', 'total_candidates', 'created_at', 'updated_at']
    list_filter = ['created_at', 'recruiter']
    search_fields = ['name', 'recruiter__first_name', 'recruiter__last_name', 'recruiter__email']
    readonly_fields = ['created_at', 'updated_at']
    actions = [export_kanban_boards_to_csv]
    
    def total_candidates(self, obj):
        return obj.profile_cards.count()
    total_candidates.short_description = 'Total Candidates'


@admin.register(ProfileCard)
class ProfileCardAdmin(admin.ModelAdmin):
    list_display = ['profile', 'stage', 'board', 'job_title', 'days_in_stage', 'added_at', 'updated_at']
    list_filter = ['stage', 'board', 'added_at']
    search_fields = ['profile__user__first_name', 'profile__user__last_name', 'profile__email', 'notes']
    readonly_fields = ['added_at', 'updated_at']
    ordering = ['stage__order', 'position']
    actions = [export_profile_cards_to_csv]
    
    fieldsets = (
        ('Card Details', {
            'fields': ('board', 'profile', 'job_application', 'stage', 'position')
        }),
        ('Recruiter Notes', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('added_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def job_title(self, obj):
        if obj.job_application:
            return obj.job_application.job.title
        return 'N/A'
    job_title.short_description = 'Job'
    
    def days_in_stage(self, obj):
        days = (timezone.now() - obj.updated_at).days
        return f"{days} days"
    days_in_stage.short_description = 'Days in Stage'


@admin.register(ProfileLike)
class ProfileLikeAdmin(admin.ModelAdmin):
    list_display = ['recruiter', 'profile', 'liked_at', 'days_since_liked']
    list_filter = ['liked_at', 'recruiter']
    search_fields = ['recruiter__first_name', 'recruiter__last_name', 'profile__user__first_name', 'profile__user__last_name']
    readonly_fields = ['liked_at']
    actions = [export_profile_likes_to_csv]
    
    def days_since_liked(self, obj):
        days = (timezone.now() - obj.liked_at).days
        return f"{days} days"
    days_since_liked.short_description = 'Days Since Liked'
