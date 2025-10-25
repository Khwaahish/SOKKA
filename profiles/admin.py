from django.contrib import admin
from django.http import HttpResponse
from django.utils import timezone
import csv
from .models import Profile, Skill, ProfileSkill, Education, WorkExperience, Link, UserProfile, ProfilePrivacySettings


def export_profiles_to_csv(modeladmin, request, queryset):
    """Export selected profiles to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="profiles_export_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Profile ID', 'Full Name', 'Email', 'Headline', 'Location', 'Phone',
        'Bio Preview', 'Skills', 'Total Experience (Years)', 'Education Count',
        'Privacy Setting', 'Allow Contact', 'Created At', 'Updated At'
    ])
    
    for profile in queryset:
        # Get all skills
        skills = ', '.join([ps.skill.name for ps in profile.profile_skills.all()])
        
        # Calculate total years of experience
        total_experience = 0
        for exp in profile.work_experiences.all():
            end = exp.end_date or timezone.now().date()
            start = exp.start_date
            years = (end - start).days / 365.25
            total_experience += years
        
        # Get privacy settings
        privacy_setting = 'N/A'
        allow_contact = 'N/A'
        if hasattr(profile, 'privacy_settings'):
            privacy_setting = profile.privacy_settings.get_profile_visibility_display()
            allow_contact = 'Yes' if profile.privacy_settings.allow_contact else 'No'
        
        # Bio preview
        bio_preview = profile.bio[:100] + '...' if len(profile.bio) > 100 else profile.bio
        
        writer.writerow([
            profile.id,
            profile.get_full_name(),
            profile.get_email(),
            profile.headline,
            profile.location,
            profile.phone or 'N/A',
            bio_preview,
            skills or 'N/A',
            f"{total_experience:.1f}",
            profile.educations.count(),
            privacy_setting,
            allow_contact,
            profile.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            profile.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    return response

export_profiles_to_csv.short_description = "Export selected profiles to CSV"


def export_skills_analysis_to_csv(modeladmin, request, queryset):
    """Export skills analysis to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="skills_analysis_export_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Profile', 'Skill', 'Proficiency Level', 'Profile Headline',
        'Profile Location', 'Years of Experience'
    ])
    
    for profile_skill in queryset:
        # Calculate years of experience for this profile
        total_experience = 0
        for exp in profile_skill.profile.work_experiences.all():
            end = exp.end_date or timezone.now().date()
            start = exp.start_date
            years = (end - start).days / 365.25
            total_experience += years
        
        writer.writerow([
            profile_skill.profile.get_full_name(),
            profile_skill.skill.name,
            profile_skill.get_proficiency_level_display(),
            profile_skill.profile.headline,
            profile_skill.profile.location or 'N/A',
            f"{total_experience:.1f}"
        ])
    
    return response

export_skills_analysis_to_csv.short_description = "Export selected skills to CSV"


def export_work_experience_to_csv(modeladmin, request, queryset):
    """Export work experience to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="work_experience_export_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Profile Name', 'Company', 'Position', 'Location', 'Start Date',
        'End Date', 'Duration (Years)', 'Is Current', 'Description Preview'
    ])
    
    for exp in queryset:
        # Calculate duration
        end = exp.end_date or timezone.now().date()
        start = exp.start_date
        duration = (end - start).days / 365.25
        
        # Description preview
        desc_preview = exp.description[:150] + '...' if len(exp.description) > 150 else exp.description
        
        writer.writerow([
            exp.profile.get_full_name(),
            exp.company,
            exp.position,
            exp.location or 'N/A',
            exp.start_date.strftime('%Y-%m-%d'),
            exp.end_date.strftime('%Y-%m-%d') if exp.end_date else 'Present',
            f"{duration:.1f}",
            'Yes' if exp.is_current else 'No',
            desc_preview
        ])
    
    return response

export_work_experience_to_csv.short_description = "Export selected work experience to CSV"


def export_education_to_csv(modeladmin, request, queryset):
    """Export education to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="education_export_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Profile Name', 'Institution', 'Degree', 'Field of Study', 'Start Date',
        'End Date', 'GPA', 'Is Current', 'Description Preview'
    ])
    
    for edu in queryset:
        # Description preview
        desc_preview = edu.description[:150] + '...' if len(edu.description) > 150 else edu.description
        
        writer.writerow([
            edu.profile.get_full_name(),
            edu.institution,
            edu.degree,
            edu.field_of_study,
            edu.start_date.strftime('%Y-%m-%d'),
            edu.end_date.strftime('%Y-%m-%d') if edu.end_date else 'Present',
            str(edu.gpa) if edu.gpa else 'N/A',
            'Yes' if edu.is_current else 'No',
            desc_preview
        ])
    
    return response

export_education_to_csv.short_description = "Export selected education to CSV"


def export_user_profiles_to_csv(modeladmin, request, queryset):
    """Export user profiles (user types) to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="user_profiles_export_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Username', 'Full Name', 'Email', 'User Type', 'Is Active',
        'Date Joined', 'Last Login', 'Days Since Last Login'
    ])
    
    for user_profile in queryset:
        # Calculate days since last login
        days_since_login = 'Never'
        if user_profile.user.last_login:
            days = (timezone.now() - user_profile.user.last_login).days
            days_since_login = f"{days} days"
        
        writer.writerow([
            user_profile.user.username,
            user_profile.user.get_full_name(),
            user_profile.user.email,
            user_profile.get_user_type_display(),
            'Yes' if user_profile.user.is_active else 'No',
            user_profile.user.date_joined.strftime('%Y-%m-%d %H:%M:%S'),
            user_profile.user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user_profile.user.last_login else 'Never',
            days_since_login
        ])
    
    return response

export_user_profiles_to_csv.short_description = "Export selected user profiles to CSV"


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'user_type', 'created_at', 'is_active_display', 'last_login_display']
    list_filter = ['user_type', 'created_at', 'user__is_active']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at']
    actions = [export_user_profiles_to_csv]
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Role', {
            'fields': ('user_type',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def is_active_display(self, obj):
        return '✓' if obj.user.is_active else '✗'
    is_active_display.short_description = 'Active'
    is_active_display.boolean = True
    
    def last_login_display(self, obj):
        if obj.user.last_login:
            days = (timezone.now() - obj.user.last_login).days
            return f"{days} days ago"
        return 'Never'
    last_login_display.short_description = 'Last Login'


class ProfileSkillInline(admin.TabularInline):
    model = ProfileSkill
    extra = 1


class EducationInline(admin.TabularInline):
    model = Education
    extra = 1
    fields = ['institution', 'degree', 'field_of_study', 'start_date', 'end_date', 'is_current']


class WorkExperienceInline(admin.TabularInline):
    model = WorkExperience
    extra = 1
    fields = ['company', 'position', 'start_date', 'end_date', 'is_current', 'location']


class LinkInline(admin.TabularInline):
    model = Link
    extra = 1


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'headline', 'location', 'created_at', 'skills_count', 'experience_count']
    list_filter = ['created_at', 'location']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'headline']
    inlines = [ProfileSkillInline, EducationInline, WorkExperienceInline, LinkInline]
    readonly_fields = ['created_at', 'updated_at']
    actions = [export_profiles_to_csv]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'headline', 'bio', 'location', 'phone')
        }),
        ('Profile Picture', {
            'fields': ('profile_picture',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def skills_count(self, obj):
        return obj.profile_skills.count()
    skills_count.short_description = 'Skills'
    
    def experience_count(self, obj):
        return obj.work_experiences.count()
    experience_count.short_description = 'Experience'


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(ProfileSkill)
class ProfileSkillAdmin(admin.ModelAdmin):
    list_display = ['profile', 'skill', 'proficiency_level']
    list_filter = ['proficiency_level', 'skill']
    search_fields = ['profile__user__first_name', 'profile__user__last_name', 'skill__name']
    actions = [export_skills_analysis_to_csv]


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ['profile', 'degree', 'field_of_study', 'institution', 'start_date', 'end_date', 'is_current']
    list_filter = ['start_date', 'end_date', 'is_current', 'degree']
    search_fields = ['profile__user__first_name', 'profile__user__last_name', 'institution', 'degree']
    actions = [export_education_to_csv]


@admin.register(WorkExperience)
class WorkExperienceAdmin(admin.ModelAdmin):
    list_display = ['profile', 'position', 'company', 'start_date', 'end_date', 'is_current']
    list_filter = ['start_date', 'end_date', 'is_current', 'company']
    search_fields = ['profile__user__first_name', 'profile__user__last_name', 'company', 'position']
    actions = [export_work_experience_to_csv]


@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    list_display = ['profile', 'link_type', 'title', 'url']
    list_filter = ['link_type']
    search_fields = ['profile__user__first_name', 'profile__user__last_name', 'title', 'url']


@admin.register(ProfilePrivacySettings)
class ProfilePrivacySettingsAdmin(admin.ModelAdmin):
    list_display = ['profile', 'profile_visibility', 'allow_contact', 'contact_method', 'updated_at']
    list_filter = ['profile_visibility', 'allow_contact', 'contact_method']
    search_fields = ['profile__user__first_name', 'profile__user__last_name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Profile Visibility', {
            'fields': ('profile', 'profile_visibility')
        }),
        ('Field Visibility', {
            'fields': ('show_email', 'show_phone', 'show_location', 'show_bio', 'show_skills', 
                      'show_work_experience', 'show_education', 'show_links', 'show_profile_picture'),
            'classes': ('collapse',)
        }),
        ('Contact Preferences', {
            'fields': ('allow_contact', 'contact_method')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )