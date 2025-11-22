from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from django.utils import timezone
from django.db.models import Q
from .models import JobApplication, SavedCandidateSearch, SearchNotification
from profiles.models import Profile, ProfileSkill
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


@receiver(post_save, sender=Profile)
def check_saved_searches_for_matches(sender, instance, created, **kwargs):
    """Check if a new or updated profile matches any saved searches"""
    # Only check if profile is public and belongs to a job seeker
    try:
        if instance.user and instance.user.user_profile.user_type != 'job_seeker':
            return
    except:
        return
    
    # Get all active saved searches with notifications enabled
    saved_searches = SavedCandidateSearch.objects.filter(
        notify_on_new_matches=True
    )
    
    for saved_search in saved_searches:
        # Check if this profile matches the search criteria
        if profile_matches_search(instance, saved_search):
            # Check if notification already exists
            if not SearchNotification.objects.filter(
                saved_search=saved_search,
                matched_profile=instance
            ).exists():
                # Create notification
                SearchNotification.objects.create(
                    saved_search=saved_search,
                    matched_profile=instance
                )
                
                # Update last_checked_at
                saved_search.last_checked_at = timezone.now()
                saved_search.save(update_fields=['last_checked_at'])


def profile_matches_search(profile, saved_search):
    """Check if a profile matches a saved search criteria"""
    criteria = saved_search.get_search_criteria_dict()
    
    # Check search query
    if criteria.get('search_query'):
        query = criteria['search_query'].lower()
        matches_query = (
            query in profile.headline.lower() or
            query in (profile.bio or '').lower() or
            query in (profile.location or '').lower() or
            (profile.user and query in profile.user.get_full_name().lower()) or
            query in (profile.first_name or '').lower() or
            query in (profile.last_name or '').lower()
        )
        if not matches_query:
            # Check skills
            profile_skills = [ps.skill.name.lower() for ps in ProfileSkill.objects.filter(profile=profile)]
            matches_query = any(query in skill for skill in profile_skills)
        if not matches_query:
            return False
    
    # Check skills
    if criteria.get('skills'):
        profile_skills = [ps.skill.name.lower() for ps in ProfileSkill.objects.filter(profile=profile)]
        required_skills = [s.lower() for s in criteria['skills']]
        matches_skills = any(
            any(req_skill in prof_skill or prof_skill in req_skill for prof_skill in profile_skills)
            for req_skill in required_skills
        )
        if not matches_skills:
            return False
    
    # Check location
    if criteria.get('location'):
        if not profile.location or criteria['location'].lower() not in profile.location.lower():
            return False
    
    # Check minimum years of experience (simplified)
    if criteria.get('min_years_experience'):
        if not profile.work_experiences.exists():
            return False
    
    return True