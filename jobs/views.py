from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Job
from .forms import JobForm


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
    return render(request, "jobs/job_detail.html", {"job": job})


@login_required
def job_create(request):
    if request.method == "POST":
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.posted_by = request.user
            job.save()
            return redirect("jobs:detail", pk=job.pk)
    else:
        form = JobForm()
    return render(request, "jobs/job_form.html", {"form": form})


@login_required
def job_edit(request, pk):
    job = get_object_or_404(Job, pk=pk)
    if request.user != job.posted_by and not request.user.is_staff:
        return redirect("jobs:detail", pk=job.pk)
    if request.method == "POST":
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            return redirect("jobs:detail", pk=job.pk)
    else:
        form = JobForm(instance=job)
    return render(request, "jobs/job_form.html", {"form": form, "job": job})
