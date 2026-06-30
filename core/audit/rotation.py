from .helpers import create_audit_log
from core.models.db.auditlog import AuditLog
from core.models.db.rotation import TrainRotationEntry

ROTATION_OBJECT_ID = "train-conductor-rotation"
ROTATION_OBJECT_REPR = "Train conductor rotation"


def rotation_order_snapshot(entries: list[TrainRotationEntry]) -> list[str]:
    return [entry.player.ingame_name for entry in sorted(entries, key=lambda entry: entry.position)]


def create_rotation_audit_log(
    *,
    action: str,
    message: str,
    old_order: list[str],
    new_order: list[str],
    extra_changes: dict | None = None,
) -> AuditLog:
    changes = {
        "rotation_order": {
            "old": old_order,
            "new": new_order,
        },
    }

    if extra_changes:
        changes.update(extra_changes)

    return create_audit_log(
        model=TrainRotationEntry,
        object_id=ROTATION_OBJECT_ID,
        object_repr=ROTATION_OBJECT_REPR,
        action=action,
        changes=changes,
        message=message,
    )
