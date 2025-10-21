from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from .models import Job, JobApplication
from .forms import JobForm, JobApplicationForm
from profiles.views import recruiter_required, job_seeker_required


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
    if request.user.is_authenticated:
        has_applied = JobApplication.objects.filter(job=job, applicant=request.user).exists()
    return render(request, "jobs/job_detail.html", {"job": job, "has_applied": has_applied})


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
