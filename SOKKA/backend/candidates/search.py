from __future__ import annotations
from dataclasses import dataclass
from math import radians, cos, sin, asin, sqrt
from typing import Optional

from django.db.models import Q, QuerySet
from .models import Candidate

EARTH_RADIUS_KM = 6371.0

def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    return EARTH_RADIUS_KM * c

@dataclass
class SearchParams:
    skills: list[str]
    require_all_skills: bool
    min_skill_level: int
    projects: list[str]
    latitude: Optional[float]
    longitude: Optional[float]
    radius_km: Optional[float]

def filter_candidates(params: SearchParams) -> QuerySet[Candidate]:
    qs = Candidate.objects.select_related("location").prefetch_related("skills", "projects")

    if params.skills:
        skill_q = Q()
        if params.require_all_skills:
            for s in params.skills:
                skill_q &= Q(skills__name__iexact=s, candidateskill__level__gte=params.min_skill_level)
            qs = qs.filter(skill_q).distinct()
        else:
            for s in params.skills:
                skill_q |= Q(skills__name__iexact=s, candidateskill__level__gte=params.min_skill_level)
            qs = qs.filter(skill_q).distinct()

    if params.projects:
        proj_q = Q()
        for p in params.projects:
            proj_q |= Q(projects__title__icontains=p) | Q(projects__tags__icontains=p)
        qs = qs.filter(proj_q).distinct()

    if params.latitude is not None and params.longitude is not None and params.radius_km:
        ids_in_radius: list[int] = []
        for c in qs:
            if c.location is None:
                continue
            d = haversine_km(params.latitude, params.longitude, c.location.latitude, c.location.longitude)
            if d <= params.radius_km:
                ids_in_radius.append(c.id)
        qs = qs.filter(id__in=ids_in_radius)

    return qs

def score_candidate(candidate: Candidate, params: SearchParams) -> float:
    skill_score = 0.0
    if params.skills:
        matched = 0.0
        for s in params.skills:
            cs = candidate.candidateskill_set.filter(skill__name__iexact=s).first()
            if cs and cs.level >= params.min_skill_level:
                matched += cs.level / 5.0
        skill_score = matched / max(len(params.skills), 1)

    project_score = 0.0
    if params.projects:
        total = len(params.projects)
        hits = 0
        titles = " ".join(candidate.projects.values_list("title", flat=True)).lower()
        tags = " ".join(candidate.projects.values_list("tags", flat=True)).lower()
        haystack = f"{titles} {tags}"
        for p in params.projects:
            if p.lower() in haystack:
                hits += 1
        project_score = hits / total

    distance_score = 0.0
    if params.latitude is not None and params.longitude is not None and params.radius_km and candidate.location:
        d = haversine_km(params.latitude, params.longitude, candidate.location.latitude, candidate.location.longitude)
        distance_score = max(0.0, 1.0 - (d / params.radius_km))

    return 0.6 * skill_score + 0.3 * distance_score + 0.1 * project_score
