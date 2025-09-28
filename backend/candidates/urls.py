from django.urls import path
from .views import home, search_candidates

urlpatterns = [
    path("", home, name="home"),
    path("candidates/search", search_candidates, name="candidate-search"),
]
