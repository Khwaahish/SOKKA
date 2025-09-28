from django.contrib import admin
from .models import Profile, Skill, ProfileSkill, Education, WorkExperience, Link


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
    list_display = ['user', 'headline', 'location', 'created_at']
    list_filter = ['created_at', 'location']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'headline']
    inlines = [ProfileSkillInline, EducationInline, WorkExperienceInline, LinkInline]
    readonly_fields = ['created_at', 'updated_at']
    
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


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(ProfileSkill)
class ProfileSkillAdmin(admin.ModelAdmin):
    list_display = ['profile', 'skill', 'proficiency_level']
    list_filter = ['proficiency_level']
    search_fields = ['profile__user__first_name', 'profile__user__last_name', 'skill__name']


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ['profile', 'degree', 'field_of_study', 'institution', 'start_date', 'end_date', 'is_current']
    list_filter = ['start_date', 'end_date', 'is_current']
    search_fields = ['profile__user__first_name', 'profile__user__last_name', 'institution', 'degree']


@admin.register(WorkExperience)
class WorkExperienceAdmin(admin.ModelAdmin):
    list_display = ['profile', 'position', 'company', 'start_date', 'end_date', 'is_current']
    list_filter = ['start_date', 'end_date', 'is_current']
    search_fields = ['profile__user__first_name', 'profile__user__last_name', 'company', 'position']


@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    list_display = ['profile', 'link_type', 'title', 'url']
    list_filter = ['link_type']
    search_fields = ['profile__user__first_name', 'profile__user__last_name', 'title', 'url']