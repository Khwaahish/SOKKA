from django.contrib import admin
from .models import Candidate, Skill, Project, Location, CandidateSkill

admin.site.register(Candidate)
admin.site.register(Skill)
admin.site.register(Project)
admin.site.register(Location)
admin.site.register(CandidateSkill)
