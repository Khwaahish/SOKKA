from django.urls import path
from . import views

app_name = "jobs"

urlpatterns = [
    path("", views.job_list, name="job_list"),
    path("", views.job_list, name="list"),  # Alias for backward compatibility
    path("create/", views.job_create, name="create"),
    path("my-applications/", views.my_applications, name="my_applications"),
    path("<int:pk>/", views.job_detail, name="detail"),
    path("<int:pk>/apply/", views.apply_to_job, name="apply"),
    path("<int:pk>/edit/", views.job_edit, name="edit"),
    path("<int:pk>/applicants/", views.job_applicants, name="applicants"),
    path("application/<int:application_id>/add-to-kanban/", views.add_to_kanban, name="add_to_kanban"),
]
