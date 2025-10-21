from django.urls import path
from . import views

app_name = 'profiles'

urlpatterns = [
    # Home page
    path('', views.home, name='home'),
    
    # Authentication - Role-specific
    path('recruiter/login/', views.recruiter_login, name='recruiter_login'),
    path('recruiter/signup/', views.recruiter_signup, name='recruiter_signup'),
    path('jobseeker/login/', views.jobseeker_login, name='jobseeker_login'),
    path('jobseeker/signup/', views.jobseeker_signup, name='jobseeker_signup'),
    path('logout/', views.logout_view, name='logout'),
    
    # Legacy authentication (for backward compatibility)
    path('signup/', views.signup, name='signup'),
    
    # Profile management
    path('profile/', views.profile_detail, name='profile_detail'),
    path('create/', views.create_profile, name='create_profile'),
    path('edit/', views.edit_profile, name='edit_profile'),
    
    # Skills management
    path('skills/add/', views.add_skill, name='add_skill'),
    path('skills/<int:skill_id>/remove/', views.remove_skill, name='remove_skill'),
    
    # Education management
    path('education/add/', views.add_education, name='add_education'),
    path('education/<int:education_id>/edit/', views.edit_education, name='edit_education'),
    path('education/<int:education_id>/delete/', views.delete_education, name='delete_education'),
    
    # Work experience management
    path('work/add/', views.add_work_experience, name='add_work_experience'),
    path('work/<int:work_id>/edit/', views.edit_work_experience, name='edit_work_experience'),
    path('work/<int:work_id>/delete/', views.delete_work_experience, name='delete_work_experience'),
    
    # Links management
    path('links/add/', views.add_link, name='add_link'),
    path('links/<int:link_id>/edit/', views.edit_link, name='edit_link'),
    path('links/<int:link_id>/delete/', views.delete_link, name='delete_link'),
    
    # Public profiles (for recruiters)
    path('browse/', views.profile_list, name='profile_list'),
    path('view/<int:user_id>/', views.public_profile_detail, name='public_profile_detail'),
    # Allow viewing profiles by profile id (works for anonymous profiles as well)
    path('view/profile/<int:profile_id>/', views.profile_detail_by_id, name='public_profile_detail_by_id'),
    
    # AJAX endpoints
    path('api/skills/search/', views.search_skills, name='search_skills'),
]
