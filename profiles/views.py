from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth import login, logout as auth_logout
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.models import User
from functools import wraps
from .models import Profile, ProfileSkill, Education, WorkExperience, Link, Skill, UserProfile
from .forms import ProfileForm, ProfileSkillForm, EducationForm, WorkExperienceForm, LinkForm, SkillSearchForm, CustomUserCreationForm


# Role-based permission decorators
def recruiter_required(view_func):
    """Decorator to restrict access to recruiters only"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'You must be logged in to access this page.')
            return redirect('login')
        
        try:
            if not request.user.user_profile.is_recruiter():
                messages.error(request, 'You must be a recruiter to access this page.')
                return redirect('profiles:home')
        except UserProfile.DoesNotExist:
            messages.error(request, 'User profile not found.')
            return redirect('profiles:home')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def job_seeker_required(view_func):
    """Decorator to restrict access to job seekers only"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'You must be logged in to access this page.')
            return redirect('login')
        
        try:
            if not request.user.user_profile.is_job_seeker():
                messages.error(request, 'You must be a job seeker to access this page.')
                return redirect('profiles:home')
        except UserProfile.DoesNotExist:
            messages.error(request, 'User profile not found.')
            return redirect('profiles:home')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def get_current_profile(request):
    """Helper function to get the current profile for the user"""
    if request.user.is_authenticated:
        try:
            return request.user.profile
        except Profile.DoesNotExist:
            return None
    else:
        # Anonymous user - get profile from session
        profile_id = request.session.get('current_profile_id')
        if profile_id:
            try:
                return Profile.objects.get(id=profile_id)
            except Profile.DoesNotExist:
                return None
        return None


def home(request):
    """Home page - show welcome page with option to create profile"""
    # If user is authenticated, redirect based on role
    if request.user.is_authenticated:
        try:
            if request.user.user_profile.is_recruiter():
                return redirect('jobs:job_list')
            else:
                # Check if job seeker has a profile
                try:
                    profile = request.user.profile
                    return redirect('profiles:profile_detail')
                except Profile.DoesNotExist:
                    return redirect('profiles:create_profile')
        except UserProfile.DoesNotExist:
            pass
    
    return render(request, 'profiles/home.html')


def recruiter_login(request):
    """Login page specifically for recruiters"""
    from django.contrib.auth import authenticate, login as auth_login
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Check if user is a recruiter
            try:
                if user.user_profile.is_recruiter():
                    auth_login(request, user)
                    messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
                    return redirect('jobs:job_list')
                else:
                    messages.error(request, 'This account is registered as a Job Seeker. Please use the Job Seeker login.')
                    return redirect('profiles:jobseeker_login')
            except UserProfile.DoesNotExist:
                messages.error(request, 'User profile not found. Please contact support.')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'profiles/recruiter_login.html', {'user_type': 'Recruiter'})


def jobseeker_login(request):
    """Login page specifically for job seekers"""
    from django.contrib.auth import authenticate, login as auth_login
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Check if user is a job seeker
            try:
                if user.user_profile.is_job_seeker():
                    auth_login(request, user)
                    messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
                    # Check if profile exists
                    try:
                        profile = user.profile
                        return redirect('profiles:profile_detail')
                    except Profile.DoesNotExist:
                        return redirect('profiles:create_profile')
                else:
                    messages.error(request, 'This account is registered as a Recruiter. Please use the Recruiter login.')
                    return redirect('profiles:recruiter_login')
            except UserProfile.DoesNotExist:
                messages.error(request, 'User profile not found. Please contact support.')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'profiles/jobseeker_login.html', {'user_type': 'Job Seeker'})


def recruiter_signup(request):
    """Sign up page specifically for recruiters"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            # Set user type to recruiter
            user.user_profile.user_type = 'recruiter'
            user.user_profile.save()
            # Log the user in
            login(request, user)
            messages.success(request, 'Account created successfully! Welcome, Recruiter!')
            return redirect('jobs:job_list')
    else:
        # Pre-set the user_type to recruiter
        form = CustomUserCreationForm(initial={'user_type': 'recruiter'})
    
    return render(request, 'profiles/recruiter_signup.html', {'form': form, 'user_type': 'Recruiter'})


def jobseeker_signup(request):
    """Sign up page specifically for job seekers"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            # Set user type to job seeker
            user.user_profile.user_type = 'job_seeker'
            user.user_profile.save()
            # Log the user in
            login(request, user)
            messages.success(request, 'Account created successfully! Welcome, Job Seeker!')
            return redirect('profiles:create_profile')
    else:
        # Pre-set the user_type to job_seeker
        form = CustomUserCreationForm(initial={'user_type': 'job_seeker'})
    
    return render(request, 'profiles/jobseeker_signup.html', {'form': form, 'user_type': 'Job Seeker'})


def signup(request):
    """Sign up page for new users to create accounts"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Log the user in after successful signup
            login(request, user)
            
            # Redirect based on user type
            if user.user_profile.is_recruiter():
                messages.success(request, 'Account created successfully! Welcome, Recruiter!')
                return redirect('jobs:job_list')  # Recruiters go to job list
            else:
                messages.success(request, 'Account created successfully! Welcome, Job Seeker!')
                return redirect('profiles:create_profile')  # Job seekers create their profile
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'profiles/signup.html', {'form': form})


def logout_view(request):
    """Logout the current user and redirect to landing page"""
    auth_logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('landing')


def profile_detail(request, profile_id=None):
    """Display a profile - either from session or by ID"""
    if profile_id:
        # View specific profile by ID
        profile = get_object_or_404(Profile, id=profile_id)
    elif request.user.is_authenticated:
        # Authenticated user viewing their own profile
        try:
            profile = request.user.profile
        except Profile.DoesNotExist:
            return redirect('profiles:create_profile')
    else:
        # Anonymous user - check session for profile ID
        profile_id = request.session.get('current_profile_id')
        if profile_id:
            try:
                profile = Profile.objects.get(id=profile_id)
            except Profile.DoesNotExist:
                return redirect('profiles:create_profile')
        else:
            return redirect('profiles:create_profile')
    
    context = {
        'profile': profile,
        'profile_skills': profile.profile_skills.select_related('skill').all(),
        'educations': profile.educations.all(),
        'work_experiences': profile.work_experiences.all(),
        'links': profile.links.all(),
        'is_owner': (request.user.is_authenticated and profile.user == request.user) or (not request.user.is_authenticated and profile_id == request.session.get('current_profile_id')),
    }
    return render(request, 'profiles/profile_detail.html', context)


def create_profile(request):
    """Create a new profile"""
    if request.user.is_authenticated:
        try:
            # Check if profile already exists
            profile = request.user.profile
            return redirect('profiles:edit_profile')
        except Profile.DoesNotExist:
            pass
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, user=request.user if request.user.is_authenticated else None)
        if form.is_valid():
            profile = form.save()
            if not request.user.is_authenticated:
                # Store profile ID in session for anonymous users
                request.session['current_profile_id'] = profile.id
            messages.success(request, 'Profile created successfully!')
            return redirect('profiles:profile_detail')
    else:
        form = ProfileForm(user=request.user if request.user.is_authenticated else None)
    
    return render(request, 'profiles/profile_form.html', {'form': form, 'title': 'Create Profile'})


def edit_profile(request):
    """Edit a profile"""
    if request.user.is_authenticated:
        try:
            profile = request.user.profile
        except Profile.DoesNotExist:
            return redirect('profiles:create_profile')
    else:
        # Anonymous user - get profile from session
        profile_id = request.session.get('current_profile_id')
        if not profile_id:
            return redirect('profiles:create_profile')
        try:
            profile = Profile.objects.get(id=profile_id)
        except Profile.DoesNotExist:
            return redirect('profiles:create_profile')
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile, user=request.user if request.user.is_authenticated else None)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profiles:profile_detail')
    else:
        form = ProfileForm(instance=profile, user=request.user if request.user.is_authenticated else None)
    
    return render(request, 'profiles/profile_form.html', {'form': form, 'title': 'Edit Profile'})


def add_skill(request):
    """Add a skill to the current profile"""
    profile = get_current_profile(request)
    if not profile:
        messages.error(request, 'Please create a profile first.')
        return redirect('profiles:create_profile')
    
    if request.method == 'POST':
        form = ProfileSkillForm(request.POST)
        if form.is_valid():
            profile_skill = form.save(commit=False)
            profile_skill.profile = profile
            profile_skill.save()
            messages.success(request, f'Skill "{profile_skill.skill.name}" added successfully!')
            return redirect('profiles:profile_detail')
    else:
        form = ProfileSkillForm()
    
    return render(request, 'profiles/add_skill.html', {'form': form})


def remove_skill(request, skill_id):
    """Remove a skill from the current profile"""
    profile = get_current_profile(request)
    if not profile:
        messages.error(request, 'Profile not found.')
        return redirect('profiles:create_profile')
    
    try:
        profile_skill = get_object_or_404(ProfileSkill, profile=profile, id=skill_id)
        skill_name = profile_skill.skill.name
        profile_skill.delete()
        messages.success(request, f'Skill "{skill_name}" removed successfully!')
    except ProfileSkill.DoesNotExist:
        messages.error(request, 'Skill not found.')
    
    return redirect('profiles:profile_detail')


def add_education(request):
    """Add education to the current profile"""
    profile = get_current_profile(request)
    if not profile:
        messages.error(request, 'Please create a profile first.')
        return redirect('profiles:create_profile')
    
    if request.method == 'POST':
        form = EducationForm(request.POST)
        if form.is_valid():
            education = form.save(commit=False)
            education.profile = profile
            education.save()
            messages.success(request, 'Education added successfully!')
            return redirect('profiles:profile_detail')
    else:
        form = EducationForm()
    
    return render(request, 'profiles/add_education.html', {'form': form})


def edit_education(request, education_id):
    """Edit education in the current profile"""
    profile = get_current_profile(request)
    if not profile:
        messages.error(request, 'Profile not found.')
        return redirect('profiles:create_profile')
    
    education = get_object_or_404(Education, profile=profile, id=education_id)
    
    if request.method == 'POST':
        form = EducationForm(request.POST, instance=education)
        if form.is_valid():
            form.save()
            messages.success(request, 'Education updated successfully!')
            return redirect('profiles:profile_detail')
    else:
        form = EducationForm(instance=education)
    
    return render(request, 'profiles/edit_education.html', {'form': form, 'education': education})


def delete_education(request, education_id):
    """Delete education from the current profile"""
    profile = get_current_profile(request)
    if not profile:
        messages.error(request, 'Profile not found.')
        return redirect('profiles:create_profile')
    
    education = get_object_or_404(Education, profile=profile, id=education_id)
    education.delete()
    messages.success(request, 'Education deleted successfully!')
    
    return redirect('profiles:profile_detail')


def add_work_experience(request):
    """Add work experience to the current profile"""
    profile = get_current_profile(request)
    if not profile:
        messages.error(request, 'Please create a profile first.')
        return redirect('profiles:create_profile')
    
    if request.method == 'POST':
        form = WorkExperienceForm(request.POST)
        if form.is_valid():
            work_experience = form.save(commit=False)
            work_experience.profile = profile
            work_experience.save()
            messages.success(request, 'Work experience added successfully!')
            return redirect('profiles:profile_detail')
    else:
        form = WorkExperienceForm()
    
    return render(request, 'profiles/add_work_experience.html', {'form': form})


def edit_work_experience(request, work_id):
    """Edit work experience in the current profile"""
    profile = get_current_profile(request)
    if not profile:
        messages.error(request, 'Profile not found.')
        return redirect('profiles:create_profile')
    
    work_experience = get_object_or_404(WorkExperience, profile=profile, id=work_id)
    
    if request.method == 'POST':
        form = WorkExperienceForm(request.POST, instance=work_experience)
        if form.is_valid():
            form.save()
            messages.success(request, 'Work experience updated successfully!')
            return redirect('profiles:profile_detail')
    else:
        form = WorkExperienceForm(instance=work_experience)
    
    return render(request, 'profiles/edit_work_experience.html', {'form': form, 'work_experience': work_experience})


def delete_work_experience(request, work_id):
    """Delete work experience from the current profile"""
    profile = get_current_profile(request)
    if not profile:
        messages.error(request, 'Profile not found.')
        return redirect('profiles:create_profile')
    
    work_experience = get_object_or_404(WorkExperience, profile=profile, id=work_id)
    work_experience.delete()
    messages.success(request, 'Work experience deleted successfully!')
    
    return redirect('profiles:profile_detail')


def add_link(request):
    """Add a link to the current profile"""
    profile = get_current_profile(request)
    if not profile:
        messages.error(request, 'Please create a profile first.')
        return redirect('profiles:create_profile')
    
    if request.method == 'POST':
        form = LinkForm(request.POST)
        if form.is_valid():
            link = form.save(commit=False)
            link.profile = profile
            link.save()
            messages.success(request, 'Link added successfully!')
            return redirect('profiles:profile_detail')
    else:
        form = LinkForm()
    
    return render(request, 'profiles/add_link.html', {'form': form})


def edit_link(request, link_id):
    """Edit a link in the current profile"""
    profile = get_current_profile(request)
    if not profile:
        messages.error(request, 'Profile not found.')
        return redirect('profiles:create_profile')
    
    link = get_object_or_404(Link, profile=profile, id=link_id)
    
    if request.method == 'POST':
        form = LinkForm(request.POST, instance=link)
        if form.is_valid():
            form.save()
            messages.success(request, 'Link updated successfully!')
            return redirect('profiles:profile_detail')
    else:
        form = LinkForm(instance=link)
    
    return render(request, 'profiles/edit_link.html', {'form': form, 'link': link})


def delete_link(request, link_id):
    """Delete a link from the current profile"""
    profile = get_current_profile(request)
    if not profile:
        messages.error(request, 'Profile not found.')
        return redirect('profiles:create_profile')
    
    link = get_object_or_404(Link, profile=profile, id=link_id)
    link.delete()
    messages.success(request, 'Link deleted successfully!')
    
    return redirect('profiles:profile_detail')


def search_skills(request):
    """AJAX endpoint for searching skills"""
    if request.method == 'GET':
        search_term = request.GET.get('search', '')
        if len(search_term) >= 2:
            skills = Skill.objects.filter(name__icontains=search_term)[:10]
            skill_data = [{'id': skill.id, 'name': skill.name} for skill in skills]
            return JsonResponse({'skills': skill_data})
    return JsonResponse({'skills': []})


@login_required
@recruiter_required
def profile_list(request):
    """List all public profiles (for recruiters to browse)"""
    # Show all profiles (including anonymous ones). Use select_related/prefetch for performance.
    profiles = Profile.objects.select_related('user').prefetch_related('profile_skills__skill').all()
    
    # Add search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        profiles = profiles.filter(
            Q(headline__icontains=search_query) |
            Q(bio__icontains=search_query) |
            Q(location__icontains=search_query) |
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(profile_skills__skill__name__icontains=search_query)
        ).distinct()
    
    paginator = Paginator(profiles, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'profiles/profile_list.html', context)


@login_required
@recruiter_required
def public_profile_detail(request, user_id):
    """View a public profile (for recruiters)"""
    user = get_object_or_404(User, id=user_id)
    profile = get_object_or_404(Profile, user=user)
    
    context = {
        'profile': profile,
        'profile_skills': profile.profile_skills.select_related('skill').all(),
        'educations': profile.educations.all(),
        'work_experiences': profile.work_experiences.all(),
        'links': profile.links.all(),
        'is_public': True,
    }
    return render(request, 'profiles/public_profile_detail.html', context)


@login_required
@recruiter_required
def profile_detail_by_id(request, profile_id):
    """View a profile by profile ID (allows viewing anonymous/session-created profiles) - Recruiters only"""
    profile = get_object_or_404(Profile, id=profile_id)

    context = {
        'profile': profile,
        'profile_skills': profile.profile_skills.select_related('skill').all(),
        'educations': profile.educations.all(),
        'work_experiences': profile.work_experiences.all(),
        'links': profile.links.all(),
        'is_public': True,
    }
    return render(request, 'profiles/public_profile_detail.html', context)
