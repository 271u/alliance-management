from typing import Any

from django.contrib.contenttypes.models import ContentType
from django.db import models

from core.audit_context import (
    get_current_ip_address,
    get_current_path,
    get_current_user,
)
from core.models.db.auditlog import AuditLog


def create_audit_log(
    *,
    model: type[models.Model],
    object_id: str,
    object_repr: str,
    action: str,
    changes: dict[str, Any],
    message: str = "",
) -> AuditLog:
    """Create one audit log entry with request context attached."""

    return AuditLog.objects.create(
        actor=get_current_user(),
        action=action,
        content_type=ContentType.objects.get_for_model(model),
        object_id=object_id,
        object_repr=object_repr,
        changes=changes,
        message=message,
        path=get_current_path(),
        ip_address=get_current_ip_address(),
    )


def create_instance_audit_log(
    *,
    instance: models.Model,
    action: str,
    changes: dict[str, Any],
    message: str = "",
) -> AuditLog:
    return create_audit_log(
        model=instance.__class__,
        object_id=str(instance.pk),
        object_repr=str(instance),
        action=action,
        changes=changes,
        message=message,
    )
