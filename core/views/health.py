from django.contrib.auth.decorators import login_not_required # pyright: ignore[reportAttributeAccessIssue]
from django.db import connection
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods


@login_not_required
@require_http_methods(["GET"])
def healthz(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception:
        return JsonResponse(
            {
                "status": "unhealthy",
                "database": "unavailable",
            },
            status=503,
        )

    return JsonResponse(
        {
            "status": "ok",
            "database": "ok",
        }
    )
