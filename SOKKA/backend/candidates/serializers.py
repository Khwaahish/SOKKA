from rest_framework import serializers
from .models import Candidate, Skill, Project, Location

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ["id", "name"]

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ["id", "title", "tags", "url"]

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ["city", "country", "latitude", "longitude"]

class CandidateSerializer(serializers.ModelSerializer):
    skills = SkillSerializer(many=True, read_only=True)
    projects = ProjectSerializer(many=True, read_only=True)
    location = LocationSerializer(read_only=True)
    score = serializers.FloatField(read_only=True)
    distance_km = serializers.FloatField(read_only=True)

    class Meta:
        model = Candidate
        fields = [
            "id",
            "full_name",
            "headline",
            "summary",
            "years_experience",
            "location",
            "skills",
            "projects",
            "score",
            "distance_km",
        ]
