"""
AI Matching Engine & Pricing Engine service layer.

The match_score is calculated from:
  - Skill overlap (50% weight)
  - User rating   (30% weight)
  - Proximity     (20% weight)

This is structured so a real ML model can replace the scoring logic later.
"""
import math
from django.db.models import Q
from accounts.models import EmployeeProfile, Skill


def _skill_score(employee_profile, required_skills):
    """Return 0-1 score based on skill tag overlap."""
    if not required_skills:
        return 1.0
    emp_skills = set(employee_profile.skills.values_list('id', flat=True))
    req_skills = set(s.id if isinstance(s, Skill) else s for s in required_skills)
    if not req_skills:
        return 1.0
    overlap = emp_skills & req_skills
    return len(overlap) / len(req_skills)


def _rating_score(employee_profile):
    """Return 0-1 score normalised from 0-5 star rating."""
    return float(employee_profile.avg_rating) / 5.0


def _proximity_score(employee_profile, customer_lat=None, customer_lng=None, max_km=50):
    """Return 0-1 score based on haversine distance. 1 = same location, 0 = >= max_km away."""
    if (
        customer_lat is None
        or customer_lng is None
        or employee_profile.latitude is None
        or employee_profile.longitude is None
    ):
        return 0.5  # neutral when location data is missing

    R = 6371  # Earth radius in km
    lat1, lat2 = math.radians(customer_lat), math.radians(employee_profile.latitude)
    dlat = lat2 - lat1
    dlng = math.radians(employee_profile.longitude - customer_lng)
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng / 2) ** 2
    distance = R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return max(0, 1 - distance / max_km)


def rank_employees(required_skills=None, customer_lat=None, customer_lng=None,
                   availability='available', limit=20):
    """
    Rank available employees by match score.

    Returns a list of dicts:
        [{"profile": EmployeeProfile, "score": float, "breakdown": {...}}, ...]

    Replace the weighted-sum logic here with a trained ML model for
    production-grade recommendation accuracy.
    """
    qs = EmployeeProfile.objects.select_related('user').prefetch_related('skills')
    if availability:
        qs = qs.filter(availability=availability)

    results = []
    for profile in qs:
        s_score = _skill_score(profile, required_skills or [])
        r_score = _rating_score(profile)
        p_score = _proximity_score(profile, customer_lat, customer_lng)

        # Weighted sum – adjust weights or swap with ML model
        match_score = round(s_score * 0.50 + r_score * 0.30 + p_score * 0.20, 4)

        results.append({
            'profile': profile,
            'score': match_score,
            'breakdown': {
                'skill': round(s_score, 2),
                'rating': round(r_score, 2),
                'proximity': round(p_score, 2),
            },
        })

    results.sort(key=lambda x: x['score'], reverse=True)
    return results[:limit]


def calculate_booking_cost(employee_profile, duration_type, duration_value):
    """Pricing Engine: straightforward Rate × Duration."""
    rate_map = {
        'hourly': employee_profile.hourly_rate,
        'daily': employee_profile.daily_rate,
        'monthly': employee_profile.monthly_rate,
    }
    rate = rate_map.get(duration_type, 0)
    return rate * duration_value, rate


def smart_search(query_text):
    """
    NLP-style search using Django Q objects.
    Searches employees by skill name, bio, city, and username.
    Ready to be replaced with a real NLP / vector-search backend.
    """
    if not query_text:
        return EmployeeProfile.objects.none()

    tokens = query_text.strip().split()
    q = Q()
    for token in tokens:
        q |= (
            Q(skills__name__icontains=token)
            | Q(bio__icontains=token)
            | Q(user__city__icontains=token)
            | Q(user__first_name__icontains=token)
            | Q(user__last_name__icontains=token)
            | Q(user__username__icontains=token)
        )
    return (
        EmployeeProfile.objects
        .filter(q, availability='available')
        .select_related('user')
        .prefetch_related('skills')
        .distinct()
    )
