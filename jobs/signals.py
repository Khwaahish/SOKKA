from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from .models import JobApplication
from kanban.models import KanbanBoard, ProfileCard, PipelineStage

@receiver(post_save, sender=JobApplication)
def create_kanban_card(sender, instance, created, **kwargs):
    """Create a Kanban card when a new job application is submitted"""
    if created:
        with transaction.atomic():
            # Get or create the recruiter's Kanban board
            board, _ = KanbanBoard.objects.get_or_create(
                recruiter=instance.job.posted_by,
                defaults={'name': 'Hiring Pipeline'}
            )
            
            # Get the initial stage (profile_interest)
            initial_stage = PipelineStage.objects.get(name='profile_interest')
            
            # Create the Kanban card specifically for this application
            profile = instance.applicant.profile
            
            # Create new card and link it to this specific application
            ProfileCard.objects.create(
                board=board,
                profile=profile,
                job_application=instance,  # Link directly to the application
                stage=initial_stage,
                notes=f"Applied for: {instance.job.title}\nApplication Date: {instance.applied_at}"
            )