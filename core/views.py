from django.conf import settings
from django.contrib.auth.decorators import login_not_required
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme


def get_safe_next_url(request):
    next_url = request.GET.get("next") or settings.LOGIN_REDIRECT_URL

    is_safe = url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    )

    if not is_safe:
        return settings.LOGIN_REDIRECT_URL

    return next_url


@login_not_required
def login_start(request):
    next_url = get_safe_next_url(request)

    if request.user.is_authenticated:
        return redirect(next_url)

    provider_id = getattr(settings, "OIDC_PROVIDER_ID", "dev")
    oidc_login_url = f"/accounts/oidc/{provider_id}/login/"

    return render(
        request,
        "login_start.html",
        {
            "oidc_login_url": oidc_login_url,
            "next_url": next_url,
        },
    )


def home(request):
    return render(request, "home.html")
