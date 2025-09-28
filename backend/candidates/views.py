from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.core.paginator import Paginator
from .serializers import CandidateSerializer
from .search import SearchParams, filter_candidates, score_candidate, haversine_km

def home(request):
    return JsonResponse({"message": "Candidate Search API", "endpoints": ["/api/candidates/search"]})

@api_view(["POST"])
def search_candidates(request):
    body = request.data if isinstance(request.data, dict) else {}
    skills = body.get("skills", []) or []
    projects = body.get("projects", []) or []
    require_all = bool(body.get("requireAllSkills", False))
    min_level = int(body.get("minSkillLevel", 3))
    location = body.get("location") or {}
    lat = location.get("lat")
    lng = location.get("lng")
    radius_km = location.get("radiusKm")

    params = SearchParams(
        skills=[str(s) for s in skills],
        require_all_skills=require_all,
        min_skill_level=min_level,
        projects=[str(p) for p in projects],
        latitude=float(lat) if lat is not None else None,
        longitude=float(lng) if lng is not None else None,
        radius_km=float(radius_km) if radius_km is not None else None,
    )

    qs = filter_candidates(params)

    enriched = []
    for c in qs:
        c.score = score_candidate(c, params)
        c.distance_km = None
        if params.latitude is not None and params.longitude is not None and c.location:
            c.distance_km = haversine_km(params.latitude, params.longitude, c.location.latitude, c.location.longitude)
        enriched.append(c)

    enriched.sort(key=lambda c: getattr(c, "score", 0.0), reverse=True)

    page = int(body.get("page", 1))
    paginator = Paginator(enriched, 10)
    page_obj = paginator.get_page(page)
    serializer = CandidateSerializer(page_obj, many=True)
    return Response(
        {
            "count": paginator.count,
            "numPages": paginator.num_pages,
            "page": page_obj.number,
            "results": serializer.data,
        },
        status=status.HTTP_200_OK,
    )
