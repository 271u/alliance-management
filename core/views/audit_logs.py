from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from core.models import AuditLog


@require_http_methods(["GET"])
def audit_log_list(request):
    if not request.user.is_staff:
        raise PermissionDenied

    audit_logs = (
        AuditLog.objects
        .select_related("actor", "content_type")
        .order_by("-created_at")
    )

    selected_action = request.GET.get("action", "")

    if selected_action in AuditLog.Action.values:
        audit_logs = audit_logs.filter(action=selected_action)

    selected_query = request.GET.get("q", "").strip()

    if selected_query:
        audit_logs = audit_logs.filter(
            Q(message__icontains=selected_query)
            | Q(object_repr__icontains=selected_query)
        )

    paginator = Paginator(audit_logs, 25)
    page = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "audit_logs.html",
        {
            "page": page,
            "selected_action": selected_action,
            "selected_query": selected_query,
            "actions": AuditLog.Action.choices,
        },
    )
