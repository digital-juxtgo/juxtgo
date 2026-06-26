# In apps/shared/views/health.py (create it)
from django.http import JsonResponse
from django.db import connections
from django.conf import settings


def health_check(request):
    try:
        # Check database connectivity
        connections["default"].cursor()
        # Optionally check Redis if configured
        # from django_redis import get_redis_connection
        # get_redis_connection("default").ping()
        return JsonResponse({"status": "ok"})
    except Exception as e:
        return JsonResponse({"status": "unhealthy", "error": str(e)}, status=503)
