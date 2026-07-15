from collections.abc import Callable
from functools import wraps
from typing import Any

from django.http import HttpRequest, JsonResponse


def json_permission_required(permission: str):
    """
    Require a Django permission for a JSON API endpoint.

    Unlike Django's regular permission_required decorator, this returns
    a JSON response instead of an HTML 403 page.
    """

    def decorator(view_func: Callable[..., Any]):
        @wraps(view_func)
        def wrapper(
            request: HttpRequest,
            *args: Any,
            **kwargs: Any,
        ):
            if not request.user.has_perm(permission):
                return JsonResponse(
                    {
                        "error": "permission_denied",
                        "detail": "You do not have permission to perform this action.",
                    },
                    status=403,
                )

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator
