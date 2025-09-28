from django.test import TestCase
from django.core.management import call_command
from django.conf import settings
from .search import SearchParams, filter_candidates, score_candidate
from .models import Candidate

class SearchTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("loaddata", "candidates/fixtures/sample_data.json")

    def test_filter_by_skill_any(self):
        params = SearchParams(skills=["React"], require_all_skills=False, min_skill_level=3, projects=[], latitude=None, longitude=None, radius_km=None)
        qs = filter_candidates(params)
        self.assertTrue(qs.filter(full_name="Taylor Kim").exists())

    def test_filter_by_location_radius(self):
        # near San Francisco, 50km radius should include Alex
        params = SearchParams(skills=[], require_all_skills=False, min_skill_level=3, projects=[], latitude=37.7749, longitude=-122.4194, radius_km=50)
        qs = filter_candidates(params)
        self.assertTrue(qs.filter(full_name="Alex Rivera").exists())

    def test_scoring_prefers_more_skill_matches(self):
        params = SearchParams(skills=["Python", "Django"], require_all_skills=False, min_skill_level=3, projects=[], latitude=None, longitude=None, radius_km=None)
        qs = list(filter_candidates(params))
        scored = [(c.full_name, score_candidate(c, params)) for c in qs]
        scores = dict(scored)
        self.assertGreater(scores["Alex Rivera"], scores["Jordan Lee"])
