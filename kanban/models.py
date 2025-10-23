from django.db import models
from django.contrib.auth.models import User
from profiles.models import Profile


class PipelineStage(models.Model):
    """Represents the different stages in the hiring pipeline"""
    STAGE_CHOICES = [
        ('profile_interest', 'Profile Interest'),
        ('resume_review', 'Resume Review'),
        ('interview', 'Interview'),
        ('hired', 'Hired'),
        ('rejected', 'Rejected'),
    ]
    
    name = models.CharField(max_length=50, choices=STAGE_CHOICES, unique=True)
    order = models.PositiveIntegerField(default=0)
    color = models.CharField(max_length=7, default='#3498db', help_text='Hex color code for the stage')
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.get_name_display()
    
    def save(self, *args, **kwargs):
        # Auto-assign order based on stage name if not set
        if not self.order:
            order_map = {
                'profile_interest': 0,
                'resume_review': 1,
                'interview': 2,
                'hired': 3,
                'rejected': 4,
            }
            self.order = order_map.get(self.name, 0)
        super().save(*args, **kwargs)


class KanbanBoard(models.Model):
    """Represents a recruiter's kanban board"""
    recruiter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='kanban_boards')
    name = models.CharField(max_length=100, default='My Hiring Pipeline')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.recruiter.get_full_name()}'s {self.name}"


class ProfileCard(models.Model):
    """Represents a profile card in the kanban board for a specific job application"""
    board = models.ForeignKey(KanbanBoard, on_delete=models.CASCADE, related_name='profile_cards')
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='kanban_cards')
    job_application = models.OneToOneField(
        'jobs.JobApplication',
        on_delete=models.CASCADE,
        related_name='pipeline_card',
        null=True  # Allow null temporarily for migration
    )
    stage = models.ForeignKey(PipelineStage, on_delete=models.CASCADE, related_name='profile_cards')
    position = models.PositiveIntegerField(default=0, help_text='Position within the stage')
    notes = models.TextField(blank=True, help_text='Recruiter notes about this candidate')
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['stage__order', 'position']
    
    def __str__(self):
        return f"{self.profile.get_full_name()} in {self.stage.get_name_display()}"
    
    def move_to_stage(self, new_stage, new_position=None):
        """Move this card to a new stage"""
        if new_position is None:
            # Get the next position in the new stage
            last_card = ProfileCard.objects.filter(
                board=self.board, 
                stage=new_stage
            ).order_by('-position').first()
            new_position = (last_card.position + 1) if last_card else 0
        
        old_stage = self.stage
        self.stage = new_stage
        self.position = new_position
        self.save(update_fields=['stage', 'position', 'updated_at'])
        
        # If the stage has changed, trigger status updates for linked applications
        if old_stage != new_stage:
            from jobs.models import JobApplication
            JobApplication.objects.filter(kanban_card=self).update(
                updated_at=models.F('updated_at')  # Force an update to trigger save signals
            )


class ProfileLike(models.Model):
    """Tracks when a recruiter likes a profile"""
    recruiter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='liked_profiles')
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='likes')
    liked_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['recruiter', 'profile']  # A recruiter can only like a profile once
    
    def __str__(self):
        return f"{self.recruiter.get_full_name()} likes {self.profile.get_full_name()}"