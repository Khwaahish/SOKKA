from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.db.models import Case, When
import json

from profiles.models import Profile
from profiles.views import recruiter_required
from .models import KanbanBoard, ProfileCard, PipelineStage, ProfileLike


def _ensure_pipeline_stages():
    """Ensure all required pipeline stages exist, create them if they don't"""
    stages_config = [
        ('profile_interest', 0, '#667eea'),
        ('resume_review', 1, '#43e97b'),
        ('interview', 2, '#4facfe'),
        ('hired', 3, '#38b2ac'),
        ('rejected', 4, '#fa709a'),
    ]
    
    for name, order, color in stages_config:
        PipelineStage.objects.get_or_create(
            name=name,
            defaults={'order': order, 'color': color}
        )


@login_required
@recruiter_required
def kanban_board(request):
    """Display the kanban board for the current user"""
    # Ensure pipeline stages exist (create if they don't)
    _ensure_pipeline_stages()
    
    # Get or create the user's kanban board
    board, created = KanbanBoard.objects.get_or_create(recruiter=request.user)
    
    # Get pipeline stages in the correct order
    stages = PipelineStage.objects.filter(
        name__in=['profile_interest', 'resume_review', 'interview', 'hired', 'rejected']
    ).order_by(
        Case(
            When(name='profile_interest', then=0),
            When(name='resume_review', then=1),
            When(name='interview', then=2),
            When(name='hired', then=3),
            When(name='rejected', then=4),
        )
    )
    
    # Get all profile cards for this board, organized by stage
    cards_by_stage = {}
    for stage in stages:
        cards_by_stage[stage.id] = ProfileCard.objects.filter(
            board=board, 
            stage=stage
        ).select_related('profile')
    
    context = {
        'board': board,
        'stages': stages,
        'cards_by_stage': cards_by_stage,
    }
    return render(request, 'kanban/kanban_board.html', context)


@login_required
@recruiter_required
def like_profile(request, profile_id):
    """Like a profile and add it to the kanban board (Recruiters only)"""
    # Ensure pipeline stages exist
    _ensure_pipeline_stages()
    
    profile = get_object_or_404(Profile, id=profile_id)
    
    # Check if already liked
    like, created = ProfileLike.objects.get_or_create(
        recruiter=request.user,
        profile=profile
    )
    
    if created:
        # Get or create the user's kanban board
        board, _ = KanbanBoard.objects.get_or_create(recruiter=request.user)
        
        # Get the first stage (Profile Interest)
        first_stage = PipelineStage.objects.filter(name='profile_interest').first()
        
        if first_stage:
            # Create a profile card in the first stage
            ProfileCard.objects.create(
                board=board,
                profile=profile,
                stage=first_stage,
                position=0
            )
        
        return JsonResponse({'status': 'liked', 'message': 'Profile added to your pipeline!'})
    else:
        return JsonResponse({'status': 'already_liked', 'message': 'Profile already in your pipeline!'})


@login_required
@recruiter_required
def unlike_profile(request, profile_id):
    """Remove a profile from the kanban board (Recruiters only)"""
    profile = get_object_or_404(Profile, id=profile_id)
    
    try:
        like = ProfileLike.objects.get(recruiter=request.user, profile=profile)
        like.delete()
        
        # Also remove from kanban board
        board = KanbanBoard.objects.get(recruiter=request.user)
        ProfileCard.objects.filter(board=board, profile=profile).delete()
        
        return JsonResponse({'status': 'unliked', 'message': 'Profile removed from your pipeline!'})
    except ProfileLike.DoesNotExist:
        return JsonResponse({'status': 'not_liked', 'message': 'Profile not in your pipeline!'})


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
@method_decorator(recruiter_required, name='dispatch')
class MoveCardView(View):
    """Handle drag and drop of profile cards between stages (Recruiters only)"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            card_id = data.get('card_id')
            new_stage_id = data.get('new_stage_id')
            new_position = data.get('new_position', 0)
            
            # Get the card and new stage
            card = get_object_or_404(ProfileCard, id=card_id, board__recruiter=request.user)
            new_stage = get_object_or_404(PipelineStage, id=new_stage_id)
            
            # Move the card
            card.move_to_stage(new_stage, new_position)
            
            return JsonResponse({
                'status': 'success',
                'message': f'Card moved to {new_stage.get_name_display()}'
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)


@login_required
@recruiter_required
def update_card_notes(request, card_id):
    """Update notes for a profile card (Recruiters only)"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            notes = data.get('notes', '')
            
            card = get_object_or_404(ProfileCard, id=card_id, board__recruiter=request.user)
            card.notes = notes
            card.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Notes updated successfully'
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


@login_required
@recruiter_required
def get_liked_profiles(request):
    """Get all profiles liked by the current user (Recruiters only)"""
    liked_profiles = ProfileLike.objects.filter(recruiter=request.user).values_list('profile_id', flat=True)
    return JsonResponse({'liked_profiles': list(liked_profiles)})