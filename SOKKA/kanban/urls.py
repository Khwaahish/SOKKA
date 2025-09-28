from django.urls import path
from . import views

app_name = 'kanban'

urlpatterns = [
    path('', views.kanban_board, name='kanban_board'),
    path('like-profile/<int:profile_id>/', views.like_profile, name='like_profile'),
    path('unlike-profile/<int:profile_id>/', views.unlike_profile, name='unlike_profile'),
    path('move-card/', views.MoveCardView.as_view(), name='move_card'),
    path('update-notes/<int:card_id>/', views.update_card_notes, name='update_notes'),
    path('liked-profiles/', views.get_liked_profiles, name='get_liked_profiles'),
]
