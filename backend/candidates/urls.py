from django.urls import path
from .views import search_candidates

urlpatterns = [
    path("candidates/search", search_candidates, name="candidate-search"),
]
