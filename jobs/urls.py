from django.urls import path
from . import views

app_name = "jobs"

urlpatterns = [
    path("", views.job_list, name="job_list"),
    path("", views.job_list, name="list"),  # Alias for backward compatibility
    path("create/", views.job_create, name="create"),
    path("my-applications/", views.my_applications, name="my_applications"),
    path("recommendations/", views.job_recommendations, name="recommendations"),
    path("my-emails/", views.my_emails, name="my_emails"),
    path("matched-candidates/", views.matched_candidates, name="matched_candidates"),
    path("<int:pk>/", views.job_detail, name="detail"),
    path("<int:pk>/apply/", views.apply_to_job, name="apply"),
    path("<int:pk>/edit/", views.job_edit, name="edit"),
    path("<int:pk>/applicants/", views.job_applicants, name="applicants"),
    path("application/<int:application_id>/add-to-kanban/", views.add_to_kanban, name="add_to_kanban"),
    path("application/<int:application_id>/send-email/", views.send_email_to_candidate, name="send_email"),
    path("application/<int:application_id>/email-history/", views.email_history, name="email_history"),
    path("email/<int:email_id>/mark-read/", views.mark_email_read, name="mark_email_read"),
    path("candidate/<int:profile_id>/send-email/", views.send_email_to_candidate_direct, name="send_email_direct"),
    # Saved searches
    path("saved-searches/", views.saved_searches, name="saved_searches"),
    path("saved-searches/save/", views.save_candidate_search, name="save_candidate_search"),
    path("saved-searches/<int:search_id>/", views.saved_search_detail, name="saved_search_detail"),
    path("saved-searches/<int:search_id>/delete/", views.delete_saved_search, name="delete_saved_search"),
    # Search notifications
    path("search-notifications/", views.search_notifications, name="search_notifications"),
    path("notification/<int:notification_id>/mark-read/", views.mark_notification_read, name="mark_notification_read"),
    # Candidate recommendations
    path("job/<int:job_id>/recommendations/", views.candidate_recommendations, name="candidate_recommendations"),
]
