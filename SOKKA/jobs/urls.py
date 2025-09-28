from django.urls import path
from . import views

app_name = "jobs"

urlpatterns = [
    path("", views.job_list, name="list"),
    path("create/", views.job_create, name="create"),
    path("<int:pk>/", views.job_detail, name="detail"),
    path("<int:pk>/apply/", views.apply_to_job, name="apply"),
    path("<int:pk>/edit/", views.job_edit, name="edit"),
]
