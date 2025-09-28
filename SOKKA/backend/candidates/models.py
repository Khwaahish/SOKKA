from django.db import models

class Location(models.Model):
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self) -> str:
        return f"{self.city}, {self.country}".strip(", ")

class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self) -> str:
        return self.name

class Project(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    tags = models.CharField(max_length=300, blank=True)  # comma-separated tags
    url = models.URLField(blank=True)

    def __str__(self) -> str:
        return self.title

class Candidate(models.Model):
    full_name = models.CharField(max_length=200)
    headline = models.CharField(max_length=200, blank=True)
    summary = models.TextField(blank=True)
    years_experience = models.PositiveIntegerField(default=0)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)
    skills = models.ManyToManyField(Skill, through="CandidateSkill", related_name="candidates")
    projects = models.ManyToManyField(Project, related_name="candidates", blank=True)

    def __str__(self) -> str:
        return self.full_name

class CandidateSkill(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    level = models.PositiveSmallIntegerField(default=3)  # 0–5
    class Meta:
        unique_together = ("candidate", "skill")
