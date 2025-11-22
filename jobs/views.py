from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum, F
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.db import transaction, models
from django.core.mail import send_mail
from django.conf import settings
from django.core import serializers
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
import json
import math
from .models import Job, JobApplication, EmailCommunication, SavedCandidateSearch, SearchNotification, JobRecommendation
from .forms import JobForm, JobApplicationForm, EmailForm
from profiles.views import recruiter_required, job_seeker_required
from kanban.models import KanbanBoard, PipelineStage, ProfileCard
from profiles.models import Profile, ProfileSkill, WorkExperience, Education


def calculate_distance_miles(lat1, lon1, lat2, lon2):
    """
    Calculate the distance between two points on Earth using the Haversine formula.
    Returns distance in miles.
    """
    # Convert latitude and longitude from degrees to radians
    lat1_rad = math.radians(float(lat1))
    lon1_rad = math.radians(float(lon1))
    lat2_rad = math.radians(float(lat2))
    lon2_rad = math.radians(float(lon2))
    
    # Haversine formula
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of Earth in miles
    r = 3959.0
    
    return c * r


def job_list(request):
    # Filters: title, skills, location, salary range, is_remote, visa_sponsorship
    qs = Job.objects.filter(is_active=True)
    title = request.GET.get("title")
    skills = request.GET.get("skills")
    location = request.GET.get("location")
    salary_min = request.GET.get("salary_min")
    salary_max = request.GET.get("salary_max")
    is_remote = request.GET.get("is_remote")
    visa = request.GET.get("visa_sponsorship")

    if title:
        qs = qs.filter(title__icontains=title)
    if skills:
        # naive: check if any of comma-separated skills string appears
        for skill in [s.strip() for s in skills.split(",") if s.strip()]:
            qs = qs.filter(skills__icontains=skill)
    if location:
        qs = qs.filter(location__icontains=location)
    if salary_min:
        try:
            smin = int(salary_min)
            qs = qs.filter(salary_max__gte=smin) | qs.filter(salary_min__gte=smin)
        except ValueError:
            pass
    if salary_max:
        try:
            smax = int(salary_max)
            qs = qs.filter(salary_min__lte=smax) | qs.filter(salary_max__lte=smax)
        except ValueError:
            pass
    if is_remote in ["1", "true", "True"]:
        qs = qs.filter(is_remote=True)
    if visa in ["1", "true", "True"]:
        qs = qs.filter(visa_sponsorship=True)

    # Filter by commute radius if user is a job seeker with commute radius set
    user_profile = None
    commute_radius_miles = None
    user_lat = None
    user_lon = None
    
    if request.user.is_authenticated:
        try:
            if request.user.user_profile.is_job_seeker():
                try:
                    user_profile = request.user.profile
                    if user_profile.commute_radius and user_profile.latitude and user_profile.longitude:
                        commute_radius_miles = user_profile.commute_radius
                        user_lat = float(user_profile.latitude)
                        user_lon = float(user_profile.longitude)
                except Profile.DoesNotExist:
                    pass
        except:
            pass
    
    # Filter jobs by commute radius
    if commute_radius_miles and user_lat and user_lon:
        # Get all jobs with coordinates
        jobs_with_coords = []
        jobs_without_coords = []
        
        for job in qs:
            # Always include remote jobs
            if job.is_remote:
                jobs_with_coords.append(job)
            elif job.latitude and job.longitude:
                # Calculate distance
                distance = calculate_distance_miles(
                    user_lat, user_lon,
                    float(job.latitude), float(job.longitude)
                )
                if distance <= commute_radius_miles:
                    jobs_with_coords.append(job)
            else:
                # Jobs without coordinates - include them but they won't be filtered
                jobs_without_coords.append(job)
        
        # Combine jobs within radius and jobs without coordinates
        qs = list(jobs_with_coords) + list(jobs_without_coords)
    else:
        # Convert queryset to list for consistency
        qs = list(qs)

    # Prepare jobs data for map view
    jobs_data = []
    for job in qs:
        job_data = {
            'id': job.id,
            'title': job.title,
            'location': job.location or '',
            'is_remote': job.is_remote,
            'salary_min': job.salary_min,
            'salary_max': job.salary_max,
            'description': job.description[:200] + '...' if len(job.description) > 200 else job.description,
            'url': f'/jobs/{job.id}/',
            'skills': job.skills or '',
        }
        # Add coordinates if available
        if job.latitude and job.longitude:
            job_data['latitude'] = float(job.latitude)
            job_data['longitude'] = float(job.longitude)
        jobs_data.append(job_data)

    context = {
        "jobs": qs,
        "jobs_json": json.dumps(jobs_data),
        "has_commute_radius": commute_radius_miles is not None,
        "commute_radius_miles": commute_radius_miles,
    }
    return render(request, "jobs/job_list.html", context)


def job_detail(request, pk):
    job = get_object_or_404(Job, pk=pk)
    has_applied = False
    application = None
    is_recruiter = False
    
    if request.user.is_authenticated:
        try:
            is_recruiter = request.user.user_profile.is_recruiter()
        except UserProfile.DoesNotExist:
            pass
    
    # If user is a recruiter, redirect to applicants view
    if is_recruiter:
        return redirect('jobs:applicants', pk=pk)
    
    if request.user.is_authenticated:
        try:
            application = JobApplication.objects.select_related(
                'kanban_card', 'kanban_card__stage'
            ).get(job=job, applicant=request.user)
            has_applied = True
        except JobApplication.DoesNotExist:
            pass
    return render(request, "jobs/job_detail.html", {
        "job": job, 
        "has_applied": has_applied,
        "application": application
    })


@login_required
@recruiter_required
def job_applicants(request, pk):
    """View all applicants for a specific job"""
    job = get_object_or_404(Job, pk=pk)
    
    # Check if the recruiter owns this job posting
    if request.user != job.posted_by and not request.user.is_staff:
        messages.error(request, "You can only view applicants for jobs that you posted.")
        return redirect("jobs:detail", pk=pk)
    
    applicants = JobApplication.objects.filter(
        job=pk
    ).select_related(
        'applicant',
        'applicant__profile',
        'pipeline_card',
        'pipeline_card__stage'
    ).order_by('-applied_at')
    
    return render(request, "jobs/job_applicants.html", {
        "job": job,
        "applicants": applicants
    })


@login_required
@recruiter_required
def add_to_kanban(request, application_id):
    """Add a job applicant to the Kanban board"""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)
    
    application = get_object_or_404(JobApplication, id=application_id)
    
    # Check if recruiter owns the job posting
    if request.user != application.job.posted_by and not request.user.is_staff:
        return JsonResponse({
            'status': 'error',
            'message': 'You can only add applicants from your own job postings'
        }, status=403)
    
    # Check if already in Kanban
    if hasattr(application, 'pipeline_card'):
        return JsonResponse({
            'status': 'error',
            'message': 'Applicant is already in your pipeline'
        }, status=400)
    
    try:
        with transaction.atomic():
            # Get or create recruiter's board
            board, _ = KanbanBoard.objects.get_or_create(
                recruiter=request.user,
                defaults={'name': 'Hiring Pipeline'}
            )
            
            # Get initial stage
            initial_stage = PipelineStage.objects.get(name='profile_interest')
            
            # Create card
            ProfileCard.objects.create(
                board=board,
                profile=application.applicant.profile,
                job_application=application,
                stage=initial_stage,
                notes=f"Applied for: {application.job.title}\nApplication Date: {application.applied_at}"
            )
            
        return JsonResponse({
            'status': 'success',
            'message': 'Successfully added to pipeline'
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@login_required
@job_seeker_required
def apply_to_job(request, pk):
    """Job seekers can apply to jobs"""
    job = get_object_or_404(Job, pk=pk)
    
    # Check if user has already applied
    if JobApplication.objects.filter(job=job, applicant=request.user).exists():
        messages.warning(request, "You have already applied to this job.")
        return redirect("jobs:detail", pk=pk)
    
    if request.method == "POST":
        form = JobApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.applicant = request.user
            application.save()
            messages.success(request, "Your application has been submitted successfully!")
            return redirect("jobs:detail", pk=pk)
    else:
        form = JobApplicationForm()
    
    return render(request, "jobs/apply.html", {"form": form, "job": job})


@login_required
@recruiter_required
def job_create(request):
    """Recruiters can post new jobs"""
    if request.method == "POST":
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.posted_by = request.user
            job.save()
            messages.success(request, "Job posted successfully!")
            return redirect("jobs:detail", pk=job.pk)
    else:
        form = JobForm()
    return render(request, "jobs/job_form.html", {"form": form})


@login_required
@recruiter_required
def job_edit(request, pk):
    """Recruiters can edit their posted jobs"""
    job = get_object_or_404(Job, pk=pk)
    if request.user != job.posted_by and not request.user.is_staff:
        messages.error(request, "You can only edit jobs that you posted.")
        return redirect("jobs:detail", pk=job.pk)
    if request.method == "POST":
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, "Job updated successfully!")
            return redirect("jobs:detail", pk=job.pk)
    else:
        form = JobForm(instance=job)
    return render(request, "jobs/job_form.html", {"form": form, "job": job})


@login_required
@job_seeker_required
def my_applications(request):
    """Show all job applications for the current user with their statuses"""
    applications = JobApplication.objects.filter(
        applicant=request.user
    ).select_related(
        'job', 'job__posted_by', 'kanban_card', 'kanban_card__stage'
    ).order_by('-applied_at')
    
    return render(request, "jobs/my_applications.html", {
        "applications": applications
    })


@login_required
@job_seeker_required
def job_recommendations(request):
    """Show job recommendations based on user's skills"""
    try:
        user_profile = request.user.profile
    except Profile.DoesNotExist:
        messages.warning(request, "Please complete your profile to get job recommendations.")
        return redirect('profiles:create_profile')
    
    # Get all active jobs
    jobs = Job.objects.filter(is_active=True)
    
    # Calculate match scores for each job
    job_scores = []
    for job in jobs:
        # Skip jobs the user has already applied to
        if JobApplication.objects.filter(job=job, applicant=request.user).exists():
            continue
            
        score = job.calculate_skill_match_score(user_profile)
        if score > 0:  # Only include jobs with some skill match
            job_scores.append((job, score))
    
    # Sort by match score (highest first)
    job_scores.sort(key=lambda x: x[1], reverse=True)
    
    # Limit to top 20 recommendations
    recommended_jobs = job_scores[:20]
    
    context = {
        'recommended_jobs': recommended_jobs,
        'user_profile': user_profile,
    }
    
    return render(request, "jobs/job_recommendations.html", context)


@login_required
@recruiter_required
def send_email_to_candidate(request, application_id):
    """Send email to a job candidate"""
    application = get_object_or_404(JobApplication, id=application_id)
    
    # Check if recruiter owns the job posting
    if request.user != application.job.posted_by and not request.user.is_staff:
        messages.error(request, "You can only email candidates from your own job postings.")
        return redirect('jobs:applicants', pk=application.job.pk)
    
    # Get candidate's email
    candidate_email = application.applicant.email
    if not candidate_email:
        messages.error(request, "Candidate's email address is not available.")
        return redirect('jobs:applicants', pk=application.job.pk)
    
    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid():
            try:
                # Create email record
                email_comm = form.save(commit=False)
                email_comm.job_application = application
                email_comm.sender = request.user
                email_comm.recipient_email = candidate_email
                email_comm.save()
                
                # Send actual email
                send_mail(
                    subject=email_comm.subject,
                    message=email_comm.message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[candidate_email],
                    fail_silently=False,
                )
                
                messages.success(request, f"Email sent successfully to {candidate_email}")
                return redirect('jobs:applicants', pk=application.job.pk)
                
            except Exception as e:
                messages.error(request, f"Failed to send email: {str(e)}")
    else:
        form = EmailForm()
    
    context = {
        'form': form,
        'application': application,
        'candidate_email': candidate_email,
        'candidate_name': application.applicant.get_full_name(),
        'job_title': application.job.title,
    }
    
    return render(request, 'jobs/send_email.html', context)


@login_required
@recruiter_required
def email_history(request, application_id):
    """View email history for a specific job application"""
    application = get_object_or_404(JobApplication, id=application_id)
    
    # Check if recruiter owns the job posting
    if request.user != application.job.posted_by and not request.user.is_staff:
        messages.error(request, "You can only view email history for your own job postings.")
        return redirect('jobs:applicants', pk=application.job.pk)
    
    emails = EmailCommunication.objects.filter(job_application=application).order_by('-sent_at')
    
    context = {
        'application': application,
        'emails': emails,
        'candidate_name': application.applicant.get_full_name(),
        'job_title': application.job.title,
    }
    
    return render(request, 'jobs/email_history.html', context)


@login_required
@job_seeker_required
def my_emails(request):
    """View emails received by the job seeker"""
    # Get all job applications for this user
    applications = JobApplication.objects.filter(applicant=request.user)
    
    # Get all emails for these applications OR direct emails to this user
    emails = EmailCommunication.objects.filter(
        Q(job_application__in=applications) | 
        Q(recipient_email=request.user.email)
    ).select_related('job_application__job', 'sender').order_by('-sent_at')
    
    context = {
        'emails': emails,
    }
    
    return render(request, 'jobs/my_emails.html', context)


@login_required
@job_seeker_required
def mark_email_read(request, email_id):
    """Mark an email as read"""
    try:
        email = EmailCommunication.objects.get(
            id=email_id,
            recipient_email=request.user.email
        )
        email.mark_as_read()
        return JsonResponse({'status': 'success'})
    except EmailCommunication.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Email not found'}, status=404)


@login_required
@recruiter_required
def send_email_to_candidate_direct(request, profile_id):
    """Send email to any candidate directly (not through job application)"""
    profile = get_object_or_404(Profile, id=profile_id)
    
    # Get candidate's email
    candidate_email = profile.get_email()
    if not candidate_email:
        messages.error(request, "Candidate's email address is not available.")
        return redirect('profiles:profile_list')
    
    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid():
            try:
                # Create a general email record (not tied to specific job application)
                email_comm = form.save(commit=False)
                email_comm.sender = request.user
                email_comm.recipient_email = candidate_email
                email_comm.save()
                
                # Send actual email
                send_mail(
                    subject=email_comm.subject,
                    message=email_comm.message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[candidate_email],
                    fail_silently=False,
                )
                
                messages.success(request, f"Email sent successfully to {candidate_email}")
                return redirect('profiles:profile_list')
                
            except Exception as e:
                messages.error(request, f"Failed to send email: {str(e)}")
    else:
        form = EmailForm()
    
    context = {
        'form': form,
        'profile': profile,
        'candidate_email': candidate_email,
        'candidate_name': profile.get_full_name(),
    }
    
    return render(request, 'jobs/send_email_direct.html', context)


@login_required
@recruiter_required
def matched_candidates(request):
    """Show matched candidates for recruiter's job postings using same logic as job recommendations"""
    # Get all jobs posted by this recruiter
    recruiter_jobs = Job.objects.filter(posted_by=request.user).order_by('-created_at')
    
    # Get all job seekers with profiles
    job_seekers = Profile.objects.filter(user__user_profile__user_type='job_seeker')
    
    # Calculate recommendations for each job using the same logic as job_recommendations
    job_recommendations = []
    for job in recruiter_jobs:
        recommendations = []
        for job_seeker in job_seekers:
            # Skip candidates who have already applied to this job
            if JobApplication.objects.filter(job=job, applicant=job_seeker.user).exists():
                continue
                
            # Calculate skill match score using the same method as job recommendations
            match_score = job.calculate_skill_match_score(job_seeker)
            if match_score > 0:  # Only include candidates with some match
                recommendations.append({
                    'profile': job_seeker,
                    'match_score': match_score,
                    'user': job_seeker.user
                })
        
        # Sort by match score (highest first) - same as job recommendations
        recommendations.sort(key=lambda x: x['match_score'], reverse=True)
        
        # Limit to top 20 recommendations per job (same as job recommendations limit)
        recommendations = recommendations[:20]
        
        # Always include the job, even if no recommendations
        job_recommendations.append({
            'job': job,
            'recommendations': recommendations
        })
    
    context = {
        'job_recommendations': job_recommendations,
        'recruiter_jobs': recruiter_jobs,
    }
    
    return render(request, 'jobs/matched_candidates.html', context)


@login_required
@recruiter_required
def save_candidate_search(request):
    """Save a candidate search with current search criteria"""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if not name:
            messages.error(request, 'Please provide a name for this saved search.')
            return redirect('profiles:profile_list')
        
        # Get search criteria from request
        search_query = request.POST.get('search', '').strip()
        skills = request.POST.get('skills', '').strip()
        location = request.POST.get('location', '').strip()
        min_years_experience = request.POST.get('min_years_experience', '').strip()
        education_level = request.POST.get('education_level', '').strip()
        
        # Create saved search
        saved_search = SavedCandidateSearch.objects.create(
            recruiter=request.user,
            name=name,
            search_query=search_query,
            skills=skills,
            location=location,
            min_years_experience=int(min_years_experience) if min_years_experience else None,
            education_level=education_level,
        )
        
        messages.success(request, f'Saved search "{name}" created successfully!')
        return redirect('jobs:saved_searches')
    
    # If GET request, redirect to profile list with current search params
    return redirect('profiles:profile_list')


@login_required
@recruiter_required
def saved_searches(request):
    """List all saved searches for the current recruiter"""
    saved_searches_list = SavedCandidateSearch.objects.filter(
        recruiter=request.user
    ).order_by('-created_at')
    
    # Get unread notification counts for each search
    for search in saved_searches_list:
        search.unread_count = SearchNotification.objects.filter(
            saved_search=search,
            is_read=False
        ).count()
    
    context = {
        'saved_searches': saved_searches_list,
    }
    
    return render(request, 'jobs/saved_searches.html', context)


@login_required
@recruiter_required
def saved_search_detail(request, search_id):
    """View details of a saved search and run it"""
    saved_search = get_object_or_404(
        SavedCandidateSearch,
        id=search_id,
        recruiter=request.user
    )
    
    # Get search criteria
    criteria = saved_search.get_search_criteria_dict()
    
    # Build query based on criteria
    profiles = Profile.objects.select_related('user').prefetch_related(
        'profile_skills__skill', 'privacy_settings'
    ).filter(
        Q(privacy_settings__isnull=True) |
        Q(privacy_settings__profile_visibility__in=['public', 'selective'])
    )
    
    # Apply search filters
    if criteria.get('search_query'):
        query = criteria['search_query']
        profiles = profiles.filter(
            Q(headline__icontains=query) |
            Q(bio__icontains=query) |
            Q(location__icontains=query) |
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(profile_skills__skill__name__icontains=query)
        ).distinct()
    
    if criteria.get('skills'):
        for skill in criteria['skills']:
            profiles = profiles.filter(profile_skills__skill__name__icontains=skill).distinct()
    
    if criteria.get('location'):
        profiles = profiles.filter(location__icontains=criteria['location'])
    
    if criteria.get('min_years_experience'):
        # Calculate years of experience from work experience
        min_years = criteria['min_years_experience']
        # This is a simplified check - in production, you'd want more sophisticated logic
        # For now, we'll filter profiles that have work experience entries
        # A more sophisticated implementation would calculate actual years
        profiles = profiles.filter(work_experiences__isnull=False).distinct()
    
    # Paginate results
    paginator = Paginator(profiles, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get notifications for this search
    notifications = SearchNotification.objects.filter(
        saved_search=saved_search
    ).select_related('matched_profile').order_by('-created_at')[:10]
    
    context = {
        'saved_search': saved_search,
        'page_obj': page_obj,
        'notifications': notifications,
        'criteria': criteria,
    }
    
    return render(request, 'jobs/saved_search_detail.html', context)


@login_required
@recruiter_required
def delete_saved_search(request, search_id):
    """Delete a saved search"""
    saved_search = get_object_or_404(
        SavedCandidateSearch,
        id=search_id,
        recruiter=request.user
    )
    
    search_name = saved_search.name
    saved_search.delete()
    
    messages.success(request, f'Saved search "{search_name}" deleted successfully!')
    return redirect('jobs:saved_searches')


@login_required
@recruiter_required
def search_notifications(request):
    """View all search notifications for the current recruiter"""
    notifications = SearchNotification.objects.filter(
        saved_search__recruiter=request.user
    ).select_related(
        'saved_search', 'matched_profile'
    ).order_by('-created_at')
    
    # Group by saved search
    notifications_by_search = {}
    for notification in notifications:
        search_name = notification.saved_search.name
        if search_name not in notifications_by_search:
            notifications_by_search[search_name] = []
        notifications_by_search[search_name].append(notification)
    
    context = {
        'notifications': notifications,
        'notifications_by_search': notifications_by_search,
    }
    
    return render(request, 'jobs/search_notifications.html', context)


@login_required
@recruiter_required
@require_POST
def mark_notification_read(request, notification_id):
    """Mark a notification as read"""
    notification = get_object_or_404(
        SearchNotification,
        id=notification_id,
        saved_search__recruiter=request.user
    )
    notification.mark_as_read()
    return JsonResponse({'status': 'success'})


@login_required
@recruiter_required
def candidate_recommendations(request, job_id):
    """Get candidate recommendations for a specific job position"""
    job = get_object_or_404(Job, id=job_id, posted_by=request.user)
    
    # Get or create recommendations
    recommendations = JobRecommendation.objects.filter(job=job).select_related(
        'candidate_profile', 'candidate_profile__user'
    ).order_by('-match_score')
    
    # If no recommendations exist, generate them
    if not recommendations.exists():
        recommendations = generate_job_recommendations(job)
    
    context = {
        'job': job,
        'recommendations': recommendations,
    }
    
    return render(request, 'jobs/candidate_recommendations.html', context)


def generate_job_recommendations(job):
    """Generate candidate recommendations for a job"""
    # Get all job seekers with profiles
    job_seekers = Profile.objects.filter(
        user__user_profile__user_type='job_seeker'
    ).select_related('user').prefetch_related('profile_skills__skill')
    
    recommendations = []
    for job_seeker in job_seekers:
        # Skip candidates who have already applied
        if JobApplication.objects.filter(job=job, applicant=job_seeker.user).exists():
            continue
        
        # Calculate match score
        match_score = job.calculate_skill_match_score(job_seeker)
        
        if match_score > 0:
            # Generate match reason
            match_reason = generate_match_reason(job, job_seeker, match_score)
            
            # Create or update recommendation
            recommendation, created = JobRecommendation.objects.update_or_create(
                job=job,
                candidate_profile=job_seeker,
                defaults={
                    'match_score': match_score,
                    'match_reason': match_reason,
                }
            )
            recommendations.append(recommendation)
    
    # Sort by match score
    recommendations.sort(key=lambda x: x.match_score, reverse=True)
    
    # Limit to top 20
    return recommendations[:20]


def generate_match_reason(job, profile, match_score):
    """Generate a human-readable reason for the match"""
    reasons = []
    
    # Skill match
    required_skills = job.get_required_skills()
    if required_skills:
        profile_skills = [ps.skill.name.lower() for ps in ProfileSkill.objects.filter(profile=profile)]
        matched_skills = [skill for skill in required_skills if any(skill in ps or ps in skill for ps in profile_skills)]
        if matched_skills:
            reasons.append(f"Matches {len(matched_skills)} required skill(s): {', '.join(matched_skills[:3])}")
    
    # Experience match
    if profile.work_experiences.exists():
        reasons.append("Has relevant work experience")
    
    # Education match
    if profile.educations.exists():
        reasons.append("Has relevant education")
    
    if not reasons:
        reasons.append("Potential match based on profile")
    
    return ". ".join(reasons) + f" (Match score: {match_score}%)"