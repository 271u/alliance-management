import json
from typing import Any

from django.db.models.signals import pre_save, post_save, pre_delete
from django.dispatch import receiver

from core.audit import create_instance_audit_log
from core.models.db.auditlog import AuditLog
from core.models.db.player import Player


AUDITED_MODELS = {
    Player,
}


IGNORED_FIELDS = {
    "id",
    "created_at",
    "updated_at",
}


def make_json_safe(value: Any):
    try:
        json.dumps(value)
        return value
    except TypeError:
        return str(value)


def snapshot_instance(instance) -> dict:
    data = {}

    for field in instance._meta.fields:
        if field.name in IGNORED_FIELDS:
            continue

        value = getattr(instance, field.name)
        data[field.name] = make_json_safe(value)

    return data


def format_field_name(field_name: str) -> str:
    return field_name.replace("_", " ")


def format_changed_fields(changes: dict) -> str:
    return ", ".join(format_field_name(field_name) for field_name in changes.keys())


@receiver(pre_save)
def audit_pre_save(sender, instance, **kwargs):
    if sender not in AUDITED_MODELS:
        return

    if instance.pk is None:
        instance._audit_old_snapshot = None
        return

    try:
        old_instance = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        instance._audit_old_snapshot = None
        return

    instance._audit_old_snapshot = snapshot_instance(old_instance)


@receiver(post_save)
def audit_post_save(sender, instance, created, **kwargs):
    if sender not in AUDITED_MODELS:
        return

    new_snapshot = snapshot_instance(instance)

    if created:
        changes = {
            field: {
                "old": None,
                "new": value,
            }
            for field, value in new_snapshot.items()
        }

        create_instance_audit_log(
            instance=instance,
            action=AuditLog.Action.CREATED,
            changes=changes,
            message=f"Created player {instance}.",
        )
        return

    old_snapshot = getattr(instance, "_audit_old_snapshot", None)

    if old_snapshot is None:
        return

    changes = {}

    for field, old_value in old_snapshot.items():
        new_value = new_snapshot.get(field)

        if old_value != new_value:
            changes[field] = {
                "old": old_value,
                "new": new_value,
            }

    if not changes:
        return

    create_instance_audit_log(
        instance=instance,
        action=AuditLog.Action.UPDATED,
        changes=changes,
        message=f"Updated player {instance}: {format_changed_fields(changes)}.",
    )


@receiver(pre_delete)
def audit_pre_delete(sender, instance, **kwargs):
    if sender not in AUDITED_MODELS:
        return

    changes = {
        field: {
            "old": value,
            "new": None,
        }
        for field, value in snapshot_instance(instance).items()
    }

    create_instance_audit_log(
        instance=instance,
        action=AuditLog.Action.DELETED,
        changes=changes,
        message=f"Deleted player {instance}.",
    )
