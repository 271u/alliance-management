from contextvars import ContextVar


_current_request = ContextVar("current_request", default=None)


def get_current_request():
    return _current_request.get()


def get_current_user():
    request = get_current_request()

    if request is None:
        return None

    user = getattr(request, "user", None)

    if user is None or not user.is_authenticated:
        return None

    return user


def get_current_path():
    request = get_current_request()

    if request is None:
        return ""

    return request.path


def get_current_ip_address():
    request = get_current_request()

    if request is None:
        return None

    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")

    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    return request.META.get("REMOTE_ADDR")


class AuditContextMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        token = _current_request.set(request)

        try:
            return self.get_response(request)
        finally:
            _current_request.reset(token)
