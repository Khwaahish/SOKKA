from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.db import transaction
from .models import Job, JobApplication
from .forms import JobForm, JobApplicationForm
from profiles.views import recruiter_required, job_seeker_required
from kanban.models import KanbanBoard, PipelineStage, ProfileCard


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

    context = {"jobs": qs}
    return render(request, "jobs/job_list.html", context)


def job_detail(request, pk):
    job = get_object_or_404(Job, pk=pk)
    has_applied = False
    application = None
    
    # If user is a recruiter, redirect to applicants view
    if request.user.is_authenticated and request.user.user_profile.is_recruiter:
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
